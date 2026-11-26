# GovAPI Bell

GovAPI Bell is a local importer for structured notification exports. It stores the first message for each ID in SQLite and exports the archive as JSON. Each archive is bound to one country, organization, and environment.

## Quick start

Use Git and Python 3.11 or later. The demo uses the Python standard library and the synthetic export included in the repository.

```powershell
git clone https://github.com/yellow444/govapi-bell.git
Set-Location govapi-bell
python .\bell.py --db demo.sqlite --input demo.ru.json --output feed.json
python .\bell.py --db demo.sqlite --input demo.ru.json --output feed.json
Get-Content .\feed.json
```

On a fresh archive, the first import prints `Bell: added 2, total 2`. The second prints `Bell: added 0, total 2`. Use a new database path to repeat the demonstration with an empty archive.

To display this export in Core, clone both repositories as siblings and follow [Add the Bell demo feed](https://github.com/yellow444/govapi-core#add-the-bell-demo-feed). The demo feed belongs to the Russia plugin.

The [single-organization guide](SINGLE_ORGANIZATION.md) covers archive isolation, repeat imports, verification in Core, and the checks to complete before connecting a provider.

## Feed contract

A version 1 snapshot contains:

- `schema` as the JSON integer `1`
- `country` as a two-letter lowercase ID such as `ru`
- `organization` as a nonempty ID of up to 64 ASCII letters, digits, underscores, or hyphens, starting with a letter or digit
- `environment` as `demo`, `test`, or `prod`
- `items` as an array of messages with non-blank string `id`, `subject`, and ISO 8601 `received_at` with a timezone

The importer rejects a snapshot whose country, organization, or environment differs from the existing database. It exports the full archive after import. Core accepts only `demo` feeds for matching loaded plugins. Collecting data directly from an external system requires a separate authorized adapter.

The project follows the approach of [EPGU Bell](https://github.com/yellow444/epgu-bell), which has its own releases.
