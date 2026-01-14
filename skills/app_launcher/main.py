import os
import glob
import subprocess
from collections import defaultdict

# -----------------------------
# Assistant Tool Manifest
# -----------------------------
MANIFEST = {
    "launch_application": {
        "description": (
            "Launch a desktop application by name or intent "
            "(e.g. 'firefox', 'browser', 'terminal')."
        )
    }
}

# -----------------------------
# Intent Normalization
# -----------------------------
INTENT_ALIASES = {
    "browser": ["browser", "internet", "web", "chrome", "firefox"],
    "terminal": ["terminal", "console", "shell"],
    "calculator": ["calculator", "calc"],
    "editor": ["editor", "text editor", "code", "ide"],
    "files": ["files", "file manager", "explorer"],
    "settings": ["settings", "preferences", "control panel"],
    "music": ["music", "audio", "player"],
    "video": ["video", "movie", "media"]
}

CATEGORY_MAP = {
    "browser": ["WebBrowser", "Network"],
    "terminal": ["TerminalEmulator"],
    "calculator": ["Calculator"],
    "editor": ["TextEditor", "IDE", "Development"],
    "files": ["FileManager"],
    "settings": ["Settings"],
    "music": ["Audio", "Music", "Player"],
    "video": ["Video", "Player"]
}

SEARCH_DIRS = [
    "/usr/share/applications",
    os.path.expanduser("~/.local/share/applications"),
    "/var/lib/flatpak/exports/share/applications",
]

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
            "categories": [],
            "keywords": [],
            "hidden": False,
        }

        try:
            with open(path, "r", errors="ignore") as f:
                for line in f:
                    if line.startswith("Name="):
                        data["name"] = line.split("=", 1)[1].strip()
                    elif line.startswith("Categories="):
                        data["categories"] = line.split("=", 1)[1].split(";")
                    elif line.startswith("Keywords="):
                        data["keywords"] = line.split("=", 1)[1].lower().split(";")
                    elif line.startswith("NoDisplay=true"):
                        data["hidden"] = True
        except Exception:
            return None

        if not data["name"] or data["hidden"]:
            return None

        return data

    # -----------------------------
    # Resolver
    # -----------------------------
    def resolve(self, query):
        query = query.lower().strip()
        intent = normalize_intent(query)

        candidates = []

        for entry in self.entries:
            score = 0
            name = entry["name"].lower()
            fname = os.path.basename(entry["path"]).lower()

            # Exact / partial name match
            if query == name:
                score += 100
            elif query in name:
                score += 50

            # Filename signal
            if query in fname:
                score += 40

            # Intent category match
            if intent in CATEGORY_MAP:
                for cat in CATEGORY_MAP[intent]:
                    if cat in entry["categories"]:
                        score += 30

            # Keyword match
            if query in entry["keywords"]:
                score += 20

            if score > 0:
                candidates.append((score, entry))

        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates


# -----------------------------
# Intent Helpers
# -----------------------------
def normalize_intent(query):
    for canonical, aliases in INTENT_ALIASES.items():
        if query == canonical or query in aliases:
            return canonical
    return query


# -----------------------------
# Public Tool Entry
# -----------------------------
INDEX = DesktopIndex()

def launch_application(query):
    if not query:
        return {
            "status": "error",
            "message": "No application specified"
        }

    results = INDEX.resolve(query)

    if not results:
        return {
            "status": "not_found",
            "query": query
        }

    # Ambiguity handling
    top_score = results[0][0]
    close_matches = [r for r in results if r[0] >= top_score - 10]

    if len(close_matches) > 1:
        return {
            "status": "ambiguous",
            "options": [r[1]["name"] for r in close_matches[:5]]
        }

    entry = results[0][1]

    try:
        subprocess.Popen(
            ["gio", "launch", entry["path"]],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return {
            "status": "launched",
            "app": entry["name"]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# -----------------------------
# Local Testing
# -----------------------------
if __name__ == "__main__":
    print(launch_application("terminal"))
    print(launch_application("browser"))
    print(launch_application("code"))
