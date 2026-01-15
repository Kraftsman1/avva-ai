#!/usr/bin/env python3
# MIT License - Copyright (c) 2026 Asigri Shamsu-Deen Al-Heyr
import sys
import os

# Add the current directory to sys.path so imports work
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from ui.dashboard import Dashboard
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def main():
    print("🚀 Starting AVVA Visual Dashboard...")
    try:
        win = Dashboard()
        Gtk.main()
    except KeyboardInterrupt:
        print("\nShutting down AVVA. Goodbye!")

if __name__ == "__main__":
    main()
