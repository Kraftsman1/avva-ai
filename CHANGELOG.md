# Changelog

All notable changes to the AVVA project will be documented in this file.

## [Unreleased] - 2026-01-14

### Added
- **Modular Project Structure**: Created `core/` and `skills/` directories to separate concerns.
- **Environment Configuration**: Added support for `.env` files via `python-dotenv` to manage API keys and settings.
- **Centralized Config**: New `core/config.py` for global application settings.
- **Isolated Speech Modules**:
    - `core/stt.py`: Handles microphone input and speech recognition.
    - `core/tts.py`: Handles text-to-speech synthesis and playback.
- **Brain Framework**: Introduced `core/brain.py` as a central logic processor, ready for LLM integration.
- **Template Config**: Added `.env.example` for easy project setup.

### Changed
- **`avva.py` Refactor**: Transformed from a monolithic script to a lean entry point that orchestrates core modules.
- **Enhanced Playback**: Improved TTS reliability in `core/tts.py` with better mixer management.
- **Updated Dependencies**: Added `python-dotenv` to `requirements.txt`.

### Fixed
- **Greeting Logic**: Resolved a bug where any input would trigger a greeting due to incorrect boolean evaluation.
