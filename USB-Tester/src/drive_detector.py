"""Drive detection utilities for USB Storage Tester"""

import os
import sys
import psutil
import subprocess
from pathlib import Path

try:
    import wmi
    import win32api  # type: ignore[import]
    import win32file  # type: ignore[import]
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

from .logger import Logger

class DriveDetector:
    """USB drive detection and information gathering"""
    
    def __init__(self, logger=None):
        self.logger = logger or Logger()
        self.drives = []
    
    def scan_usb_drives(self):
        """Scan for USB storage devices"""
        self.logger.info("Scanning for USB storage devices...")
        self.drives = []
        
        if sys.platform == "win32" and WMI_AVAILABLE:
            self._scan_windows_drives()
        else:
            self._scan_cross_platform_drives()
        
        if self.drives:
            self.logger.success(f"Found {len(self.drives)} USB drive(s)")
        else:
            self.logger.warning("No USB drives detected")
        
        return self.drives
    
    def _scan_windows_drives(self):
        """Scan drives on Windows using WMI"""
        try:
            c = wmi.WMI()
            
            # Get USB storage devices
            for disk in c.Win32_DiskDrive():
                if disk.InterfaceType and 'USB' in disk.InterfaceType.upper():
                    drive_info = self._get_windows_drive_info(disk)
                    if drive_info:
                        self.drives.append(drive_info)
                        
        except Exception as e:
            self.logger.error(f"Error scanning Windows drives: {e}")
            self._scan_cross_platform_drives()
    
    def _scan_cross_platform_drives(self):
        """Scan drives using cross-platform method"""
        try:
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                if self._is_removable_drive(partition):
                    drive_info = self._get_cross_platform_drive_info(partition)
                    if drive_info:
                        self.drives.append(drive_info)
                        
        except Exception as e:
            self.logger.error(f"Error scanning drives: {e}")
    
    def _get_windows_drive_info(self, disk):
        """Get detailed drive information on Windows"""
        try:
            drive_info = {
                'path': None,
                'label': disk.Caption or 'Unknown',
                'size': int(disk.Size) if disk.Size else 0,
                'model': disk.Model or 'Unknown',
                'serial': disk.SerialNumber or 'Unknown',
                'interface': disk.InterfaceType or 'USB',
                'vendor': 'Unknown',
                'product': 'Unknown'
            }
            
            # Get drive letter
            c = disk.associators("Win32_DiskDriveToDiskPartition")
            for partition in c:
                logical_disks = partition.associators("Win32_LogicalDiskToPartition")
                for logical_disk in logical_disks:
                    if logical_disk.DriveType == 2:  # Removable disk
                        drive_info['path'] = logical_disk.DeviceID + '\\'
                        drive_info['label'] = logical_disk.VolumeName or drive_info['label']
                        break
            
            return drive_info if drive_info['path'] else None
            
        except Exception as e:
            self.logger.error(f"Error getting Windows drive info: {e}")
            return None
    
    def _get_cross_platform_drive_info(self, partition):
        """Get drive information using cross-platform method"""
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            
            return {
                'path': partition.mountpoint,
                'label': partition.device,
                'size': usage.total,
                'model': 'Unknown',
                'serial': 'Unknown',
                'interface': 'USB',
                'vendor': 'Unknown',
                'product': 'Unknown'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting drive info for {partition.device}: {e}")
            return None
    
    def _is_removable_drive(self, partition):
        """Check if partition is a removable drive"""
        try:
            if sys.platform == "win32":
                drive_type = win32file.GetDriveType(partition.mountpoint)
                return drive_type == win32file.DRIVE_REMOVABLE
            else:
                # On Linux/macOS, check if it's mounted in typical removable locations
                removable_paths = ['/media', '/mnt', '/Volumes']
                return any(partition.mountpoint.startswith(path) for path in removable_paths)
        except:
            return False
    
    def get_drive_filesystem(self, drive_path):
        """Get the filesystem type of a drive"""
        try:
            if sys.platform == "win32" and WMI_AVAILABLE:
                c = wmi.WMI()
                for logical_disk in c.Win32_LogicalDisk():
                    if logical_disk.DeviceID == drive_path.rstrip('\\'):
                        return logical_disk.FileSystem
            else:
                # For cross-platform, try to get filesystem info
                partitions = psutil.disk_partitions()
                for partition in partitions:
                    if partition.mountpoint == drive_path:
                        return partition.fstype
            return "NTFS"  # Default fallback
        except Exception as e:
            self.logger.error(f"Error getting filesystem type: {e}")
            return "NTFS"  # Default fallback
    
    def format_drive(self, drive_path, filesystem=None, label=None):
        """Format a drive with specified filesystem"""
        try:
            if not filesystem:
                filesystem = self.get_drive_filesystem(drive_path)
            
            if not label:
                label = "USB_DRIVE"
            
            self.logger.info(f"Formatting drive {drive_path} with {filesystem} filesystem...")
            
            if sys.platform == "win32":
                drive_letter = drive_path.rstrip('\\:')
                if not drive_letter.endswith(':'):
                    drive_letter += ':'
                
                # Clean label for Windows (remove spaces and special chars)
                clean_label = ''.join(c for c in label if c.isalnum() or c in '-_')[:11]
                
                # Use PowerShell Format-Volume (most reliable method)
                ps_cmd = f'Format-Volume -DriveLetter {drive_letter[0]} -FileSystem {filesystem} -NewFileSystemLabel "{clean_label}" -Confirm:$false'
                
                try:
                    result = subprocess.run(
                        ['powershell', '-Command', ps_cmd],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if result.returncode == 0:
                        self.logger.success(f"Drive {drive_path} formatted successfully")
                        return True
                    else:
                        self.logger.error(f"PowerShell format failed: {result.stderr}")
                        return False
                        
                except subprocess.TimeoutExpired:
                    self.logger.error("Format operation timed out")
                    return False
                except Exception as e:
                    self.logger.error(f"Format operation failed: {e}")
                    return False
            else:
                # Linux/macOS format commands (requires sudo)
                self.logger.warning("Formatting on Linux/macOS requires manual intervention")
                return False
                
        except Exception as e:
            self.logger.error(f"Error formatting drive: {e}")
            return False
    
    def display_drives(self):
        """Display detected drives in a formatted table"""
        if not self.drives:
            self.logger.warning("No drives to display")
            return
        
        print(f"\n{'='*80}")
        print(f"{'DETECTED USB DRIVES':^80}")
        print(f"{'='*80}")
        
        for i, drive in enumerate(self.drives, 1):
            size_gb = drive['size'] / (1024**3) if drive['size'] > 0 else 0
            
            print(f"\n{i}. {drive['label']}")
            print(f"   Path: {drive['path']}")
            print(f"   Size: {size_gb:.2f} GB")
            print(f"   Model: {drive['model']}")
            print(f"   Serial: {drive['serial']}")
            print(f"   Interface: {drive['interface']}")
        
        print(f"\n{'='*80}")
    
    def get_drive_by_index(self, index):
        """Get drive by menu index (1-based)"""
        try:
            return self.drives[index - 1] if 1 <= index <= len(self.drives) else None
        except (IndexError, TypeError):
            return None