"""General attribute normalizer for <technology name=""> blocks in Eagle .lbr files.

Ensures each blank-named <technology> block contains the required attributes:
  DESCRIPTION, HQ_PART, LCSC_PART, MANUFACTURER, MPN, PACKAGE, ROHS, VALUE

Missing ones are appended (in the listed order) with empty string value, preserving
any existing attributes and indentation style found in the block.

Features:
 - Process a single file (--file) or all .lbr files in a directory (--dir)
 - Optional recursive scan (--recursive)
 - Dry-run mode (--dry-run) reports intended changes
 - Backup creation (--backup)

Usage examples (PowerShell):
  python add_missing_tech_attrs.py --file .\my_lib.lbr
  python add_missing_tech_attrs.py --dir . --recursive --backup
  python add_missing_tech_attrs.py --dir . --dry-run
"""

from __future__ import annotations
import argparse
import re
from pathlib import Path
from typing import List

RE_TECH_OPEN = re.compile(r'^\s*<technology name="">\s*$')
RE_ATTR_NAME = re.compile(r'<attribute name="([A-Z0-9_]+)"')

REQUIRED = ["DESCRIPTION","HQ_PART","LCSC_PART","MANUFACTURER","MPN","PACKAGE","ROHS","VALUE"]

def process_file(path: Path, dry_run: bool = False, backup: bool = False) -> bool:
    try:
        original = path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"[WARN] Cannot read {path}: {e}")
        return False
    lines = original.splitlines()
    out_lines = []
    i = 0
    changed = False
    while i < len(lines):
        line = lines[i]
        if RE_TECH_OPEN.match(line):
            block = [line]
            i += 1
            while i < len(lines) and lines[i].strip() != '</technology>':
                block.append(lines[i])
                i += 1
            if i < len(lines):
                closing = lines[i]
            else:
                closing = '</technology>'
            present = set()
            indent_attr = None
            for bline in block[1:]:
                m = RE_ATTR_NAME.search(bline)
                if m:
                    name = m.group(1)
                    if name in REQUIRED:
                        present.add(name)
                    if indent_attr is None and '<attribute ' in bline:
                        indent_attr = bline.split('<attribute')[0]
            if indent_attr is None:
                indent_attr = ''
            missing = [r for r in REQUIRED if r not in present]
            out_lines.extend(block)
            if missing:
                changed = True
                for mname in missing:
                    out_lines.append(f"{indent_attr}<attribute name=\"{mname}\" value=\"\" constant=\"no\"/>")
            out_lines.append(closing)
            i += 1
        else:
            out_lines.append(line)
            i += 1
    new_text = '\n'.join(out_lines) + '\n'
    if changed and not dry_run:
        if backup:
            try:
                backup_path = path.with_suffix(path.suffix + '.bak')
                backup_path.write_text(original, encoding='utf-8')
            except Exception as e:
                print(f"[WARN] Backup failed for {path}: {e}")
        try:
            path.write_text(new_text, encoding='utf-8')
        except Exception as e:
            print(f"[ERROR] Write failed for {path}: {e}")
            return False
    mode = 'DRY-RUN' if dry_run else 'WRITE'
    print(f"[{mode}] {path} -> {'CHANGED' if changed else 'UNCHANGED'}")
    return changed

def gather_files(single: Path | None, directory: Path | None, recursive: bool) -> List[Path]:
    if single:
        return [single]
    if not directory:
        return []
    pattern = '**/*.lbr' if recursive else '*.lbr'
    return sorted(directory.glob(pattern))

def main():
    ap = argparse.ArgumentParser(description='Add missing technology attributes to Eagle libraries.')
    ap.add_argument('--file', type=Path, help='Single .lbr file to process')
    ap.add_argument('--dir', type=Path, help='Directory containing .lbr files to process')
    ap.add_argument('--recursive', action='store_true', help='Recurse into subdirectories')
    ap.add_argument('--dry-run', action='store_true', help='Preview changes only')
    ap.add_argument('--backup', action='store_true', help='Create .bak backups before writing')
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
