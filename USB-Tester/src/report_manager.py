"""Report management for USB Storage Tester"""

import os
import json
import csv
from pathlib import Path
from datetime import datetime
from .logger import Logger
from .config import LOGS_DIR, REPORTS_DIR

class ReportManager:
    """Report generation and management"""
    
    def __init__(self, logger=None):
        self.logger = logger or Logger()
    
    def view_test_logs(self):
        """View available test logs"""
        self.logger.info("Viewing test logs...")
        
        log_files = list(LOGS_DIR.glob("*.log"))
        
        if not log_files:
            self.logger.warning("No test logs found")
            return
        
        print(f"\n{'='*60}")
        print(f"{'AVAILABLE TEST LOGS':^60}")
        print(f"{'='*60}")
        
        for i, log_file in enumerate(log_files, 1):
            stat = log_file.stat()
            modified = datetime.fromtimestamp(stat.st_mtime)
            size_kb = stat.st_size / 1024
            
            print(f"{i}. {log_file.name}")
            print(f"   Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Size: {size_kb:.1f} KB")
            print()
        
        try:
            choice = int(input(f"Enter log number to view (1-{len(log_files)}), or 0 to return: "))
            if 1 <= choice <= len(log_files):
                self._display_log_file(log_files[choice - 1])
        except ValueError:
            self.logger.error("Invalid input")
    
    def view_test_reports(self):
        """View available test reports"""
        self.logger.info("Viewing test reports...")
        
        report_files = list(REPORTS_DIR.glob("*.json")) + list(REPORTS_DIR.glob("*.txt"))
        
        if not report_files:
            self.logger.warning("No test reports found")
            return
        
        print(f"\n{'='*60}")
        print(f"{'AVAILABLE TEST REPORTS':^60}")
        print(f"{'='*60}")
        
        for i, report_file in enumerate(report_files, 1):
            stat = report_file.stat()
            modified = datetime.fromtimestamp(stat.st_mtime)
            size_kb = stat.st_size / 1024
            
            print(f"{i}. {report_file.name}")
            print(f"   Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Size: {size_kb:.1f} KB")
            print()
        
        try:
            choice = int(input(f"Enter report number to view (1-{len(report_files)}), or 0 to return: "))
            if 1 <= choice <= len(report_files):
                self._display_report_file(report_files[choice - 1])
        except ValueError:
            self.logger.error("Invalid input")
    
    def _display_log_file(self, log_file):
        """Display contents of a log file"""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"\n{'='*60}")
            print(f"LOG FILE: {log_file.name}")
            print(f"{'='*60}")
            print(content)
            print(f"{'='*60}")
            
        except Exception as e:
            self.logger.error(f"Error reading log file: {e}")
    
    def _display_report_file(self, report_file):
        """Display contents of a report file"""
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"\n{'='*60}")
            print(f"REPORT FILE: {report_file.name}")
            print(f"{'='*60}")
            
            if report_file.suffix == '.json':
                # Pretty print JSON
                try:
                    data = json.loads(content)
                    print(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    print(content)
            else:
                print(content)
            
            print(f"{'='*60}")
            
        except Exception as e:
            self.logger.error(f"Error reading report file: {e}")
    
    def generate_comprehensive_report(self, test_results):
        """Generate comprehensive test report in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        drive_name = test_results['drive_info']['label'].replace(' ', '_')
        
        # Generate JSON report
        json_file = REPORTS_DIR / f"test_report_{drive_name}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, default=str)
        
        # Generate text report
        txt_file = REPORTS_DIR / f"test_report_{drive_name}_{timestamp}.txt"
        self._generate_text_report(test_results, txt_file)
        
        # Generate CSV summary
        csv_file = REPORTS_DIR / f"test_summary_{drive_name}_{timestamp}.csv"
        self._generate_csv_report(test_results, csv_file)
        
        self.logger.success(f"Reports generated:")
        self.logger.success(f"  JSON: {json_file.name}")
        self.logger.success(f"  Text: {txt_file.name}")
        self.logger.success(f"  CSV:  {csv_file.name}")
        
        return json_file
    
    def _generate_text_report(self, test_results, output_file):
        """Generate human-readable text report"""
        drive_info = test_results['drive_info']
        tests = test_results['tests']
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("="*80 + "\n")
            f.write("USB STORAGE TESTER - COMPREHENSIVE REPORT\n")
            f.write("="*80 + "\n\n")
            
            # Test Information
            f.write("TEST INFORMATION\n")
            f.write("-"*40 + "\n")
            f.write(f"Test Type: {test_results['test_type']}\n")
            f.write(f"Timestamp: {test_results['timestamp']}\n")
            f.write(f"Drive: {drive_info['label']}\n")
            f.write(f"Path: {drive_info['path']}\n")
            f.write(f"Size: {drive_info['size'] / (1024**3):.2f} GB\n")
            f.write(f"Model: {drive_info['model']}\n")
            f.write(f"Serial: {drive_info['serial']}\n\n")
            
            # Speed Test Results
            if 'speed_test' in tests and tests['speed_test']:
                speed = tests['speed_test']
                f.write("SPEED TEST RESULTS\n")
                f.write("-"*40 + "\n")
                f.write(f"Sequential Write: {speed['sequential_write_avg']:.2f} MB/s\n")
                f.write(f"Sequential Read:  {speed['sequential_read_avg']:.2f} MB/s\n")
                f.write(f"Random Write:     {speed['random_write_avg']:.2f} MB/s\n")
                f.write(f"Random Read:      {speed['random_read_avg']:.2f} MB/s\n")
                f.write(f"Access Time:      {speed['access_time_avg']:.2f} ms\n\n")
            
            # Data Integrity Results
            if 'integrity_test' in tests and tests['integrity_test']:
                integrity = tests['integrity_test']
                f.write("DATA INTEGRITY TEST RESULTS\n")
                f.write("-"*40 + "\n")
                f.write(f"Patterns Tested:      {integrity['patterns_tested']}\n")
                f.write(f"Files Created:        {integrity['files_created']}\n")
                f.write(f"Verification Passed:  {integrity['verification_passed']}\n")
                f.write(f"Verification Failed:  {integrity['verification_failed']}\n")
                if integrity['errors']:
                    f.write("Errors:\n")
                    for error in integrity['errors']:
                        f.write(f"  - {error}\n")
                f.write("\n")
            
            # Capacity Test Results
            if 'capacity_test' in tests and tests['capacity_test']:
                capacity = tests['capacity_test']
                f.write("CAPACITY TEST RESULTS\n")
                f.write("-"*40 + "\n")
                f.write(f"Size Tested:      {capacity['total_size_tested'] / (1024*1024):.1f} MB\n")
                f.write(f"Blocks Written:   {capacity['blocks_written']}\n")
                f.write(f"Blocks Verified:  {capacity['blocks_verified']}\n")
                f.write(f"Write Speed:      {capacity['write_speed']:.2f} MB/s\n")
                f.write(f"Verify Speed:     {capacity['verify_speed']:.2f} MB/s\n")
                if capacity['errors']:
                    f.write(f"Errors: {len(capacity['errors'])}\n")
                f.write("\n")
            
            # Summary
            f.write("TEST SUMMARY\n")
            f.write("-"*40 + "\n")
            
            overall_status = "PASS"
            issues = []
            
            if 'integrity_test' in tests and tests['integrity_test']:
                if tests['integrity_test']['verification_failed'] > 0:
                    overall_status = "FAIL"
                    issues.append("Data integrity failures detected")
            
            if 'capacity_test' in tests and tests['capacity_test']:
                if tests['capacity_test']['errors']:
                    overall_status = "FAIL"
                    issues.append("Capacity test errors detected")
            
            f.write(f"Overall Status: {overall_status}\n")
            if issues:
                f.write("Issues Found:\n")
                for issue in issues:
                    f.write(f"  - {issue}\n")
            else:
                f.write("No issues detected\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("End of Report\n")
    
    def _generate_csv_report(self, test_results, output_file):
        """Generate CSV summary report"""
        drive_info = test_results['drive_info']
        tests = test_results['tests']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Drive', 'Path', 'Size_GB', 'Test_Type', 'Timestamp',
                'Seq_Write_MBs', 'Seq_Read_MBs', 'Random_Write_MBs', 'Random_Read_MBs', 'Access_Time_ms',
                'Integrity_Patterns', 'Integrity_Files', 'Integrity_Passed', 'Integrity_Failed',
                'Capacity_Size_MB', 'Capacity_Write_MBs', 'Capacity_Verify_MBs',
                'Overall_Status'
            ])
            
            # Data row
            row = [
                drive_info['label'],
                drive_info['path'],
                f"{drive_info['size'] / (1024**3):.2f}",
                test_results['test_type'],
                test_results['timestamp']
            ]
            
            # Speed test data
            if 'speed_test' in tests and tests['speed_test']:
                speed = tests['speed_test']
                row.extend([
                    f"{speed['sequential_write_avg']:.2f}",
                    f"{speed['sequential_read_avg']:.2f}",
                    f"{speed['random_write_avg']:.2f}",
                    f"{speed['random_read_avg']:.2f}",
                    f"{speed['access_time_avg']:.2f}"
                ])
            else:
                row.extend(['', '', '', '', ''])
            
            # Integrity test data
            if 'integrity_test' in tests and tests['integrity_test']:
                integrity = tests['integrity_test']
                row.extend([
                    integrity['patterns_tested'],
                    integrity['files_created'],
                    integrity['verification_passed'],
                    integrity['verification_failed']
                ])
            else:
                row.extend(['', '', '', ''])
            
            # Capacity test data
            if 'capacity_test' in tests and tests['capacity_test']:
                capacity = tests['capacity_test']
                row.extend([
                    f"{capacity['total_size_tested'] / (1024*1024):.1f}",
                    f"{capacity['write_speed']:.2f}",
                    f"{capacity['verify_speed']:.2f}"
                ])
            else:
                row.extend(['', '', ''])
            
            # Overall status
            overall_status = "PASS"
            if 'integrity_test' in tests and tests['integrity_test']:
                if tests['integrity_test']['verification_failed'] > 0:
                    overall_status = "FAIL"
            if 'capacity_test' in tests and tests['capacity_test']:
                if tests['capacity_test']['errors']:
                    overall_status = "FAIL"
            
            row.append(overall_status)
            
            writer.writerow(row)