"""Logging utilities for USB Storage Tester"""

import os
import sys
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init

from .config import LOGS_DIR

# Initialize colorama
init(autoreset=True)

class Logger:
    """Enhanced logging with colors and file output"""
    
    def __init__(self, log_file=None):
        self.log_file = log_file
        if log_file:
            self.log_path = LOGS_DIR / log_file
            # Ensure log directory exists
            self.log_path.parent.mkdir(exist_ok=True)
    
    def _write_to_file(self, message):
        """Write message to log file"""
        if self.log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
    
    def info(self, message):
        """Log info message"""
        print(f"{Fore.WHITE}[INFO]{Style.RESET_ALL} {message}")
        self._write_to_file(f"[INFO] {message}")
    
    def success(self, message):
        """Log success message"""
        print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {message}")
        self._write_to_file(f"[SUCCESS] {message}")
    
    def warning(self, message):
        """Log warning message"""
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}")
        self._write_to_file(f"[WARNING] {message}")
    
    def error(self, message):
        """Log error message"""
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}")
        self._write_to_file(f"[ERROR] {message}")
    
    def debug(self, message):
        """Log debug message"""
        print(f"{Fore.MAGENTA}[DEBUG]{Style.RESET_ALL} {message}")
        self._write_to_file(f"[DEBUG] {message}")
    
    def progress(self, message):
        """Log progress message"""
        print(f"{Fore.CYAN}[PROGRESS]{Style.RESET_ALL} {message}")
        self._write_to_file(f"[PROGRESS] {message}")