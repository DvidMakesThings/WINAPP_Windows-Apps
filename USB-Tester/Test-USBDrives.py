#!/usr/bin/env python3
"""
USB Storage Tester v2.0
Main entry point for the application
"""

from src.usb_tester import USBStorageTester

def main():
    """Main entry point"""
    try:
        tester = USBStorageTester()
        tester.run()
    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()