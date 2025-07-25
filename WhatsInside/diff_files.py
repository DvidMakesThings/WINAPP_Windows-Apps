def read_file_lines(path):
    with open(path, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

def compare_snapshots(before_path, after_path):
    before = read_file_lines(before_path)
    after = read_file_lines(after_path)

    added = after - before
    removed = before - after

    print("🟢 Added:")
    for item in sorted(added):
        print(" +", item)

    print("\n🔴 Removed:")
    for item in sorted(removed):
        print(" -", item)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python diff_files.py baseline.txt post_launch.txt")
    else:
        compare_snapshots(sys.argv[1], sys.argv[2])
