#!/usr/bin/env python3
"""
Sortify — CLI file organizer using the Python standard library only.
Moves files in a target directory into category subfolders.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# Extension (lowercase, with dot) -> category folder name
EXTENSION_CATEGORIES: dict[str, str] = {
    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".webp": "Images",
    ".svg": "Images",
    ".ico": "Images",
    ".tiff": "Images",
    ".tif": "Images",
    ".heic": "Images",
    # Documents
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".rtf": "Documents",
    ".odt": "Documents",
    ".xls": "Documents",
    ".xlsx": "Documents",
    ".csv": "Documents",
    ".ppt": "Documents",
    ".pptx": "Documents",
    ".md": "Documents",
    ".pages": "Documents",
    # Videos
    ".mp4": "Videos",
    ".avi": "Videos",
    ".mkv": "Videos",
    ".mov": "Videos",
    ".wmv": "Videos",
    ".flv": "Videos",
    ".webm": "Videos",
    ".m4v": "Videos",
    ".mpeg": "Videos",
    ".mpg": "Videos",
    # Audio
    ".mp3": "Audio",
    ".wav": "Audio",
    ".flac": "Audio",
    ".aac": "Audio",
    ".ogg": "Audio",
    ".m4a": "Audio",
    ".wma": "Audio",
    # Code & data
    ".py": "Code",
    ".js": "Code",
    ".ts": "Code",
    ".tsx": "Code",
    ".jsx": "Code",
    ".html": "Code",
    ".htm": "Code",
    ".css": "Code",
    ".java": "Code",
    ".c": "Code",
    ".cpp": "Code",
    ".h": "Code",
    ".hpp": "Code",
    ".go": "Code",
    ".rs": "Code",
    ".rb": "Code",
    ".php": "Code",
    ".swift": "Code",
    ".kt": "Code",
    ".sql": "Code",
    ".sh": "Code",
    ".json": "Code",
    ".xml": "Code",
    ".yaml": "Code",
    ".yml": "Code",
    ".toml": "Code",
    ".ini": "Code",
    ".env": "Code",
    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    ".bz2": "Archives",
    ".xz": "Archives",
    ".tgz": "Archives",
}

LOG_FILENAME = "sortify.log"


def validate_target_directory(raw: Path, logger: logging.Logger | None) -> Path:
    """Ensure target exists and is a directory; print errors (and log when logger is set)."""
    path = raw.expanduser()
    if not path.exists():
        msg = f"Path does not exist: {path}"
        if logger:
            logger.error(msg)
        print(f"Error: {msg}", file=sys.stderr)
        raise SystemExit(2)
    if not path.is_dir():
        msg = f"Not a directory: {path}"
        if logger:
            logger.error(msg)
        print(f"Error: {msg}", file=sys.stderr)
        raise SystemExit(2)
    resolved = path.resolve()
    if logger:
        logger.debug("Target directory: %s", resolved)
    return resolved


def category_for(path: Path) -> str:
    ext = path.suffix.lower()
    return EXTENSION_CATEGORIES.get(ext, "Others")


def unique_destination(dest: Path) -> Path:
    """Pick a path that does not exist yet (never overwrites)."""
    if not dest.exists():
        return dest
    stem, suffix, parent = dest.stem, dest.suffix, dest.parent
    n = 1
    while True:
        candidate = parent / f"{stem}_{n}{suffix}"
        if not candidate.exists():
            return candidate
        n += 1


def setup_logging(log_path: Path, dry_run: bool) -> logging.Logger:
    logger = logging.getLogger("sortify")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    logger.info(
        "Run started (dry_run=%s, utc=%s)",
        dry_run,
        datetime.now(timezone.utc).isoformat(),
    )
    return logger


def collect_files_to_sort(target: Path) -> list[Path]:
    """Only regular files directly under target; skip category dirs and the log file."""
    out: list[Path] = []
    for entry in sorted(target.iterdir(), key=lambda p: p.name.lower()):
        if not entry.is_file():
            continue
        if entry.name == LOG_FILENAME:
            continue
        if entry.name == Path(__file__).name:
            continue
        # Already inside a known category folder as direct child — still at target root, so name is filename only
        out.append(entry)
    return out


def run_sort(target: Path, dry_run: bool, logger: logging.Logger) -> tuple[int, int]:
    """
    Returns (moved_count, skipped_count).
    Skipped = errors or same-path (no-op).
    Caller must pass a resolved directory from validate_target_directory.
    """
    moved = 0
    skipped = 0

    for src in collect_files_to_sort(target):
        category = category_for(src)
        dest_dir = target / category
        dest = dest_dir / src.name

        if src.resolve() == dest.resolve():
            logger.info("SKIP (already in place): %s", src.name)
            skipped += 1
            continue

        dest = unique_destination(dest)

        if dry_run:
            try:
                dest_disp = dest.relative_to(target)
            except ValueError:
                dest_disp = dest
            logger.info("DRY-RUN: would move %s -> %s", src, dest_disp)
            moved += 1
            continue

        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            logger.info("MOVED: %s -> %s", src.name, dest.relative_to(target))
            moved += 1
        except OSError as e:
            logger.error("FAILED: %s — %s", src, e)
            skipped += 1

    logger.info(
        "Run finished: moved_or_previewed=%d, skipped_or_failed=%d, dry_run=%s",
        moved,
        skipped,
        dry_run,
    )
    return moved, skipped


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Sort files in a directory into Images, Documents, Videos, Audio, Code, Archives, and Others.",
    )
    p.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Folder to organize (default: current directory)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview only: log planned moves; do not create folders or move files",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    raw_target = Path(args.directory)

    target = validate_target_directory(raw_target, logger=None)

    log_path = Path.cwd() / LOG_FILENAME
    logger = setup_logging(log_path, args.dry_run)

    try:
        moved, skipped = run_sort(target, args.dry_run, logger)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(
            f"Dry-run complete: {moved} file(s) would move, {skipped} skipped.\n"
            "Nothing was changed on disk. Run the same command without --dry-run to sort files."
        )
    else:
        print(f"Done: {moved} file(s) moved, {skipped} skipped.")
    print(f"Log: {log_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
