#!/usr/bin/env python3
import os
from pathlib import Path

def get_desktop_files():
    dirs = [
        "/usr/share/applications",
        "/usr/local/share/applications",
        str(Path.home() / ".local/share/applications")
    ]

    desktop_files = []

    for dir_path in dirs:
        if os.path.exists(dir_path):
            for file in os.listdir(dir_path):
                if file.endswith(".desktop"):
                    desktop_files.append(file)

    return sorted(set(desktop_files))

if __name__ == "__main__":
    apps = get_desktop_files()
    print(f"Found {len(apps)} desktop entries:\n")
    for app in apps:
        print(f"- {app}")
