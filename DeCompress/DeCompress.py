import sys
import os
import time
import gc
import threading
from datetime import datetime

# Standard library modules for various archive types
import zipfile
import tarfile
import shutil

# Third-party libraries for rar and 7z
import rarfile          # pip install rarfile (requires unrar or rar in PATH)
import py7zr            # pip install py7zr

# PyQt5 imports
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction

# Watchdog imports
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
WATCH_FOLDER = r"C:\Users\DSP\Downloads"  # Change this path as needed
GC_INTERVAL = 3600   # Force garbage collection every 1 hour
FILE_ACCESS_ATTEMPTS = 5
FILE_ACCESS_DELAY_SEC = 1

# List of recognized archive formats. The first item is the file extension (or pattern),
# second is the format label we'll use in extraction logic.
ARCHIVE_FORMATS = [
    ('.tar.gz',   'tar.gz'),  ('.tgz',     'tar.gz'),
    ('.tar.bz2',  'tar.bz2'), ('.tbz',     'tar.bz2'),
    ('.tar.xz',   'tar.xz'),  ('.txz',     'tar.xz'),
    ('.tar',      'tar'),
    ('.zip',      'zip'),
    ('.rar',      'rar'),
    ('.7z',       '7z'),
]

# ------------------------------------------------------------------
# Helper: wait_for_file
# ------------------------------------------------------------------
def wait_for_file(file_path, attempts=FILE_ACCESS_ATTEMPTS, delay=FILE_ACCESS_DELAY_SEC):
    """
    Attempt to open the file in read mode up to 'attempts' times,
    waiting 'delay' seconds between each try. This helps if another
    process is still locking the file (e.g., antivirus scan or incomplete download).
    """
    for _ in range(attempts):
        try:
            with open(file_path, 'rb'):
                pass
            return True
        except PermissionError:
            time.sleep(delay)
    return False

# ------------------------------------------------------------------
# Helper: detect_archive_type
# ------------------------------------------------------------------
def detect_archive_type(file_name: str) -> str:
    """
    Returns a string describing the archive format based on the file_name,
    or an empty string if unrecognized.
    We match multi-part extensions first (e.g. .tar.gz).
    """
    name_lower = file_name.lower()
    for pattern, fmt_label in ARCHIVE_FORMATS:
        if name_lower.endswith(pattern):
            return fmt_label
    return ''  # not recognized

# ------------------------------------------------------------------
# Helper: extract_archive
# ------------------------------------------------------------------
def extract_archive(file_path: str, archive_format: str, dest_folder: str):
    """
    Extracts the archive at 'file_path' into 'dest_folder',
    using the appropriate library for each format.
    """
    if archive_format == 'zip':
        with zipfile.ZipFile(file_path, 'r') as zf:
            zf.extractall(dest_folder)

    elif archive_format == 'rar':
        with rarfile.RarFile(file_path) as rf:
            rf.extractall(dest_folder)

    elif archive_format == '7z':
        with py7zr.SevenZipFile(file_path, 'r') as sz:
            sz.extractall(dest_folder)

    elif archive_format.startswith('tar'):  # tar, tar.gz, tar.bz2, tar.xz
        with tarfile.open(file_path, 'r:*') as tf:
            tf.extractall(dest_folder)

    else:
        # Optionally handle any other single-file compressions or fallback
        # e.g. shutil.unpack_archive(file_path, dest_folder)
        pass

# ------------------------------------------------------------------
# Signals object to communicate from Watchdog to the GUI
# ------------------------------------------------------------------
class MonitorSignals(QObject):
    file_extracted = pyqtSignal(str)  # string with info about the file

# ------------------------------------------------------------------
# Watchdog Event Handler
# ------------------------------------------------------------------
class ArchiveHandler(FileSystemEventHandler):
    """
    Handles created files in the watch folder. Checks if it's an archive
    we recognize, then extracts it, deletes the original file,
    and emits a signal about the extraction.
    """
    def __init__(self, signals: MonitorSignals):
        super().__init__()
        self.signals = signals

    def on_created(self, event):
        if event.is_directory:
            return
        self.process_file(event.src_path)

    def process_file(self, file_path):
        file_name = os.path.basename(file_path)
        archive_type = detect_archive_type(file_name)
        if not archive_type:
            return  # Not an archive we handle

        if not wait_for_file(file_path):
            print(f"Could not access file after multiple attempts: {file_path}")
            return

        # Deduce a subfolder name
        file_base = file_name
        # Remove recognized patterns from the end to get a cleaner base name
        # e.g. "myarchive.tar.gz" -> "myarchive"
        for pattern, _ in ARCHIVE_FORMATS:
            plower = pattern.lower()
            if file_base.lower().endswith(plower):
                file_base = file_base[: -len(plower)]
                break  # Remove the first matching pattern, then stop
        else:
            # Or you can do multiple passes if needed
            file_base, _ = os.path.splitext(file_base)

        new_folder = os.path.join(WATCH_FOLDER, file_base)
        os.makedirs(new_folder, exist_ok=True)

        try:
            extract_archive(file_path, archive_type, new_folder)
            os.remove(file_path)
            msg = f"{file_base} ({archive_type.upper()}) extracted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.signals.file_extracted.emit(msg)
        except Exception as e:
            print(f"Error handling {archive_type} file {file_path}: {e}")

