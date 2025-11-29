"""General filler for empty PACKAGE attributes in Eagle .lbr files.

For every <attribute name="PACKAGE" value="" constant="no"/> inside a <device>
the script copies the enclosing <device ... package="X"> value into the attribute.

Features:
 - Works on a single file (--file) or all .lbr files in a directory (--dir)
 - Optional recursive directory scan (--recursive)
 - Dry-run mode to preview changes without writing (--dry-run)
 - Backup creation before modifying files (--backup)

Usage examples (PowerShell):
  python fill_package_attrs.py --file .\ds_capacitors.lbr
  python fill_package_attrs.py --dir . --recursive --backup
  python fill_package_attrs.py --dir . --dry-run
"""

from __future__ import annotations
import argparse
import re
from pathlib import Path
from typing import List

DEVICE_RE = re.compile(r'<device\b[^>]*\bpackage="([^\"]+)"')
EMPTY_PKG_ATTR = '<attribute name="PACKAGE" value="" constant="no"/>'

def process_file(path: Path, dry_run: bool = False, backup: bool = False) -> bool:
    try:
        original = path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"[WARN] Cannot read {path}: {e}")
        return False
    lines = original.splitlines()
    current_pkg = None
    changed = False
    for idx, line in enumerate(lines):
        if '<device ' in line:
            m = DEVICE_RE.search(line)
            if m:
                current_pkg = m.group(1)
        if EMPTY_PKG_ATTR in line and current_pkg:
            new_line = line.replace('value=""', f'value="{current_pkg}"')
            if new_line != line:
                lines[idx] = new_line
                changed = True
    if changed and not dry_run:
        if backup:
            try:
                backup_path = path.with_suffix(path.suffix + '.bak')
                backup_path.write_text(original, encoding='utf-8')
            except Exception as e:
                print(f"[WARN] Failed backup for {path}: {e}")
        try:
            path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        except Exception as e:
            print(f"[ERROR] Write failed for {path}: {e}")
            return False
    status = 'CHANGED' if changed else 'UNCHANGED'
    mode = 'DRY-RUN' if dry_run else 'WRITE'
    print(f"[{mode}] {path} -> {status}")
    return changed

def gather_files(single: Path | None, directory: Path | None, recursive: bool) -> List[Path]:
    if single:
        return [single]
    if not directory:
        return []
    pattern = '**/*.lbr' if recursive else '*.lbr'
    return sorted(directory.glob(pattern))

def main():
    ap = argparse.ArgumentParser(description='Fill empty PACKAGE attributes in Eagle libraries.')
    ap.add_argument('--file', type=Path, help='Single .lbr file to process')
    ap.add_argument('--dir', type=Path, help='Directory containing .lbr files to process')
    ap.add_argument('--recursive', action='store_true', help='Recurse into subdirectories')
    ap.add_argument('--dry-run', action='store_true', help='Show intended changes without writing')
    ap.add_argument('--backup', action='store_true', help='Create .bak backup before writing')
    args = ap.parse_args()

    targets = gather_files(args.file, args.dir, args.recursive)
    if not targets:
        print('No target files found. Use --file or --dir.')
        return
    total_changed = 0
    for f in targets:
        if process_file(f, dry_run=args.dry_run, backup=args.backup):
            total_changed += 1
    print(f"Summary: {total_changed} / {len(targets)} files modified.")

if __name__ == '__main__':
    main()
