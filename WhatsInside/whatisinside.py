import os
import argparse

def list_contents(parent_folder):
    contents = []
    for root, dirs, files in os.walk(parent_folder):
        for name in dirs:
            contents.append(os.path.join(root, name))
        for name in files:
            contents.append(os.path.join(root, name))
    return contents

def save_to_file(contents, filename, save_location):
    if not save_location:
        save_location = os.getcwd()
    filepath = os.path.join(save_location, filename)
    with open(filepath, 'w') as f:
        for item in contents:
            f.write(f"{item}\n")

def main():
    parser = argparse.ArgumentParser(description="List all subfolders and files in a parent folder.")
    parser.add_argument("parent_folder", help="The parent folder to list contents of.")
    parser.add_argument("--file", help="The filename to save the output to.")
    parser.add_argument("--save", help="The location to save the output file.")
    args = parser.parse_args()

    contents = list_contents(args.parent_folder)

    if args.file:
        save_to_file(contents, args.file, args.save)
    else:
        for item in contents:
            print(item)

if __name__ == "__main__":
    main()