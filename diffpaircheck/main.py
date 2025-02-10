#!/usr/bin/env python3
import sys
import os

# Add the parent directory to sys.path so that diffpaircheck becomes importable.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from diffpaircheck.app import DiffPairApp

if __name__ == "__main__":
    app = DiffPairApp()
    app.mainloop()
