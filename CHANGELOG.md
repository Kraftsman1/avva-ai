# Changelog

All notable changes to the AVVA project will be documented in this file.

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
