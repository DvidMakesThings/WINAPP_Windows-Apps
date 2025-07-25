"""Menu system for USB Storage Tester"""

from colorama import Fore, Style
from .config import VERSION, TITLE
from .logger import Logger

class Menu:
    """Main menu system"""
    
    def __init__(self, logger=None):
        self.logger = logger or Logger()
    
    def show_menu(self):
        """Display main menu"""
        print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  {TITLE} v{VERSION}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1.{Style.RESET_ALL} 📊 Scan for USB drives")
        print(f"{Fore.CYAN}2.{Style.RESET_ALL} ⚡ Run speed test only")
        print(f"{Fore.CYAN}3.{Style.RESET_ALL} 🛡️  Run data integrity test only")
        print(f"{Fore.CYAN}4.{Style.RESET_ALL} 🚀 Run fast capacity verify only")
        print(f"{Fore.CYAN}5.{Style.RESET_ALL} 💾 Run full capacity test only")
        print(f"{Fore.CYAN}6.{Style.RESET_ALL} 🔍 Run comprehensive test fast")
        print(f"{Fore.CYAN}7.{Style.RESET_ALL} 🔍 Run comprehensive test detailed")
        print(f"{Fore.CYAN}8.{Style.RESET_ALL} 📋 View test logs")
        print(f"{Fore.CYAN}9.{Style.RESET_ALL} 📄 View test reports")
        print(f"{Fore.CYAN}10.{Style.RESET_ALL} 🚪 Exit")
    
    def get_user_choice(self, max_choice=10):
        """Get and validate user choice"""
        try:
            choice = input(f"\nEnter your choice (1-{max_choice}): ").strip()
            return int(choice)
        except ValueError:
            return None
    
    def show_drive_selection_menu(self, drives):
        """Show drive selection menu"""
        if not drives:
            self.logger.warning("No drives available for selection")
            return None
        
        print(f"\n{Fore.YELLOW}Select a drive to test:{Style.RESET_ALL}")
        for i, drive in enumerate(drives, 1):
            size_gb = drive['size'] / (1024**3) if drive['size'] > 0 else 0
            print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {drive['label']} ({size_gb:.2f} GB) - {drive['path']}")
        
        try:
            choice = int(input(f"\nEnter drive number (1-{len(drives)}): "))
            if 1 <= choice <= len(drives):
                return drives[choice - 1]
            else:
                self.logger.error("Invalid drive selection")
                return None
        except ValueError:
            self.logger.error("Invalid input. Please enter a number.")
            return None
    
    def confirm_destructive_test(self, drive, test_type):
        """Confirm destructive test operation"""
        print(f"\n{Fore.RED}⚠️  WARNING: DESTRUCTIVE TEST ⚠️{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}This {test_type} will OVERWRITE ALL DATA on:{Style.RESET_ALL}")
        print(f"  Drive: {drive['label']}")
        print(f"  Path: {drive['path']}")
        print(f"  Size: {drive['size'] / (1024**3):.2f} GB")
        print(f"\n{Fore.RED}ALL DATA ON THIS DRIVE WILL BE PERMANENTLY LOST!{Style.RESET_ALL}")
        
        confirmation = input(f"\nType 'YES' to confirm: ").strip().upper()
        return confirmation == 'YES'
    
    def pause(self, message="Press Enter to continue..."):
        """Pause execution and wait for user input"""
        input(f"\n{message}")