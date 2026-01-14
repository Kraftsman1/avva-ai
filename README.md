A.V.V.A - Linux Virtual Assistant

## Setup Instructions

1. **Install prerequisite system requirements (Linux):**
   If you are on a Debian/Ubuntu based system, run:
   ```bash
   sudo apt install python3-venv build-essential portaudio19-dev python3-dev
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration:**
   Copy the example environment file and add your API keys:
   ```bash
   cp .env.example .env
   ```

5. **Run AVVA:**
   ```bash
   python avva.py
   ```
