# Sortify

A small **Python CLI** that organizes loose files in a folder into category subfolders. Built with the **standard library only** (no `pip install`), so it runs anywhere Python 3 is available.

Good fit for portfolios that emphasize **Python fundamentals**, **scripting**, **filesystem work**, and **clean CLI design**—without leaning on heavy ML frameworks for this particular tool.

## What it does

- Scans **only the top level** of a target directory (does not recurse into subfolders).
- Moves each file into one of: **Images**, **Documents**, **Videos**, **Audio**, **Code**, **Archives**, or **Others** (by extension).
- **`--dry-run`**: writes planned actions to the log as “would move” and prints a summary — **it does not create folders or move anything**. To actually sort files, run the same command **without** `--dry-run`.
- Appends **`sortify.log`** in the **current working directory** with **timestamped** lines for every action.
- **Never overwrites** an existing file: if the destination name exists, it uses `name_1.ext`, `name_2.ext`, …

Files named `sortify.log` or `sortify.py` in the target folder are **not moved** (so the tool does not relocate itself or its log when you organize the project directory).

## Requirements

- Python **3.8+** (uses `pathlib`, `argparse`, `logging`, `shutil`).

## Usage

```bash
python3 sortify.py                 # organize current directory
python3 sortify.py ~/Downloads     # organize a specific folder
python3 sortify.py ~/Downloads --dry-run
```

## Repo layout

```
sortify/
├── sortify.py
├── README.md
└── sortify.log    # created on first run (from your cwd)
```

## Skills this demonstrates

| Area | How |
|------|-----|
| Python | CLI, `pathlib`, file I/O patterns, type hints |
| Engineering | Idempotent-ish runs, duplicate-safe moves, logging |
| Git-friendly | Single module, no lockfiles, easy to review |

## License

MIT — use freely in your portfolio and interviews.
