# GovAPI Bell

GovAPI Bell is the free local importer for structured notification exports. It accepts JSON, stores the first message for each ID in SQLite, and exports a feed. Each database belongs to one country, organization, and environment.

```powershell
python .\bell.py --db demo.sqlite --input demo.ru.json --output feed.json
```

The synthetic `demo.ru.json` file shows the input format. You can rerun the same import. Pass the demo export to GovAPI Core with `--feed`. Reading an external portal requires a separate authorized adapter. This repository handles local import and export.

The project follows the approach of [EPGU Bell](https://github.com/yellow444/epgu-bell). EPGU Bell releases remain in their original repository.
