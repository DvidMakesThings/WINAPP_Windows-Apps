"""Main USB Storage Tester class"""

from logging import config
import sys
import time
from datetime import datetime
from .drive_detector import DriveDetector
from .menu import Menu
from .logger import Logger
from .test_runner import TestRunner
from .report_manager import ReportManager

class USBStorageTester:
    """Main USB Storage Tester application"""
    
    def __init__(self):
        # Create main logger with session timestamp
        session_log = f"main_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.logger = Logger(session_log)
        self.drive_detector = DriveDetector(self.logger)
        self.menu = Menu(self.logger)
        self.test_runner = TestRunner(self.logger)
        self.report_manager = ReportManager(self.logger)
        self.drives = []
    
    def run(self):
        """Main application loop"""
        while True:
            try:
                self.menu.show_menu()
                choice = self.menu.get_user_choice(10)
                
                if choice is None:
                    self.logger.error("Invalid input. Please enter a number.")
                    continue
                
                if choice == 1:
                    self._scan_drives()
                elif choice == 2:
                    self._run_speed_test()
                elif choice == 3:
                    self._run_data_integrity_test()
                elif choice == 4:
                    self._run_fast_capacity_verify()
                elif choice == 5:
                    self._run_full_capacity_test()
                elif choice == 6:
                    self._run_comprehensive_test_fast()
                elif choice == 7:
                    self._run_comprehensive_test_detailed()
                elif choice == 8:
                    self._view_test_logs()
                elif choice == 9:
                    self._view_test_reports()
                elif choice == 10:
                    self.logger.info("Exiting USB Storage Tester. Goodbye!")
                    break
                else:
                    self.logger.error("Invalid choice. Please select 1-10.")
                
                if choice != 10:
                    self.menu.pause()
                    
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user.")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                self.menu.pause()
    
    def _scan_drives(self):
        """Scan for USB drives"""
        self.logger.info("Refreshing USB drive list...")
        self.drives = self.drive_detector.scan_usb_drives()
        self.drive_detector.display_drives()
    
    def _ensure_drives_scanned(self):
        """Ensure drives are scanned, scan if not"""
        # Always rescan drives to handle USB replug scenarios
        self.logger.info("Scanning for current USB drives...")
        self.drives = self.drive_detector.scan_usb_drives()
        
        if not self.drives:
            self.logger.warning("No USB drives detected. Please connect a USB drive and try again.")
            return False
        return True
    
    def _select_drive(self):
        """Select a drive for testing"""
        if not self._ensure_drives_scanned():
            return None
        return self.menu.show_drive_selection_menu(self.drives)
    
    def _run_speed_test(self):
        """Run speed test only"""
        drive = self._select_drive()
        if drive:
            self.test_runner.run_speed_test(drive)
    
    def _run_data_integrity_test(self):
        """Run data integrity test only"""
        drive = self._select_drive()
        if drive:
            if self.menu.confirm_destructive_test(drive, "data integrity test"):
                result = self.test_runner.run_data_integrity_test(drive)
                if result and not self.test_runner.stop_requested:
                    self.test_runner._format_drive_after_test(drive)
            else:
                self.logger.warning("Test cancelled - confirmation not received")
    
    def _run_fast_capacity_verify(self):
        """Run fast capacity verify only"""
        drive = self._select_drive()
        if drive:
            if self.menu.confirm_destructive_test(drive, "fast capacity verify"):
                result = self.test_runner.run_fast_capacity_verify(drive)
                if result and not self.test_runner.stop_requested:
                    self.test_runner._format_drive_after_test(drive)
            else:
                self.logger.warning("Test cancelled - confirmation not received")
    
    def _run_full_capacity_test(self):
        """Run full capacity test only"""
        drive = self._select_drive()
        if drive:
            if self.menu.confirm_destructive_test(drive, "full capacity verify"):
                result = self.test_runner.run_full_capacity_test(drive)
                if result and not self.test_runner.stop_requested:
                    self.test_runner._format_drive_after_test(drive)
            else:
                self.logger.warning("Test cancelled - confirmation not received")
    
    def _run_comprehensive_test_fast(self):
        """Run comprehensive test (fast)"""
        if not self._ensure_drives_scanned():
            return
        
        drive = self.menu.show_drive_selection_menu(self.drives)
        if drive:
            if self.menu.confirm_destructive_test(drive, "comprehensive test (fast)"):
                self.test_runner.run_comprehensive_test_fast(drive)
            else:
                self.logger.warning("Test cancelled - confirmation not received")
    
    def _run_comprehensive_test_detailed(self):
        """Run comprehensive test (detailed)"""
        if not self._ensure_drives_scanned():
            return
        
        drive = self.menu.show_drive_selection_menu(self.drives)
        if drive:
            if self.menu.confirm_destructive_test(drive, "comprehensive test (detailed)"):
                self.test_runner.run_comprehensive_test_detailed(drive)
            else:
                self.logger.warning("Test cancelled - confirmation not received")
    
    def _view_test_logs(self):
        """View test logs"""
        self.report_manager.view_test_logs()
    
    def _view_test_reports(self):
        """View test reports"""
        self.report_manager.view_test_reports()
    
    def _toggle_temp_file_cleanup(self):
        """Toggle temp file cleanup setting"""
        config.DELETE_TEMP_FILES = not config.DELETE_TEMP_FILES
        status = "enabled" if config.DELETE_TEMP_FILES else "disabled"
        self.logger.success(f"Temp file cleanup {status}")
        
        if config.DELETE_TEMP_FILES:
            self.logger.warning("Temp files will be automatically deleted after tests")
        else:
            self.logger.info("Temp files will be preserved for analysis")