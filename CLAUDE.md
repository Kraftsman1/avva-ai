# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AVVA (Advanced Voice Virtual Assistant) is an open-source, modular Linux virtual assistant with voice interaction, multi-LLM support, and system integration capabilities. The project consists of:

- **Python Core** (`core/`, `avva_core.py`): Headless assistant engine with STT/TTS, LLM orchestration, and skill execution
- **Tauri Desktop App** (`ui-web/`): Nuxt 4 + Vue 3 frontend wrapped in a Rust Tauri shell
- **WebSocket Bridge**: Real-time communication between Python core (sidecar) and Tauri UI

## Build Commands

### Full Application Build
```bash
./build.sh
```
This orchestrates the complete build pipeline:
1. Compiles Python core with PyInstaller to `ui-web/src-tauri/sidecars/avva-core-x86_64-unknown-linux-gnu`
2. Bundles TTS assets from `bin/` to `ui-web/src-tauri/sidecars/bin/`
3. Builds Nuxt frontend (`npm run generate`)
4. Compiles Tauri native app (Rust)

Final binary: `ui-web/src-tauri/target/release/avva`

### Python Core Only
```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run headless core
python avva_core.py
```

### Web UI Development
```bash
cd ui-web
npm install
npm run dev  # Nuxt dev server on localhost:3000
```

### Tauri Development
```bash
cd ui-web
npx tauri dev  # Launches both Nuxt dev server and Tauri window
```

### Flatpak Package
```bash
# After running ./build.sh
flatpak-builder build-dir flatpak/com.kraftsman.AVA.yaml
```

## Architecture

### 1. Python Core (Headless Assistant Engine)

**Entry Points:**
- `avva.py`: Simple CLI voice loop (legacy)
- `avva_core.py`: Headless core with WebSocket server for UI integration

**Core Components:**

- **`core/assistant.py`**: Main orchestration layer
  - Manages voice loop, state machine (idle/listening/thinking/speaking)
  - Event emission system for UI updates
  - Processes commands and coordinates brain/TTS responses

- **`core/brain.py`** + **`core/brain_manager.py`**: LLM orchestration
  - Manages multiple Brain providers with fallback logic
  - Intent detection, skill routing, and context filtering
  - Supports local (Ollama, LM Studio, Rules) and cloud (OpenAI, Google Gemini, Claude) providers

- **`core/skill_manager.py`**: Plugin system for OS integration
  - Auto-discovers skills from `skills/` directory via `manifest.json`
  - Intent mapping (regex + static phrases) to Python functions
  - Permission system with persistent user approval

- **`core/websocket_server.py`**: Bridge to Tauri UI
  - Broadcasts assistant events (state changes, commands, responses)
  - Handles incoming UI commands
  - Default port: 8765

**Brain System (`core/brains/`):**
All Brain providers implement `core/brain_interface.py`:
- `BaseBrain` class with standardized interface
- Health checks, capability discovery, privacy levels
- Available providers: Rules (offline fallback), Ollama, LM Studio, Google Gemini, OpenAI, Claude
- See `core/brains/README.md` for detailed Brain implementation guide

**Skills System (`skills/`):**
Each skill is a folder with:
- `manifest.json`: Defines ID, intents (static phrases + regex), permissions, entry point
- `main.py`: Python module exposing functions called by intents
- Example: `skills/clock/` provides `get_time()` and `get_date()`

### 2. Tauri Desktop Application

**Structure:**
- `ui-web/app/`: Nuxt 4 application (Vue 3 + TypeScript)
  - `pages/index.vue`: Main chat interface
  - `pages/settings.vue`: Brain configuration UI
  - `components/ChatArea.vue`: Voice interaction and chat display
- `ui-web/src-tauri/src/`: Rust Tauri application
  - Manages Python sidecar lifecycle
  - Provides native window and OS integration

**Communication Flow:**
1. Tauri frontend connects to WebSocket (localhost:8765)
2. User input sent via WebSocket to Python core
3. Core processes via Brain + Skills
4. Events broadcast back to UI (state changes, responses)

