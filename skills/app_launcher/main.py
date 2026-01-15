#!/usr/bin/env python3
import os
import glob
import subprocess
import shlex
import shutil
import rapidfuzz
from pathlib import Path

# -----------------------------
# Assistant Tool Manifest
# -----------------------------
MANIFEST = {
    "launch_application": {
        "description": "Launch a desktop application by name or generic intent (e.g. 'browser', 'terminal')."
    }
}

# -----------------------------
# Constants & Aliases
# -----------------------------
FIELD_CODES = ["%U", "%u", "%F", "%f", "%i", "%c", "%k", "%n", "%m", "%v"]

INTENT_ALIASES = {
    "browser": ["internet", "web", "browser", "navigator"],
    "terminal": ["terminal", "console", "shell", "command prompt"],
    "calculator": ["calc", "calculator", "math"],
    "editor": ["text editor", "code", "editor", "ide"],
    "files": ["file manager", "explorer", "files"],
    "settings": ["preferences", "settings", "configuration"],
    "music": ["music", "audio", "player"],
    "video": ["video", "movie", "media"]
}

SEARCH_DIRS = [
    "/usr/share/applications",
    "/usr/local/share/applications",
    str(Path.home() / ".local/share/applications"),
    "/var/lib/flatpak/exports/share/applications",
]

# -----------------------------
# Helpers
# -----------------------------
def clean_exec(exec_cmd):
    """Strips Freedesktop field codes from the Exec command."""
    for code in FIELD_CODES:
        exec_cmd = exec_cmd.replace(code, "")
    return exec_cmd.strip()

def find_preferred_terminal():
    """Finds an installed terminal emulator."""
    candidates = ["com.system76.CosmicTerm", "gnome-terminal", "kgx", "konsole", "alacritty", "kitty", "xterm"]
    for term in candidates:
        if shutil.which(term):
            return term
    return "xterm"

def fallback_path_executable(query):
    """Checks if the query is a direct command in $PATH."""
    exe = shutil.which(query)
    if exe:
        return {"name": query, "exec": exe, "terminal": True, "keywords": []}
    return None

# -----------------------------
# Desktop Index
# -----------------------------
class DesktopIndex:
    def __init__(self):
        self.entries = []
        self._build_index()

    def _build_index(self):
        for sdir in SEARCH_DIRS:
            if not os.path.exists(sdir):
                continue
            for path in glob.glob(os.path.join(sdir, "*.desktop")):
                entry = self._parse_desktop_file(path)
                if entry:
                    self.entries.append(entry)

    def _parse_desktop_file(self, path):
        data = {
            "path": path, 
            "name": "", 
            "exec": "", 
            "terminal": False,
            "keywords": [], 
            "hidden": False
        }
        try:
            with open(path, "r", errors="ignore") as f:
                current_section = ""
                for line in f:
                    line = line.strip()
                    if line.startswith("[") and line.endswith("]"):
                        current_section = line
                        continue
                    if current_section != "[Desktop Entry]":
                        continue

                    if line.startswith("Name="):
                        data["name"] = line.split("=", 1)[1].strip()
                    elif line.startswith("Exec="):
                        data["exec"] = line.split("=", 1)[1].strip()
                    elif line.startswith("Terminal="):
                        data["terminal"] = line.split("=", 1)[1].strip().lower() == "true"
                    elif line.startswith("Keywords="):
                        # Keywords are semicolon separated
                        kws = line.split("=", 1)[1].split(";")
                        data["keywords"].extend([k.strip().lower() for k in kws if k.strip()])
                    elif line.startswith("NoDisplay=true"):
                        data["hidden"] = True
        except Exception:
            return None

        if not data["name"] or data["hidden"] or not data["exec"]:
            return None
        return data

    def resolve(self, query):
        """Uses RapidFuzz to find the best matching application."""
        query_clean = query.lower().strip()
        candidates = []

        for entry in self.entries:
            name = entry["name"].lower()
            fname = os.path.basename(entry["path"]).lower()
            
            # 1. Check for Intent Match (Manual boost)
            intent_boost = 0
            for canonical, aliases in INTENT_ALIASES.items():
                if query_clean == canonical or query_clean in aliases:
                    # If this app belongs to the category, boost it
                    # We check keywords/names for category hints since user removed Category parsing
                    if canonical in name or any(canonical in kw for kw in entry["keywords"]):
                        intent_boost = 20

            # 2. Fuzzy Matching with RapidFuzz
            # WRatio is great for varying length strings and partial matches
            score_name = rapidfuzz.fuzz.WRatio(query_clean, name)
            score_file = rapidfuzz.fuzz.WRatio(query_clean, fname)
            
            max_kw_score = 0
            for kw in entry["keywords"]:
                kw_score = rapidfuzz.fuzz.WRatio(query_clean, kw)
                if kw_score > max_kw_score:
                    max_kw_score = kw_score

            # Combined score
            final_score = (score_name * 1.0) + (score_file * 0.5) + (max_kw_score * 0.3) + intent_boost
            
            if final_score > 60: # Threshold for a confident match
                candidates.append((final_score, entry))

        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates

# -----------------------------
# Launcher Logic
# -----------------------------
INDEX = DesktopIndex()

def launch_application(query):
    if not query:
        return {"status": "error", "message": "No application specified"}

    results = INDEX.resolve(query)
    entry = None

    if results:
        # Check if top result is significantly better
        if len(results) > 1 and (results[0][0] - results[1][0] < 5):
            # If scores are very close, report ambiguity
            return {
                "status": "ambiguous",
                "options": [r[1]["name"] for r in results[:5]]
            }
        entry = results[0][1]
    else:
        # Fallback to direct executable if no desktop file found
        entry = fallback_path_executable(query)
        if not entry:
            return {"status": "not_found", "query": query}

    try:
        # 1. Clean the Exec command
        clean_cmd = clean_exec(entry["exec"])
        
        # 2. Handle Terminal apps
        if entry.get("terminal", False):
            term = find_preferred_terminal()
            # Most modern terminals support -e or -- to execute commands
            subprocess.Popen([term, "-e"] + shlex.split(clean_cmd), 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # GUI apps
            subprocess.Popen(shlex.split(clean_cmd), 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return {"status": "launched", "app": entry["name"]}
    except Exception as e:
        return {"status": "error", "message": f"Launch failed: {str(e)}"}

if __name__ == "__main__":
    tests = ["terminal", "browser", "calculator", "vlc", "code", "nautilus"]
    for t in tests:
        print(f"Testing '{t}':", launch_application(t))
