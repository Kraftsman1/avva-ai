import os
import glob
import subprocess
import shlex
import shutil

# -----------------------------
# Assistant Tool Manifest
# -----------------------------
MANIFEST = {
    "launch_application": {
        "description": (
            "Launch a desktop application by name or intent "
            "(e.g. 'firefox', 'browser', 'terminal', 'terminal_emulator')."
        )
    }
}

# -----------------------------
# Constants & Mappings
# -----------------------------
FIELD_CODES = ["%U", "%u", "%F", "%f", "%i", "%c", "%k", "%n", "%m", "%v"]

INTENT_ALIASES = {
    "browser": ["browser", "internet", "web", "chrome", "firefox", "navigator"],
    "terminal": ["terminal", "console", "shell", "bash", "command prompt"],
    "terminal_emulator": ["terminal emulator", "gui terminal", "gnome-terminal", "kgx", "konsole"],
    "calculator": ["calculator", "calc"],
    "editor": ["editor", "text editor", "code", "ide", "writing"],
    "files": ["files", "file manager", "explorer", "nautilus", "thunar"],
    "settings": ["settings", "preferences", "control panel", "config"],
    "music": ["music", "audio", "player", "spotify"],
    "video": ["video", "movie", "media", "vlc"]
}

CATEGORY_MAP = {
    "browser": ["WebBrowser", "Network"],
    "terminal": ["TerminalEmulator", "System"],
    "calculator": ["Calculator", "Utility"],
    "editor": ["TextEditor", "Development", "IDE"],
    "files": ["FileManager", "System", "Core"],
    "settings": ["Settings", "DesktopSettings"],
    "music": ["Audio", "Music", "Player"],
    "video": ["Video", "Player"]
}

SEARCH_DIRS = [
    "/usr/share/applications",
    os.path.expanduser("~/.local/share/applications"),
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
    """Finds an installed terminal emulator for CLI apps."""
    candidates = ["com.system76.CosmicTerm", "gnome-terminal", "kgx", "konsole", "alacritty", "kitty", "xterm"]
    for term in candidates:
        if shutil.which(term):
            return term
    return "xterm"

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
            "hidden": False,
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
                        data["categories"] = line.split("=", 1)[1].split(";")
                    elif line.startswith("Keywords="):
                        data["keywords"] = line.split("=", 1)[1].lower().split(";")
                    elif line.startswith("NoDisplay=true"):
                        data["hidden"] = True
        except Exception:
            return None

        if not data["name"] or data["hidden"] or not data["exec"]:
            return None

        return data

    def resolve(self, query):
        query_clean = query.lower().strip()
        intent = normalize_intent(query_clean)

        candidates = []
        for entry in self.entries:
            score = 0
            name = entry["name"].lower()
            fname = os.path.basename(entry["path"]).lower()

            if query_clean == name:
                score += 100
            elif query_clean in name:
                score += 50

            if query_clean in fname:
                score += 40

            if intent in CATEGORY_MAP:
                for cat in CATEGORY_MAP[intent]:
                    if cat in entry["categories"]:
                        score += 30

            for kw in entry["keywords"]:
                if query_clean in kw:
                    score += 20
                    break

            if score > 0:
                candidates.append((score, entry))

        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates

# -----------------------------
# Public Tool Entry
# -----------------------------
INDEX = DesktopIndex()

def launch_application(query):
    if not query:
        return {"status": "error", "message": "No application specified"}

    results = INDEX.resolve(query)

    if not results:
        return {"status": "not_found", "query": query}

    # Ambiguity handling
    top_score = results[0][0]
    close_matches = [r for r in results if r[0] >= top_score - 10]

    if len(close_matches) > 1 and query.lower() not in results[0][1]["name"].lower():
        return {
            "status": "ambiguous",
            "options": [r[1]["name"] for r in close_matches[:5]]
        }

    entry = results[0][1]

    try:
        intent = normalize_intent(query)

        # -----------------
        # Dual Terminal Handling
        # -----------------
        if intent == "terminal":  # CLI/console apps
            term_bin = find_preferred_terminal()
            cmd = [term_bin, "-e"] + shlex.split(clean_exec(entry["exec"]))
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        elif intent == "terminal_emulator":  # GUI terminals
            subprocess.Popen(["gio", "launch", entry["path"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        elif entry["terminal"]:  # Terminal=true for CLI apps
            term_bin = find_preferred_terminal()
            cmd = [term_bin, "-e"] + shlex.split(clean_exec(entry["exec"]))
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        elif entry["exec"]:  # Standard GUI apps
            cmd = shlex.split(clean_exec(entry["exec"]))
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        else:  # Fallback
            subprocess.Popen(["gio", "launch", entry["path"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return {"status": "launched", "app": entry["name"]}

    except Exception as e:
        return {"status": "error", "message": str(e)}

# -----------------------------
# Test
# -----------------------------
if __name__ == "__main__":
    print(launch_application("terminal"))            # CLI/console
    print(launch_application("terminal emulator"))  # GUI terminal
    print(launch_application("calculator"))
    print(launch_application("browser"))
