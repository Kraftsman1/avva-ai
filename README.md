# AVVA: The Linux Virtual Assistant

AVVA (Advanced Voice Virtual Assistant) is an open-source, modular virtual assistant designed specifically for Linux. Inspired by assistants like Siri and Cortana, AVVA bridges the gap between natural language interaction and Linux system control.

## 🚀 Vision
The goal of AVVA is to provide a private, extensible, and intelligent assistant that lives in your terminal and controls your OS. By leveraging modern LLMs (OpenAI, Gemini, Ollama) and local Python tools, AVVA can understand complex requests and execute them directly on your system.

## ✨ Features
- **Voice First**: Built-in Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities.
- **LLM Powered**: Support for multiple AI providers (Google Gemini, OpenAI, and local Ollama) to serve as the assistant's "brain".
- **Local Intelligence**: Works out-of-the-box without API keys for basic tasks like time, date, and greetings.
- **OS Integration**: Designed to be extended with "Linux Skills" like opening applications, system monitoring, and media control.
- **Privacy Focused**: Use local models via Ollama to keep your voice and data on your machine.
- **Modular Architecture**: Easily add new "Skills" or swap AI providers.

## 🛠️ Project Structure
- `avva.py`: The main entry point and orchestrator.
- `core/`: Core internal logic (Speech handling, Brain, Config management).
- `skills/`: The "Skills" layer donde you can add system automation scripts.

## 📥 Setup Instructions

### 1. Prerequisite System Requirements (Linux)
AVVA requires Python 3.10+ and a few system libraries for audio handling. On Debian/Ubuntu based systems, run:
```bash
sudo apt install python3-venv build-essential portaudio19-dev python3-dev
```

### 2. Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
AVVA uses environment variables for configuration. Copy the template and edit it with your settings/API keys:
```bash
cp .env.example .env
```

### 5. Run AVVA
```bash
python avva.py
```

## 🤝 Contributing
AVVA is built to be extensible. Feel free to add new skills in the `skills/` directory or improve the core logic!
