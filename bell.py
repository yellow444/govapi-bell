"""Import an authorized JSON snapshot into an isolated local Bell archive."""
import argparse
from contextlib import closing
from datetime import datetime
import json
from pathlib import Path
import re
import sqlite3
from tempfile import NamedTemporaryFile


def read_snapshot(path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    try:
        country, organization, environment = (data[key] for key in ("country", "organization", "environment"))
        if (type(data["schema"]) is not int or data["schema"] != 1 or
                not re.fullmatch(r"[a-z]{2}", country) or
                not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", organization) or
                environment not in ("demo", "test", "prod") or not isinstance(data["items"], list)):
            raise ValueError("Invalid snapshot context.")
        for item in data["items"]:
            if any(not isinstance(item[key], str) or not item[key].strip()
                   for key in ("id", "subject", "received_at")):
                raise ValueError("Each item requires id, subject and received_at.")
            if datetime.fromisoformat(item["received_at"]).tzinfo is None:
                raise ValueError("received_at requires a time zone.")
    except (KeyError, TypeError) as error:
        raise ValueError("Invalid snapshot document.") from error
    return data


def ingest(db, snapshot):
    scope = tuple(snapshot[key] for key in ("country", "organization", "environment"))
    items = [(item["id"], item["subject"], item["received_at"]) for item in snapshot["items"]]
    with closing(sqlite3.connect(db, isolation_level=None)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("CREATE TABLE IF NOT EXISTS context (id INTEGER PRIMARY KEY CHECK(id = 1), country, organization, environment)")
        connection.execute("CREATE TABLE IF NOT EXISTS messages (id TEXT PRIMARY KEY, subject TEXT NOT NULL, received_at TEXT NOT NULL)")
        connection.execute("INSERT OR IGNORE INTO context VALUES (1, ?, ?, ?)", scope)
        stored = connection.execute("SELECT country, organization, environment FROM context").fetchone()
        if tuple(stored) != scope:
            raise ValueError("The archive belongs to a different country, organization or environment.")
        count_before = connection.total_changes
        connection.executemany("INSERT OR IGNORE INTO messages VALUES (?, ?, ?)", items)
        added = connection.total_changes - count_before
        rows = [dict(row) for row in connection.execute("SELECT * FROM messages ORDER BY received_at DESC, id")]
        connection.commit()
    return added, {
        "schema": 1, "country": scope[0], "organization": scope[1],
        "environment": scope[2], "items": rows,
    }


def export(output, snapshot):
    with NamedTemporaryFile(dir=output.parent, mode="w", encoding="utf-8", delete=False) as temporary:
        path = Path(temporary.name)
        json.dump(snapshot, temporary, ensure_ascii=False, indent=2)
    try:
        path.replace(output)
    finally:
        path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if len({args.db.resolve(), args.input.resolve(), args.output.resolve()}) != 3:
        parser.error("Database, source and export must have different paths.")
    try:
        added, snapshot = ingest(args.db, read_snapshot(args.input))
        export(args.output, snapshot)
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.exit(1, f"Bell: {error}\n")
    print(f"Bell: added {added}, total {len(snapshot['items'])}")


if __name__ == "__main__":
    main()
