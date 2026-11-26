# Use Bell for one organization

This guide uses a synthetic notification export. Bell imports locally into SQLite and writes a JSON feed. It makes no network calls and does not mark provider messages as read.

## 1. Prepare a separate archive

Use Python 3.11 or later. From a clean Bell clone, run in PowerShell:

```powershell
$archive = Join-Path ([System.IO.Path]::GetTempPath()) ('govapi-bell-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $archive | Out-Null
$db = Join-Path $archive 'demo.sqlite'
$feed = Join-Path $archive 'feed.json'
```

Use one database per country, organization, and environment. The sample uses `ru`, `ORG-DEMO`, and `demo`. Keep actual organization exports and working databases outside Git.

## 2. Import an authorized export

Run from the Bell directory:

```powershell
python .\bell.py --db $db --input .\demo.ru.json --output $feed
python .\bell.py --db $db --input .\demo.ru.json --output $feed
$result = Get-Content $feed -Raw | ConvertFrom-Json
$result | Select-Object country, organization, environment
$result.items | Select-Object id, subject, received_at
```

Expect `Bell: added 2, total 2` on the first run and `Bell: added 0, total 2` on the second. The export should contain `demo-1` and `demo-2`. Bell keeps the first record for an ID in this archive. A later export with the same ID does not update the stored record. A snapshot from another country, organization, or environment is rejected.

For data from an authorized provider, map a stable source message ID to `id`, the source subject to `subject`, and the source timestamp with timezone to `received_at`. Preserve provider provenance in your import records. Use the [version 1 format](README.md#feed-contract). Keep a structured case status separately. A provider may issue a message without changing the status of a case.

## 3. Verify the feed in Core

With Core cloned next to Bell, switch to Core in the same PowerShell window so `$feed` remains available:

```powershell
Set-Location ..\govapi-core
python .\serve.py --plugin .\plugins\ru.json --feed $feed
```

Open <http://127.0.0.1:8765>, select **Russia**, and check that both messages appear under **Notifications**. Core accepts synthetic feeds with `environment: "demo"`. For a production-like archive, consume the local export in a separately authorized workflow. Do not label real data as synthetic to load it into the demo.

## 4. Confirm the source before automating retrieval

For a future official adapter, obtain the operator's permission for this organization and role. Check whether the provider distinguishes listing metadata, downloading a message, and acknowledging receipt. Confirm the effect of each action and use the approved TEST environment before implementing any network collection. Bell's local import has no effect on the source mailbox.

**Acceptance:** one clean archive, two stable message IDs, zero new records on repeat, and a feed visible only in the matching Core demo. An archive-context error means you should select the correct database or create an isolated one.
