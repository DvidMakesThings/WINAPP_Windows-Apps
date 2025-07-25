"""Configuration constants for USB Storage Tester"""

import os
from pathlib import Path

# Version info
VERSION = "2.0.0"
TITLE = "USB STORAGE TESTER"

# Test parameters
DEFAULT_BLOCK_SIZE_MB = 100
SPEED_TEST_BLOCK_SIZE_MB = 10
SPEED_TEST_ITERATIONS = 5
MAX_CONCURRENT_OPERATIONS = 4

# File management
DELETE_TEMP_FILES = False  # Set to True to auto-delete temp files after tests
FORMAT_AFTER_TEST = True   # Set to True to offer drive formatting after destructive tests

# Directory paths
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "usb_test_logs"
REPORTS_DIR = BASE_DIR / "test_reports"
TEMP_DIR = BASE_DIR / "temp_test_files"

# Ensure directories exist
for directory in [LOGS_DIR, REPORTS_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# Test patterns
TEST_PATTERNS = {
    'zeros': b'\x00',
    'ones': b'\xFF',
    'alternating': b'\xAA',
    'random': None,  # Generated dynamically
    'incremental': None  # Generated dynamically
}