"""Progress bar utilities for USB Storage Tester"""

import sys
import time
from colorama import Fore, Style

class ProgressBar:
    """Enhanced progress bar with ETA and speed indicators"""
    
    def __init__(self, total, description="Progress", width=50):
        self.total = total
        self.current = 0
        self.description = description
        self.width = width
        self.start_time = time.time()
        self.last_update = 0
    
    def update(self, current, status=""):
        """Update progress bar"""
        self.current = current
        
        # Throttle updates to avoid too frequent refreshes
        now = time.time()
        if now - self.last_update < 0.1 and current < self.total:
            return
        self.last_update = now
        
        # Calculate progress
        progress = min(current / self.total, 1.0)
        filled_width = int(self.width * progress)
        
        # Calculate ETA
        elapsed = now - self.start_time
        if current > 0 and current < self.total:
            eta = (elapsed / current) * (self.total - current)
            eta_str = f"ETA: {self._format_time(eta)}"
        else:
            eta_str = "ETA: --:--"
        
        # Calculate speed
        if elapsed > 0:
            speed = current / elapsed
            speed_str = f"{speed:.1f}/s"
        else:
            speed_str = "0.0/s"
        
        # Build progress bar
        bar = f"{Fore.GREEN}{'█' * filled_width}{Style.RESET_ALL}"
        bar += f"{Fore.WHITE}{'░' * (self.width - filled_width)}{Style.RESET_ALL}"
        
        # Build status line
        percentage = progress * 100
        status_line = f"\r{Fore.CYAN}[{self.description}]{Style.RESET_ALL} "
        status_line += f"{bar} {percentage:5.1f}% "
        status_line += f"({current}/{self.total}) "
        status_line += f"{speed_str} {eta_str}"
        
        if status:
            status_line += f" - {status}"
        
        # Print and flush
        sys.stdout.write(status_line)
        sys.stdout.flush()
    
    def complete(self):
        """Mark progress as complete"""
        elapsed = time.time() - self.start_time
        
        bar = f"{Fore.GREEN}{'█' * self.width}{Style.RESET_ALL}"
        status_line = f"\r{Fore.CYAN}[{self.description}]{Style.RESET_ALL} "
        status_line += f"{bar} {Fore.GREEN}100.0%{Style.RESET_ALL} "
        status_line += f"({self.total}/{self.total}) "
        status_line += f"Completed in {self._format_time(elapsed)}"
        
        print(status_line)
    
    def _format_time(self, seconds):
        """Format time in MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"


class SpeedIndicator:
    """Real-time speed indicator"""
    
    def __init__(self, description="Speed"):
        self.description = description
        self.start_time = time.time()
        self.bytes_processed = 0
        self.last_update = 0
    
    def update(self, bytes_processed):
        """Update speed indicator"""
        self.bytes_processed = bytes_processed
        
        now = time.time()
        if now - self.last_update < 0.5:  # Update every 0.5 seconds
            return
        self.last_update = now
        
        elapsed = now - self.start_time
        if elapsed > 0:
            speed_bps = bytes_processed / elapsed
            speed_mbps = speed_bps / (1024 * 1024)
            
            status_line = f"\r{Fore.YELLOW}[{self.description}]{Style.RESET_ALL} "
            status_line += f"{self._format_bytes(bytes_processed)} "
            status_line += f"@ {speed_mbps:.2f} MB/s"
            
            sys.stdout.write(status_line)
            sys.stdout.flush()
    
    def complete(self):
        """Complete speed indicator"""
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            speed_bps = self.bytes_processed / elapsed
            speed_mbps = speed_bps / (1024 * 1024)
            
            status_line = f"\r{Fore.YELLOW}[{self.description}]{Style.RESET_ALL} "
            status_line += f"{self._format_bytes(self.bytes_processed)} "
            status_line += f"@ {speed_mbps:.2f} MB/s "
            status_line += f"in {elapsed:.1f}s"
            
            print(status_line)
    
    def _format_bytes(self, bytes_count):
        """Format bytes in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024
        return f"{bytes_count:.1f} TB"