# ------------------------------------------------------------------
# Background Thread (Watchdog)
# ------------------------------------------------------------------
class MonitorThread(threading.Thread):
    """
    Runs Watchdog in the background. Does an initial scan, monitors for new files,
    and periodically forces garbage collection.
    """
    def __init__(self, signals: MonitorSignals, folder: str):
        super().__init__()
        self.signals = signals
        self.folder = folder
        self.stop_event = threading.Event()
        self.observer = None
        self.daemon = True

    def run(self):
        event_handler = ArchiveHandler(self.signals)

        # Initial scan
        for entry in os.scandir(self.folder):
            if entry.is_file():
                event_handler.process_file(entry.path)

        self.observer = Observer()
        self.observer.schedule(event_handler, self.folder, recursive=False)
        self.observer.start()
        print(f"Monitoring folder: {self.folder}")

        last_gc_time = time.time()
        while not self.stop_event.is_set():
            time.sleep(1)
            now = time.time()
            if now - last_gc_time >= GC_INTERVAL:
                gc.collect()
                last_gc_time = now
                print("Garbage collection forced to maintain low memory usage.")

        # Stop gracefully
        self.observer.stop()
        self.observer.join()
        print("Monitor thread stopped.")

    def stop(self):
        self.stop_event.set()

# ------------------------------------------------------------------
# The GUI Window
# ------------------------------------------------------------------
class ArchiveWindow(QtWidgets.QWidget):
    """
    A window with:
      - A list of extracted files
      - "Close Window" button (just hides the GUI)
      - "Stop/Restart Application" button controlling the monitor
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DeCompress Monitor")

        # Set a window icon (use your own icon file here)
        app_icon = QtGui.QIcon("G:\_GitHub\Eagle-projects\Scripts\DeCompress\extract-icon.png")  # Make sure myicon.ico is in the same folder
        self.setWindowIcon(app_icon)

        self.resize(343, 562)
        self.listWidget = QtWidgets.QListWidget(self)
        self.listWidget.setGeometry(20, 30, 301, 471)

        self.closeButton = QtWidgets.QPushButton(self)
        self.closeButton.setText("Close Window")
        self.closeButton.setGeometry(182, 520, 131, 29)
        self.closeButton.clicked.connect(self.on_close_clicked)

        self.quitButton = QtWidgets.QPushButton(self)
        self.quitButton.setText("Stop Application")
        self.quitButton.setGeometry(22, 520, 131, 29)
        self.quitButton.clicked.connect(self.on_quit_clicked)

        self.app_running = True

    def on_close_clicked(self):
        self.hide()  # Just hide the window

    def on_quit_clicked(self):
        """
        Toggles between stopping and restarting the monitor thread.
        """
        main_app = QtWidgets.QApplication.instance()

        if self.app_running:
            # Stop
            self.quitButton.setText("Restart Application")
            self.app_running = False
            if hasattr(main_app, 'stop_monitor'):
                main_app.stop_monitor()
        else:
            # Restart
            self.quitButton.setText("Stop Application")
            self.app_running = True
            if hasattr(main_app, 'start_monitor'):
                main_app.start_monitor()

    def add_extracted_file(self, text: str):
        """
        Adds a line to the list widget about the extracted file and timestamp.
        """
        self.listWidget.addItem(text)

    def closeEvent(self, event):
        """
        Override the X button to hide the window instead of quitting.
        """
        self.hide()
        event.ignore()

# ------------------------------------------------------------------
# Main Application Class
# ------------------------------------------------------------------
class DeCompressApp(QtWidgets.QApplication):
    """
    The main PyQt application with:
      - a tray icon
      - a single ArchiveWindow
      - a background MonitorThread
    """
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.signals = MonitorSignals()

        # Create the main window
        self.window = ArchiveWindow()

        # Connect the extracted-file signal
        self.signals.file_extracted.connect(self.window.add_extracted_file)

        # Start the monitor thread
        self.monitor_thread = None
        self.start_monitor()

        # Tray icon
        self.tray_icon = QSystemTrayIcon(self)

        # Load a custom icon for the tray
        tray_app_icon = QtGui.QIcon("G:\_GitHub\Eagle-projects\Scripts\DeCompress\extract-icon.png")  # Same icon as window
        self.tray_icon.setIcon(tray_app_icon)

        # Optional: set a global application icon
        self.setWindowIcon(tray_app_icon)

        # Create tray menu
        tray_menu = QMenu()
        action_show = QAction("Show Window", self)
        action_show.triggered.connect(self.show_window)
        tray_menu.addAction(action_show)

        action_exit = QAction("Exit", self)
        action_exit.triggered.connect(self.exit_app)
        tray_menu.addAction(action_exit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.icon_activated)
        self.tray_icon.show()

    def icon_activated(self, reason):
        """
        Show the main window if the tray icon is clicked or double-clicked.
        """
        if reason == QSystemTrayIcon.Trigger or reason == QSystemTrayIcon.DoubleClick:
            self.show_window()

    def show_window(self):
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def exit_app(self):
        """
        Stop everything and quit the application entirely.
        """
        self.stop_monitor()
        self.quit()

    def stop_monitor(self):
        """
        Stop the monitoring thread if running.
        """
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.stop()

    def start_monitor(self):
        """
        Start the monitoring thread if not already running.
        """
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.monitor_thread = MonitorThread(self.signals, WATCH_FOLDER)
            self.monitor_thread.start()

# ------------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------------
def main():
    app = DeCompressApp(sys.argv)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
