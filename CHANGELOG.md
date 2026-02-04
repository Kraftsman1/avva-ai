# Changelog

All notable changes to the AVVA project will be documented in this file.

## [Unreleased] - 2026-01-22
### Added
- **Modern Web UI (Nuxt 4 + Tauri)**: Complete frontend rewrite using **Nuxt 4** and **Tauri** for a native desktop experience.
  - **Cyberpunk Aesthetic**: High-fidelity dark mode UI with telemetry visualizations, glassmorphism, and animated components.
  - **Real-time Telemetry**: WebSocket integration displaying live CPU, RAM, and VRAM usage from the Python core.
  - **Visual Thinking Mode**: 
    - **Header Status Indicator**: Central status pulse (Idle, Listening, Thinking, Speaking) for immediate state feedback.
    - **Chat Bubbles**: Dynamic "Thinking..." bubbles with typing animations that appear during LLM inference.
- **WebSocket Bridge**: Bidirectional real-time communication layer (`core/websocket_server.py`) connecting the Python backend with the Vue frontend.
- **Active Model Sync**: The UI now automatically detects and displays the specific active model name (e.g., "llama3.2") from the configured Brain.

### Changed
- **UI Architecture**: Moved from simple HTML/JS interfaces to a robust component-based architecture using Vue 3 and Shadcn-vue.
- **Brain Integration**: Brains now expose granular `config_data` to the web client for accurate model reporting.

## [Unreleased] - 2026-01-18
### Added
- **Configurable LLM Brains System**: Complete architectural overhaul of LLM integration.
  - **Brain Interface**: Standardized interface for all LLM providers with capability system, privacy levels, and health checks.
  - **Brain Manager**: Central orchestrator for Brain registration, selection, and fallback handling.
  - **Brain Providers**: 
    - Rules Brain (deterministic fallback, no LLM required)
    - Ollama Brain (local LLM with JSON mode and vision support)
    - LM Studio Brain (local OpenAI-compatible API)
    - Google Gemini Brain (cloud, tool calling, vision, cost estimation)
    - OpenAI Brain (cloud, JSON mode, streaming, usage tracking)
    - Claude Brain (cloud, tool calling, vision, cost tracking)
  - **Context Filtering**: Privacy-aware context redaction based on Brain privacy level (local/trusted/external cloud).
  - **Brain Selection Logic**: Context-aware routing (sensitive requests → local Brains), automatic fallback chain.
  - **Database Schema**: New tables for Brain configs, capabilities, and usage tracking.
  - **Legacy Migration**: Automatic migration from old `config.py` LLM settings to new Brain system.
  - **Backward Compatibility**: Refactored `brain.py` as facade maintaining existing API.

### Changed
- Refactored `core/brain.py` to delegate to new Brain Manager system.
- Extended `core/persistence.py` with Brain configuration methods and usage tracking.
- Updated `requirements.txt` to include `anthropic` package for Claude support.

## [Unreleased] - 2026-01-15
### Added
- **Global Permissions**: Implemented a scope-based permission system (`system.read`, `audio.record`, `ai.generate`).
- **LLM Access Control**: Added a "Privacy Mode" to disable LLM inference (`ai.generate` scope).
- **Dynamic Configuration**: New "AI Brain" settings tab to hot-swap providers (Ollama, Google, OpenAI), models, and API keys.
- **Persistent Settings**: Configuration is now saved to `~/.config/avva/config.json`.
- **UI Polish**: 
  - Dark mode support for Settings Dialog.
  - Improved contrast for inputs and buttons.
  - Consolidated "Security" and "AI Brain" into a tabbed interface.
- **Onboarding**: First-run prompts for Microphone and AI access.

### Changed
- Refactored `PermissionSettingsDialog` into a tabbed `SettingsDialog`.
- Normalized permission keys to human-readable labels in the UI.
- Updated `core/brain.py` to support hot-reloading of LLM backends.

## [0.2.0] - 2026-01-15

### Added
- **Plugin Architecture (V2)**: Transitioned to a folder-based plugin system. Each skill now resides in its own directory with a `manifest.json` for discovery and permissions.
- **Parametric Intent Router**: Implemented a regex-capable local router in `SkillManager`. It can now capture variables (e.g., app names) from natural language and inject them into tool calls.
- **Standardized Skill Schema**: Introduced a structured JSON output schema for skills, allowing for consistent handling of success, ambiguity, and errors.
- **RapidFuzz Integration**: Switched to `rapidfuzz` for high-performance fuzzy matching in the App Launcher and intent discovery.
- **Production-Grade App Launcher**: 
    - Full `.desktop` file parsing for `Exec`, `Categories`, and `Keywords`.
    - Native `Terminal=true` handling for terminal-based applications.
    - Automatic cleaning of Freedesktop field codes (e.g., `%U`, `%f`).
- **Execution Transparency**: Added real-time command/response logging to `avva.py` for better user visibility.

### Changed
- **Tiered Intent Pipeline**: Refactored the Brain and SkillManager to support a three-tier system: static match → parametric regex → LLM fallback.
- **Skill Manifests**: Updated all core skills (Clock, System Stats, App Launcher) to use the new dynamic intent format.
- **Brain Refactor**: The Brain now dynamically generates tool descriptions for the LLM based on loaded plugin metadata.

### Fixed
- **App Launching on COSMIC**: Resolved an issue where COSMIC-specific applications (like `cosmic-term`) wouldn't launch due to lack of terminal awareness.
- **Fuzzy Collisions**: Tuned regex patterns to prevent greedy matches between specialized skills.

## [0.1.0] - 2026-01-14

### Added
- **Modular Project Structure**: Created `core/` and `skills/` directories to separate concerns.
- **Environment Configuration**: Added support for `.env` files via `python-dotenv` to manage API keys and settings.
- **Centralized Config**: New `core/config.py` for global application settings.
- **Multi-engine TTS Provider**: Refactored `core/tts.py` to support multiple backends:
    - **Piper**: High-quality local neural TTS (fluid and fast).
    - **OpenAI/ElevenLabs**: Industry-leading cloud TTS for human-like voices.
    - **gTTS**: Baseline fallback.
- **System Stats Skill**: New modular skill in `skills/system_stats.py` that reports CPU, RAM, and Disk usage via `psutil`.
- **Isolated Speech Modules**:
    - `core/stt.py`: Handles microphone input and speech recognition.
    - `core/tts.py`: Handles text-to-speech synthesis and playback.
- **Brain Framework**: Introduced `core/brain.py` as a central logic processor with **Local Intent Fallback** (works without API keys for time, date, and basic queries).
- **Template Config**: Added `.env.example` for easy project setup.

### Changed
- **`avva.py` Refactor**: Transformed from a monolithic script to a lean entry point that orchestrates core modules.
- **Enhanced Playback**: Improved TTS reliability in `core/tts.py` with better mixer management.
- **Updated Dependencies**: Added `python-dotenv` to `requirements.txt`.

### Fixed
- **Greeting Logic**: Resolved a bug where any input would trigger a greeting due to incorrect boolean evaluation.
