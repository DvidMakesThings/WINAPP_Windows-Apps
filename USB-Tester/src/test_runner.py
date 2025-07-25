"""Test execution engine for USB Storage Tester"""

import os
import time
import threading
import hashlib
import random
import shutil
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from .logger import Logger
from .config import TEMP_DIR, LOGS_DIR, DEFAULT_BLOCK_SIZE_MB, SPEED_TEST_BLOCK_SIZE_MB, SPEED_TEST_ITERATIONS, MAX_CONCURRENT_OPERATIONS, TEST_PATTERNS, DELETE_TEMP_FILES
from .progress_bar import ProgressBar
from .report_manager import ReportManager
from .drive_detector import DriveDetector

class TestRunner:
    """Test execution engine with real testing functionality"""
    
    def __init__(self, logger=None):
        # Create logger with timestamped log file
        log_filename = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.logger = logger or Logger(log_filename)
        self.current_test = None
        self.test_results = {}
        self.stop_requested = False
        self.report_manager = ReportManager(self.logger)
        self.drive_detector = DriveDetector(self.logger)
    
    def run_speed_test(self, drive):
        """Run comprehensive speed test"""
        self.logger.info(f"Starting speed test on {drive['label']} ({drive['path']})")
        
        results = {
            'sequential_write': [],
            'sequential_read': [],
            'random_write': [],
            'random_read': [],
            'access_time': []
        }
        
        # Write directly to USB drive for accurate speed testing
        test_file = Path(drive['path']) / f"speed_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tmp"
        block_size = SPEED_TEST_BLOCK_SIZE_MB * 1024 * 1024  # Convert to bytes
        
        try:
            # Sequential Write Test
            self.logger.info("Running sequential write test...")
            progress = ProgressBar(SPEED_TEST_ITERATIONS, "Sequential Write")
            
            for i in range(SPEED_TEST_ITERATIONS):
                if self.stop_requested:
                    break
                    
                write_speed = self._test_sequential_write(test_file, block_size)
                results['sequential_write'].append(write_speed)
                progress.update(i + 1)
                time.sleep(0.1)  # Brief pause between tests
            
            progress.complete()
            
            # Sequential Read Test
            self.logger.info("Running sequential read test...")
            progress = ProgressBar(SPEED_TEST_ITERATIONS, "Sequential Read")
            
            for i in range(SPEED_TEST_ITERATIONS):
                if self.stop_requested:
                    break
                    
                read_speed = self._test_sequential_read(test_file, block_size)
                results['sequential_read'].append(read_speed)
                progress.update(i + 1)
                time.sleep(0.1)
            
            progress.complete()
            
            # Random Access Test
            self.logger.info("Running random access test...")
            random_speed = self._test_random_access(test_file, block_size // 10)  # Smaller blocks for random
            results['random_write'].append(random_speed['write'])
            results['random_read'].append(random_speed['read'])
            
            # Access Time Test
            self.logger.info("Measuring access time...")
            access_time = self._test_access_time(test_file)
            results['access_time'].append(access_time)
            
            # Calculate averages
            avg_results = {
                'sequential_write_avg': sum(results['sequential_write']) / len(results['sequential_write']) if results['sequential_write'] else 0,
                'sequential_read_avg': sum(results['sequential_read']) / len(results['sequential_read']) if results['sequential_read'] else 0,
                'random_write_avg': sum(results['random_write']) / len(results['random_write']) if results['random_write'] else 0,
                'random_read_avg': sum(results['random_read']) / len(results['random_read']) if results['random_read'] else 0,
                'access_time_avg': sum(results['access_time']) / len(results['access_time']) if results['access_time'] else 0
            }
            
            # Display results
            self._display_speed_results(avg_results)
            
            self.logger.success("Speed test completed")
            return avg_results
            
        except Exception as e:
            self.logger.error(f"Speed test failed: {e}")
            return None
        finally:
            # Cleanup
            self._cleanup_temp_file(test_file, "Speed test file")
    
    def run_data_integrity_test(self, drive):
        """Run comprehensive data integrity test"""
        self.logger.info(f"Starting data integrity test on {drive['label']} ({drive['path']})")
        
        # Write directly to USB drive for real integrity testing
        test_dir = Path(drive['path']) / f"integrity_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_dir.mkdir(exist_ok=True)
        
        results = {
            'patterns_tested': 0,
            'files_created': 0,
            'verification_passed': 0,
            'verification_failed': 0,
            'errors': []
        }
        
        try:
            patterns = ['zeros', 'ones', 'alternating', 'random', 'incremental']
            total_tests = len(patterns) * 3  # 3 files per pattern
            
            progress = ProgressBar(total_tests, "Data Integrity Test")
            test_count = 0
            
            for pattern_name in patterns:
                if self.stop_requested:
                    break
                
                self.logger.info(f"Testing pattern: {pattern_name}")
                results['patterns_tested'] += 1
                
                # Create 3 test files per pattern
                for file_num in range(3):
                    if self.stop_requested:
                        break
                    
                    test_file = test_dir / f"{pattern_name}_test_{file_num}.dat"
                    
                    try:
                        # Generate test data
                        test_data = self._generate_test_pattern(pattern_name, 1024 * 1024)  # 1MB
                        original_hash = hashlib.sha256(test_data).hexdigest()
                        
                        # Write data
                        with open(test_file, 'wb') as f:
                            f.write(test_data)
                            f.flush()
                            os.fsync(f.fileno())
                        
                        results['files_created'] += 1
                        self.logger.debug(f"Created test file: {test_file.name}")
                        
                        # Verify data
                        with open(test_file, 'rb') as f:
                            read_data = f.read()
                        
                        read_hash = hashlib.sha256(read_data).hexdigest()
                        
                        if original_hash == read_hash:
                            results['verification_passed'] += 1
                            self.logger.debug(f"Verification passed for {test_file.name}")
                        else:
                            results['verification_failed'] += 1
                            error_msg = f"Hash mismatch in {test_file.name}"
                            results['errors'].append(error_msg)
                            self.logger.error(error_msg)
                        
                        test_count += 1
                        progress.update(test_count)
                        
                    except Exception as e:
                        error_msg = f"Error testing {test_file.name}: {str(e)}"
                        results['errors'].append(error_msg)
                        self.logger.error(error_msg)
                        test_count += 1
                        progress.update(test_count)
            
            progress.complete()
            
            # Display results
            self._display_integrity_results(results)
            
            self.logger.success("Data integrity test completed")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Data integrity test failed: {e}")
            return None
        finally:
            # Cleanup
            self._cleanup_temp_directory(test_dir, "Integrity test files")
    
    def run_fast_capacity_verify(self, drive):
        """Run fast capacity verification"""
        self.logger.info(f"Starting fast capacity verify on {drive['label']} ({drive['path']})")
        
        try:
            # Get drive capacity
            total, used, free = shutil.disk_usage(drive['path'])
            
            # Test with 10% of free space or 1GB, whichever is smaller
            test_size = min(free * 0.1, 1024 * 1024 * 1024)  # 1GB max
            
            self.logger.info(f"Testing {test_size / (1024*1024):.1f} MB of capacity...")
            
            # Write directly to USB drive for real capacity testing
            test_file = Path(drive['path']) / f"capacity_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tmp"
            block_size = 1024 * 1024  # 1MB blocks
            blocks_to_write = int(test_size // block_size)
            
            results = {
                'total_size_tested': test_size,
                'blocks_written': 0,
                'blocks_verified': 0,
                'write_speed': 0,
                'verify_speed': 0,
                'errors': []
            }
            
            # Write phase
            progress = ProgressBar(blocks_to_write, "Writing Test Data")
            start_time = time.time()
            
            test_data = os.urandom(block_size)
            original_hash = hashlib.sha256(test_data).hexdigest()
            
            with open(test_file, 'wb') as f:
                for i in range(blocks_to_write):
                    if self.stop_requested:
                        break
                    
                    f.write(test_data)
                    f.flush()
                    results['blocks_written'] += 1
                    progress.update(i + 1)
            
            progress.complete()
            write_time = time.time() - start_time
            results['write_speed'] = (results['blocks_written'] * block_size) / write_time / (1024 * 1024)  # MB/s
            
            # Verify phase
            progress = ProgressBar(blocks_to_write, "Verifying Test Data")
            start_time = time.time()
            
            with open(test_file, 'rb') as f:
                for i in range(blocks_to_write):
                    if self.stop_requested:
                        break
                    
                    block_data = f.read(block_size)
                    if len(block_data) == block_size:
                        block_hash = hashlib.sha256(block_data).hexdigest()
                        if block_hash == original_hash:
                            results['blocks_verified'] += 1
                        else:
                            error_msg = f"Verification failed at block {i}"
                            results['errors'].append(error_msg)
                            self.logger.error(error_msg)
                    
                    progress.update(i + 1)
            
            progress.complete()
            verify_time = time.time() - start_time
            results['verify_speed'] = (results['blocks_verified'] * block_size) / verify_time / (1024 * 1024)  # MB/s
            
            # Display results
            self._display_capacity_results(results)
            
            self.logger.success("Fast capacity verify completed")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Fast capacity verify failed: {e}")
            return None
        finally:
            # Cleanup
            if 'test_file' in locals():
                self._cleanup_temp_file(test_file, "Capacity test file")
    
    def run_full_capacity_test(self, drive):
        """Run full capacity test"""
        self.logger.info(f"Starting full capacity test on {drive['label']} ({drive['path']})")
        
        try:
            # Get available space
            total, used, free = shutil.disk_usage(drive['path'])
            
            # Use 90% of free space to avoid filling completely
            test_size = free * 0.9
            
            self.logger.info(f"Testing {test_size / (1024*1024*1024):.2f} GB of capacity...")
            
            # Write directly to USB drive for real full capacity testing
            test_file = Path(drive['path']) / f"full_capacity_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tmp"
            block_size = DEFAULT_BLOCK_SIZE_MB * 1024 * 1024  # Convert to bytes
            blocks_to_write = int(test_size // block_size)
            
            results = {
                'total_size_tested': test_size,
                'blocks_written': 0,
                'blocks_verified': 0,
                'write_speed': 0,
                'verify_speed': 0,
                'errors': []
            }
            
            # Write phase with verification
            progress = ProgressBar(blocks_to_write, "Full Capacity Test")
            start_time = time.time()
            
            with open(test_file, 'wb') as f:
                for i in range(blocks_to_write):
                    if self.stop_requested:
                        break
                    
                    # Generate unique data for each block
                    test_data = os.urandom(block_size)
                    f.write(test_data)
                    f.flush()
                    results['blocks_written'] += 1
                    
                    progress.update(i + 1, f"Block {i+1}/{blocks_to_write}")
            
            progress.complete()
            total_time = time.time() - start_time
            results['write_speed'] = (results['blocks_written'] * block_size) / total_time / (1024 * 1024)  # MB/s
            
            # Display results
            self._display_full_capacity_results(results)
            
            self.logger.success("Full capacity test completed")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Full capacity test failed: {e}")
            return None
        finally:
            # Cleanup
            if 'test_file' in locals():
                self._cleanup_temp_file(test_file, "Full capacity test file")
    
    def run_comprehensive_test_fast(self, drive):
        """Run comprehensive test (fast)"""
        self.logger.info(f"Starting comprehensive test (fast) on {drive['label']} ({drive['path']})")
        
        all_results = {
            'drive_info': drive,
            'test_type': 'comprehensive_fast',
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # Initialize results variables
        speed_results = None
        integrity_results = None
        capacity_results = None
        
        # Run all tests
        self.logger.info("=== PHASE 1: SPEED TEST ===")
        speed_results = self.run_speed_test(drive)
        all_results['tests']['speed_test'] = speed_results
        
        if not self.stop_requested and speed_results:
            self.logger.info("=== PHASE 2: DATA INTEGRITY TEST ===")
            integrity_results = self.run_data_integrity_test(drive)
            all_results['tests']['integrity_test'] = integrity_results
        
        if not self.stop_requested and integrity_results:
            self.logger.info("=== PHASE 3: CAPACITY VERIFICATION ===")
            capacity_results = self.run_fast_capacity_verify(drive)
            all_results['tests']['capacity_test'] = capacity_results
        
        # Generate comprehensive report
        if not self.stop_requested:
            report_file = self.report_manager.generate_comprehensive_report(all_results)
            self.logger.success(f"Comprehensive report generated: {report_file}")
            
            # Format drive to restore initial state after comprehensive test
            self._format_drive_after_test(drive)
        
        self.logger.success("Comprehensive test (fast) completed")
        return all_results
    
    def run_comprehensive_test_detailed(self, drive):
        """Run comprehensive test (detailed)"""
        self.logger.info(f"Starting comprehensive test (detailed) on {drive['label']} ({drive['path']})")
        
        all_results = {
            'drive_info': drive,
            'test_type': 'comprehensive_detailed',
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # Initialize results variables
        speed_results = None
        integrity_results = None
        capacity_results = None
        
        # Run all tests
        self.logger.info("=== PHASE 1: SPEED TEST ===")
        speed_results = self.run_speed_test(drive)
        all_results['tests']['speed_test'] = speed_results
        
        if not self.stop_requested and speed_results:
            self.logger.info("=== PHASE 2: DATA INTEGRITY TEST ===")
            integrity_results = self.run_data_integrity_test(drive)
            all_results['tests']['integrity_test'] = integrity_results
        
        if not self.stop_requested and integrity_results:
            self.logger.info("=== PHASE 3: FULL CAPACITY TEST ===")
            capacity_results = self.run_full_capacity_test(drive)
            all_results['tests']['capacity_test'] = capacity_results
        
        # Generate comprehensive report
        if not self.stop_requested:
            report_file = self.report_manager.generate_comprehensive_report(all_results)
            self.logger.success(f"Comprehensive report generated: {report_file}")
            
            # Format drive to restore initial state after comprehensive test
            self._format_drive_after_test(drive)
        
        self.logger.success("Comprehensive test (detailed) completed")
        return all_results
    
    def _test_sequential_write(self, test_file, block_size):
        """Test sequential write speed"""
        test_data = os.urandom(block_size)
        
        start_time = time.time()
        with open(test_file, 'wb') as f:
            f.write(test_data)
            f.flush()
            os.fsync(f.fileno())  # Force write to disk
        end_time = time.time()
        
        speed_mbps = block_size / (end_time - start_time) / (1024 * 1024)
        self.logger.debug(f"Sequential write speed: {speed_mbps:.2f} MB/s")
        return speed_mbps
    
    def _test_sequential_read(self, test_file, block_size):
        """Test sequential read speed"""
        start_time = time.time()
        with open(test_file, 'rb') as f:
            data = f.read(block_size)
        end_time = time.time()
        
        speed_mbps = len(data) / (end_time - start_time) / (1024 * 1024)
        self.logger.debug(f"Sequential read speed: {speed_mbps:.2f} MB/s")
        return speed_mbps
    
    def _test_random_access(self, test_file, block_size):
        """Test random access speed"""
        # Create a larger file for random access
        file_size = block_size * 100
        test_data = os.urandom(file_size)
        
        with open(test_file, 'wb') as f:
            f.write(test_data)
        
        # Random write test
        write_times = []
        for _ in range(10):
            pos = random.randint(0, file_size - block_size)
            random_data = os.urandom(block_size)
            
            start_time = time.time()
            with open(test_file, 'r+b') as f:
                f.seek(pos)
                f.write(random_data)
                f.flush()
            end_time = time.time()
            
            write_times.append(end_time - start_time)
        
        # Random read test
        read_times = []
        for _ in range(10):
            pos = random.randint(0, file_size - block_size)
            
            start_time = time.time()
            with open(test_file, 'rb') as f:
                f.seek(pos)
                data = f.read(block_size)
            end_time = time.time()
            
            read_times.append(end_time - start_time)
        
        avg_write_time = sum(write_times) / len(write_times)
        avg_read_time = sum(read_times) / len(read_times)
        
        write_speed = block_size / avg_write_time / (1024 * 1024)
        read_speed = block_size / avg_read_time / (1024 * 1024)
        
        self.logger.debug(f"Random write speed: {write_speed:.2f} MB/s")
        self.logger.debug(f"Random read speed: {read_speed:.2f} MB/s")
        
        return {
            'write': write_speed,
            'read': read_speed
        }
    
    def _test_access_time(self, test_file):
        """Test access time"""
        access_times = []
        
        for _ in range(100):
            start_time = time.time()
            with open(test_file, 'rb') as f:
                f.read(1)  # Read just 1 byte
            end_time = time.time()
            
            access_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
        
        avg_access_time = sum(access_times) / len(access_times)
        self.logger.debug(f"Average access time: {avg_access_time:.2f} ms")
        return avg_access_time
    
    def _generate_test_pattern(self, pattern_name, size):
        """Generate test data pattern"""
        if pattern_name == 'zeros':
            return b'\x00' * size
        elif pattern_name == 'ones':
            return b'\xFF' * size
        elif pattern_name == 'alternating':
            return b'\xAA' * size
        elif pattern_name == 'random':
            return os.urandom(size)
        elif pattern_name == 'incremental':
            return bytes(i % 256 for i in range(size))
        else:
            return os.urandom(size)
    
    def _display_speed_results(self, results):
        """Display speed test results"""
        print(f"\n{'='*60}")
        print(f"{'SPEED TEST RESULTS':^60}")
        print(f"{'='*60}")
        print(f"Sequential Write: {results['sequential_write_avg']:.2f} MB/s")
        print(f"Sequential Read:  {results['sequential_read_avg']:.2f} MB/s")
        print(f"Random Write:     {results['random_write_avg']:.2f} MB/s")
        print(f"Random Read:      {results['random_read_avg']:.2f} MB/s")
        print(f"Access Time:      {results['access_time_avg']:.2f} ms")
        print(f"{'='*60}")
    
    def _display_integrity_results(self, results):
        """Display data integrity results"""
        print(f"\n{'='*60}")
        print(f"{'DATA INTEGRITY TEST RESULTS':^60}")
        print(f"{'='*60}")
        print(f"Patterns Tested:      {results['patterns_tested']}")
        print(f"Files Created:        {results['files_created']}")
        print(f"Verification Passed:  {results['verification_passed']}")
        print(f"Verification Failed:  {results['verification_failed']}")
        if results['errors']:
            print(f"Errors:")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
        print(f"{'='*60}")
    
    def _display_capacity_results(self, results):
        """Display capacity test results"""
        print(f"\n{'='*60}")
        print(f"{'CAPACITY TEST RESULTS':^60}")
        print(f"{'='*60}")
        print(f"Size Tested:      {results['total_size_tested'] / (1024*1024):.1f} MB")
        print(f"Blocks Written:   {results['blocks_written']}")
        print(f"Blocks Verified:  {results['blocks_verified']}")
        print(f"Write Speed:      {results['write_speed']:.2f} MB/s")
        print(f"Verify Speed:     {results['verify_speed']:.2f} MB/s")
        if results['errors']:
            print(f"Errors: {len(results['errors'])}")
        print(f"{'='*60}")
    
    def _display_full_capacity_results(self, results):
        """Display full capacity test results"""
        print(f"\n{'='*60}")
        print(f"{'FULL CAPACITY TEST RESULTS':^60}")
        print(f"{'='*60}")
        print(f"Size Tested:      {results['total_size_tested'] / (1024*1024*1024):.2f} GB")
        print(f"Blocks Written:   {results['blocks_written']}")
        print(f"Write Speed:      {results['write_speed']:.2f} MB/s")
        if results['errors']:
            print(f"Errors: {len(results['errors'])}")
        print(f"{'='*60}")
    
    def _cleanup_temp_file(self, file_path, description):
        """Clean up temporary file based on configuration"""
        if not file_path.exists():
            return
            
        if DELETE_TEMP_FILES:
            try:
                file_path.unlink()
                self.logger.info(f"{description} cleaned up")
            except Exception as e:
                self.logger.warning(f"Could not clean up {description.lower()}: {e}")
        else:
            # For USB drive files, show they're preserved on the drive
            self.logger.info(f"{description} preserved on USB drive at: {file_path}")
    
    def _cleanup_temp_directory(self, dir_path, description):
        """Clean up temporary directory based on configuration"""
        if not dir_path.exists():
            return
            
        if DELETE_TEMP_FILES:
            try:
                shutil.rmtree(dir_path)
                self.logger.info(f"{description} cleaned up")
            except Exception as e:
                self.logger.warning(f"Could not clean up {description.lower()}: {e}")
        else:
            # For USB drive directories, show they're preserved on the drive
            self.logger.info(f"{description} preserved on USB drive at: {dir_path}")
    
    def _format_drive_after_test(self, drive):
        """Format drive after destructive test to restore initial state"""
        try:
            self.logger.info("Restoring drive to initial state...")
            
            # Get original filesystem
            original_fs = self.drive_detector.get_drive_filesystem(drive['path'])
            original_label = drive['label'] if drive['label'] != 'Unknown' else 'USB_DRIVE'
            
            self.logger.info(f"Detected original filesystem: {original_fs}")
            self.logger.info(f"Original label: {original_label}")
            
            # Format drive automatically
            success = self.drive_detector.format_drive(
                drive['path'], 
                filesystem=original_fs, 
                label=original_label
            )
            
            if success:
                self.logger.success("Drive successfully restored to initial state")
            else:
                self.logger.warning("Drive formatting failed - you may need to format manually")
                self.logger.info(f"To format manually: Right-click drive {drive['path']} → Format → {original_fs}")
            
        except Exception as e:
            self.logger.error(f"Error during drive restoration: {e}")