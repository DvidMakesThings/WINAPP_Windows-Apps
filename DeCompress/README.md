# DeCompress - Auto-Extract Archives on Folder Change

This Python script monitors a specified folder on Windows for new compressed files. Whenever a new archive is detected, it automatically extracts the archive into a subfolder named after the archive, and then deletes the original archive.

It supports multiple archive types, including zip, rar, 7z, tar, tar.gz, tar.bz2, and tar.xz. For rar files, you need unrar or rar installed on your system. For 7z files, the py7zr library is used.

## Features

- Monitors a folder in real time using the `watchdog` library.
- Automatically extracts multiple archive types (zip, rar, 7z, tar variants).
- Deletes the original archive after successful extraction.
- Can be configured to run at system startup via Task Scheduler, Startup folder, or Registry.

## Requirements

- Python 3.7 or later
- pip
- For .rar extraction, unrar or rar executable must be installed and on the system PATH
- `watchdog` library
- `rarfile` library
- `py7zr` library (for .7z)

## Installation

1. Download or clone this repository.
2. Install the required Python libraries by running `pip install -r requirements.txt` (or install each manually).
3. Make sure unrar is accessible on your system PATH if you want to handle .rar files.
4. Edit the Python script to set the folder you want to monitor.
5. Run the script manually using `python DeCompress.py` to verify it works.

## Usage

### Manual Launch

Run the script with `python DeCompress.py`. It will begin monitoring the specified folder and show a tray icon. Leave it running to continue monitoring.

### Automated Launch on Startup

#### Option 1: Task Scheduler

1. Open Task Scheduler, create a new task, set the trigger to `At startup` or `At log on`, and point the action to `python.exe` with the script path as an argument.

#### Option 2: Startup Folder

1. Press `Win + R`, type `shell:startup`, and create a shortcut to `DeCompress.exe`.

#### Option 3: Registry (Run Key)

1. Press `Win + R`, type `regedit`, navigate to `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`, and create a new string entry with the path to your Python script.

## Notes

- If you only need to handle certain archive formats, you can remove unused libraries (`rarfile`, `py7zr`, etc).
- If you want to monitor subfolders, set `recursive=True` in the `observer.schedule` line.
- Add logging or more robust error handling as needed.
- For tar-based archives, Python's `tarfile` module handles most common variants.

## License

This project is licensed under the GPL3 License. See the LICENSE file for details.

## Contact

For questions or feedback, email s.dvid@hotmail.com or visit [GitHub](https://github.com/DvidMakesThings).