# AVVA Skills Blueprint

This document outlines the planned roadmap for AVVA's capabilities. Skills are modular components located in the `skills/` directory that extend AVVA's functionality.

---

## 🛠️ Category 1: Core System Control (Priority: HIGH)
The foundation of a Linux assistant is physical control over the machine.

| Skill | Description | Tools/Libraries | Status |
| :--- | :--- | :--- | :--- |
| **System Stats** | Report CPU, RAM, Disk, and Temp usage. | `psutil` | ✅ Done |
| **Volume/Mute** | Control system audio levels. | `amixer`, `pactl` | ⏳ Planned |
| **Brightness** | Control screen backlight. | `brightnessctl`, `light` | ⏳ Planned |
| **App Launcher** | Open apps by name (e.g., "Open Firefox"). | `subprocess`, `shutil` | ⏳ Planned |
| **Power Mgmt** | Shutdown, Reboot, Sleep, Lock Screen. | `systemctl`, `loginctl` | ⏳ Planned |
| **Screenshot** | Capture screen or active window. | `scrot`, `gnome-screenshot`| ⏳ Planned |

---

## 📅 Category 2: Productivity & Work (Priority: MEDIUM)
Helping the user manage their daily tasks and files.

| Skill | Description | Tools/Libraries | Status |
| :--- | :--- | :--- | :--- |
| **Todo Manager** | Add/Remove items from a persistent list. | `sqlite3`, `json` | ⏳ Planned |
| **Calendar** | Check upcoming events or add new ones. | Google Calendar API | ⏳ Planned |
| **Email Digest** | Summarize recent unread emails. | `imaplib` | ⏳ Planned |
| **File Search** | Find files by name/type in home dir. | `find`, `locate` | ⏳ Planned |
| **Timer/Alarm** | Set voice-activated reminders. | `time`, `threading` | ⏳ Planned |

---

## 📺 Category 3: Media & Web (Priority: LOW)
Entertainment and information gathering.

| Skill | Description | Tools/Libraries | Status |
| :--- | :--- | :--- | :--- |
| **Media Playback** | Play/Pause/Skip music or video. | `playerctl` | ⏳ Planned |
| **YouTube** | Play specific songs/videos on YouTube. | `selenium`, `yt-dlp` | ⏳ Planned |
| **Weather** | Fetch current local weather. | `requests` (OpenWeather) | ⏳ Planned |
| **Web Search** | Perform a Google/DuckDuckGo search. | `webbrowser` | ⏳ Planned |
| **News** | Read top headlines for specific topics. | `feedparser` (RSS) | ⏳ Planned |

---

## 🧠 Category 4: Specialized AI Skills (Priority: ADVANCED)
Leveraging LLMs for deep system interaction.

| Skill | Description | Tools/Libraries | Status |
| :--- | :--- | :--- | :--- |
| **Error Explainer** | Explain the last terminal error code. | `.bash_history` + LLM | ⏳ Planned |
| **Code Writer** | Write and save a script based on prompt. | LLM + FS | ⏳ Planned |
| **Personality** | Contextual conversation and memory. | LLM Vector Store | ⏳ Planned |

---

## 🚀 Next Steps (Phase 1)
1. Implement **System Stats** using `psutil`.
2. Implement **App Launcher** using `subprocess`.
3. Integrate these into `core/brain.py` as local skills.
