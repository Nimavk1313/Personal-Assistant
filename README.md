## Personal Assistant (Backend + System-wide)

This project provides:
- A FastAPI backend with REST endpoints for chat, live screen, and web search.
- A system-wide Windows helper (`assistant_daemon.py`) with global hotkeys and screen OCR.
- A simple web frontend for browser-based interaction.

### Requirements
- **Windows**: Windows 10/11
- **macOS**: macOS 10.15+ (Catalina or later)
- **Linux**: Most modern distributions (limited window management features)
- Python 3.10+
- A Cerebras API key

### Platform-Specific Setup

#### Windows
- Tesseract OCR will be automatically detected from common installation paths
- Full window management and screen capture support

#### macOS
- Install Tesseract OCR via Homebrew: `brew install tesseract`
- The app will automatically install required macOS frameworks (AppKit, Quartz)
- Grant necessary permissions for screen recording and accessibility when prompted

#### Linux
- Install Tesseract OCR via package manager: `sudo apt install tesseract-ocr` (Ubuntu/Debian)
- Limited window management features available

### Install
1. Clone or copy this folder.
2. Create a virtual environment and install deps:

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
3. Create a `.env` in the project root:
```
CEREBRAS_API_KEY=YOUR_KEY
```
Optional environment overrides:
```
ASSISTANT_MODEL=llama3.1-8b
ASSISTANT_TEMPERATURE=0.2
ASSISTANT_TOP_P=0.9
```

### Run the backend server

**Windows:**
```bash
.venv\Scripts\activate
python backend.py
```

**macOS/Linux:**
```bash
source .venv/bin/activate
python backend.py
```
Then open http://localhost:8000 in your browser.

Features:
- REST API with chat, live screen toggle, status, and transcript endpoints
- Web frontend with real-time status and transcript updates
- Live screen OCR with continuous background capture
- Web search integration
- System-wide hotkeys via daemon

### Run the system-wide assistant

**Windows:**
```bash
.venv\Scripts\activate
python assistant_daemon.py
```

**macOS/Linux:**
```bash
source .venv/bin/activate
python assistant_daemon.py
```

Note: On macOS, you may need to grant accessibility permissions when prompted.

Hotkeys:
- Ctrl+Alt+P: open prompt anywhere
- Ctrl+Alt+O: toggle OCR (screen-aware answers)
- Ctrl+Alt+R: toggle Live Screen (continuous in-memory OCR)

### API Endpoints
- `POST /chat` - Send message with optional OCR/web search
- `POST /live/toggle` - Toggle live screen capture
- `GET /status` - Get system status and statistics
- `GET /transcript` - Get recent OCR transcript
- `GET /` - Web frontend

Notes:
- For OCR, install Tesseract OCR engine if needed and ensure `pytesseract` can find it. On Windows, install from `https://github.com/UB-Mannheim/tesseract/wiki` and add it to PATH.
- If screen capture fails, ensure `mss` and `pillow` are installed and you have permission to capture the screen.
- Live Screen does not save recordings to disk; it continuously OCRs frames and keeps a short in-memory transcript only.