**Sidecar Configuration:**
The Python core is bundled as a Tauri sidecar (see `tauri.conf.json`):
- Binary: `sidecars/avva-core-x86_64-unknown-linux-gnu`
- Assets: `sidecars/bin/` contains Piper TTS models

### 3. Configuration and Environment

**Environment Variables (`.env`):**
- `AVVA_NAME`: Assistant name (default: "Ava")
- `AVVA_WAKE_WORD`: Voice activation phrase
- `LLM_PROVIDER`: google | openai | ollama | claude | lmstudio
- `LLM_API_KEY`: API key for cloud providers
- `LLM_MODEL`: Model identifier (e.g., gemini-1.5-flash, gpt-4o, llama3)
- `TTS_ENGINE`: gtts | piper | openai | elevenlabs
- `OLLAMA_HOST`: Ollama server URL (default: http://localhost:11434)

**Brain Persistence:**
Active Brain configuration stored in `core/persistence.py` using JSON files.

## Development Workflow

### Adding a New Skill
1. Create folder in `skills/` (e.g., `skills/weather/`)
2. Add `manifest.json` with intents and permissions
3. Create `main.py` with callable functions
4. Functions return strings (spoken responses)

### Adding a New Brain Provider
1. Create `core/brains/my_brain.py` extending `BaseBrain`
2. Implement required methods: `get_capabilities()`, `health_check()`, `execute()`
3. Register in `core/brain.py` `_restore_brain()` method
4. Add UI support in `ui-web/app/pages/settings.vue`

### Testing Core Independently
```bash
source venv/bin/activate
python avva_core.py
# Type commands directly or use voice input
```

### Debugging WebSocket Communication
WebSocket events follow this schema:
```json
{
  "type": "assistant.state|assistant.command|assistant.response",
  "payload": { "state": "...", "command": "...", "text": "..." },
  "timestamp": "ISO-8601"
}
```

## Key Design Patterns

1. **Event-Driven Architecture**: Assistant emits events consumed by UI and callbacks
2. **Provider Pattern**: Brains and Skills use plugin-style registration
3. **Fallback Chain**: Brain Manager supports primary → fallback → rules-based brain
4. **Headless Core**: Python engine runs independently; UI is optional
5. **Permission System**: Skills require user approval for sensitive operations (persisted)

## Planning & Documentation

### PRD Validation Report
See `PRD_VALIDATION_REPORT.md` for detailed analysis of implementation vs. PRD specifications:
- WebSocket protocol compliance
- Event type coverage (Core ↔ UI)
- Screen state implementation
- Known gaps and critical issues
- **Compliance Score**: 75/100

**Critical Gaps**:
- ❌ No streaming response support
- ❌ No correlation IDs in protocol
- ❌ No structured error handling (`core.error` event)
- ❌ Voice input UI controls missing

### Product Roadmap
See `PRODUCT_ROADMAP.md` for strategic feature planning (12-month timeline):
- **P0 (Immediate)**: Fix PRD gaps, add conversation memory
- **P1 (Short-term)**: Multi-step workflows, vision support, proactive suggestions
- **P2 (Short-term)**: Deep Linux integration (dev tools, file system, sysadmin)
- **P3 (Long-term)**: Skill/Brain marketplaces, REST API, developer SDK
- **P4 (Long-term)**: RAG, multi-Brain orchestration, autonomous agent mode

40+ features planned with implementation details, effort estimates, and acceptance criteria.

## Important Notes

- The Python core is compiled with PyInstaller for distribution but runs as standard Python during development
- TTS assets (Piper models in `bin/`) must be bundled with the sidecar
- Brain configurations are stored persistently and survive restarts
- The WebSocket server runs on a background thread in the Python core
- Tauri manages the sidecar process lifecycle (start/stop/restart)
- **Current version**: v0.1.0 (MVP with known gaps - see PRD validation report)
