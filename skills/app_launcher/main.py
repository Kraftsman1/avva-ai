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

def normalize_intent(query):
    query_clean = query.lower().strip()
    for canonical, aliases in INTENT_ALIASES.items():
        if query_clean == canonical or query_clean in aliases:
            return canonical
    return query_clean

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
            "categories": [],
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
                    elif line.startswith("Categories="):
                        data["categories"] = [c.strip() for c in line.split("=", 1)[1].split(";") if c.strip()]
                    elif line.startswith("Keywords="):
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
        """
        Uses a weighted search across Name, Filename, Keywords, and Categories.
        Expands generic intents (e.g., 'browser') into multiple search terms.
        """
        query_clean = query.lower().strip()
        intent = normalize_intent(query_clean)
        candidates = []

        # Expansion terms for generic intents
        INTENT_EXPANSION = {
            "browser": ["firefox", "chrome", "chromium", "opera", "browser", "web", "navigator", "internet", "net"],
            "terminal": ["terminal", "console", "shell", "emulator", "bash", "term", "cosmic-term"],
            "calculator": ["calc", "math", "calculator", "spreadsheet", "excel"],
            "editor": ["code", "editor", "text", "ide", "writing", "edit", "vscode"],
            "files": ["files", "explorer", "manager", "nautilus", "thunar", "folder"],
            "settings": ["settings", "config", "preferences", "control"],
            "music": ["music", "audio", "player", "spotify", "rhythmbox"],
            "video": ["video", "movie", "player", "vlc", "mpv", "totem"]
        }

        # Categories for generic intents (Primary + Fallback)
        INTENT_CATS = {
            "browser": ["WebBrowser", "Network"],
            "terminal": ["TerminalEmulator", "System"],
            "calculator": ["Calculator", "Office", "Spreadsheet"],
            "editor": ["TextEditor", "IDE", "Development"],
            "files": ["FileManager"],
            "settings": ["Settings", "DesktopSettings"],
            "music": ["Music", "Audio"],
            "video": ["Video", "AudioVideo"]
        }

        for entry in self.entries:
            name = entry["name"].lower()
            fname = os.path.basename(entry["path"]).lower()
            kws = " ".join(entry["keywords"])
            cats = entry["categories"]
            
            score = 0
            
            # 1. Direct Search Matching
            search_terms = [query_clean]
            if intent in INTENT_EXPANSION:
                search_terms.extend(INTENT_EXPANSION[intent])
            
            for term in search_terms:
                if term in name:
                    score += 50
                    if term == name: score += 50
                    break
                if term in fname:
                    score += 40
                    break
            
            # 2. Category Match
            if intent in INTENT_CATS:
                for idx, cat in enumerate(INTENT_CATS[intent]):
                    if cat in cats:
                        # Primary category (first in list) gets more boost
                        score += 50 if idx == 0 else 25
                        break

            # 3. Keyword Match
            for term in search_terms:
                if term in kws:
                    score += 20
                    break

            # 4. Fuzzy logic fallback
            fuzzy_name = rapidfuzz.fuzz.token_set_ratio(query_clean, name)
            
            final_score = score + (fuzzy_name * 0.5)

            if final_score > 40:
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
