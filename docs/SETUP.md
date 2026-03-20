# JewelRender Setup Guide

## Development Environment

### Machine
- **Mac Mini M4** (hostname: `Raks-Mac-mini`)
- **macOS 14.x or later** (Sonoma or newer recommended)

### Required Software

#### 1. ComfyUI
- **Version**: Latest stable
- **Location**: Running on same Mac Mini
- **Access**: `127.0.0.1:8188`
- **Checkpoint**: `sd_xl_base_1.0.safetensors`
- **Model Support**: Must support Apple Silicon (M4 compatible)

**Installation**:
```bash
# If not already installed, follow ComfyUI setup for Mac:
# https://github.com/comfyanonymous/ComfyUI

# Ensure checkpoint is in:
# ~/ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors
```

**Test Connection**:
```bash
curl http://127.0.0.1:8188/api/
# Should return JSON response
```

#### 2. Python 3.10+
```bash
python3 --version
# Should be 3.10.x or higher
```

#### 3. Claude Code (Optional but Recommended)
- Version: 2.1.80+
- Used for development and testing
- Installed via native installer on Mac

#### 4. Git
```bash
git --version
```

### Frontend Setup

1. **Copy existing HTML file**
   ```bash
   cp [path-to-existing]/JewelRender.html jewelrender/frontend/src/index.html
   ```

2. **Create folder structure**
   ```bash
   mkdir -p jewelrender/frontend/src/{css,js,assets/{icons,images}}
   mkdir -p jewelrender/frontend/public
   ```

3. **Extract CSS/JS** (when splitting single file):
   - All CSS currently inline in HTML
   - All JS currently inline in HTML
   - These can stay as-is for MVP, or split into separate files for maintainability

4. **Serve frontend** (simple HTTP server for testing):
   ```bash
   cd jewelrender/frontend
   python3 -m http.server 5000
   # Open http://localhost:5000/src/index.html
   ```

### Backend Setup

#### 1. Create Python Environment

```bash
cd jewelrender/backend

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Install Dependencies

**requirements.txt** should include:
- fastapi — web framework
- uvicorn — ASGI server
- requests — HTTP client for ComfyUI
- pillow — image processing
- python-dotenv — configuration
- pydantic — data validation

```bash
pip install fastapi uvicorn requests pillow python-dotenv pydantic
```

#### 3. Configure Backend

Create `backend/config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

# ComfyUI Connection
COMFYUI_HOST = os.getenv('COMFYUI_HOST', '127.0.0.1')
COMFYUI_PORT = os.getenv('COMFYUI_PORT', '8188')
COMFYUI_URL = f'http://{COMFYUI_HOST}:{COMFYUI_PORT}'

# Output Settings
OUTPUT_WIDTH = 1170
OUTPUT_HEIGHT = 2532
JPEG_QUALITY = 95

# Storage
USER_DATA_DIR = os.path.expanduser('~/JewelRender')
PRESETS_DIR = os.path.join(USER_DATA_DIR, 'presets')
EXPORTS_DIR = os.path.join(USER_DATA_DIR, 'exports')

# Create dirs if not exist
os.makedirs(PRESETS_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)
```

Create `.env` file:
```
COMFYUI_HOST=127.0.0.1
COMFYUI_PORT=8188
```

#### 4. Create Entry Point

Create `backend/src/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="JewelRender API")

# CORS for local + Tailscale access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
app.mount("/", StaticFiles(directory="../../frontend/src", html=True), name="static")

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
```

#### 5. Run Backend

```bash
cd jewelrender/backend
source venv/bin/activate
python src/main.py

# Server runs at http://0.0.0.0:5000
# Access from Mac: http://localhost:5000
# Access from iPhone: http://<mac-mini-ip>:5000
```

### iPhone Remote Access

#### Option 1: Local Network

1. **Ensure same Wi-Fi**
   - Mac Mini on Wi-Fi
   - iPhone on same Wi-Fi network

2. **Find Mac Mini IP**
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   # e.g., 192.168.1.100
   ```

3. **Open on iPhone**
   - Safari: `http://192.168.1.100:5000`

#### Option 2: Tailscale (Remote Access)

1. **Install Tailscale on Mac**
   ```bash
   brew install tailscale
   tailscale up
   ```

2. **Install Tailscale on iPhone**
   - App Store: Tailscale
   - Sign in with same account

3. **Open on iPhone**
   - Find Mac's Tailscale IP (e.g., 100.x.x.x)
   - Safari: `http://100.x.x.x:5000`

### ComfyUI Workflow Integration

The backend needs to communicate with ComfyUI via HTTP API.

#### Key Endpoints

- `GET /api/` — Health check
- `POST /prompt` — Queue workflow for execution
- `GET /history/{prompt_id}` — Check workflow status/results

#### Example Workflow (Image Generation)

```json
{
  "1": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {
      "ckpt_name": "sd_xl_base_1.0.safetensors"
    }
  },
  "2": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "beautiful jewelry on white background",
      "clip": ["1", 0]
    }
  },
  ...
}
```

See `docs/API.md` for complete workflow examples.

### File Structure After Setup

```
jewelrender/
├── frontend/
│   ├── src/
│   │   ├── index.html          # Main app
│   │   ├── css/                 # Stylesheets (when split)
│   │   ├── js/                  # Scripts (when split)
│   │   └── assets/
│   ├── public/
│   └── package.json (optional, if using npm)
├── backend/
│   ├── venv/                    # Python virtual environment
│   ├── src/
│   │   ├── main.py              # FastAPI app
│   │   ├── comfyui/
│   │   │   ├── client.py
│   │   │   └── workflows.py
│   │   ├── utils/
│   │   ├── models.py
│   │   └── config.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── FEATURES.md
│   ├── SETUP.md (this file)
│   └── PROGRESS.md
├── config/
│   ├── presets.json
│   └── settings.json
└── .github/
    └── workflows/
```

### Data Directory (User Machine)

```
~/JewelRender/
├── presets/
│   ├── cool-blue/
│   │   ├── config.json
│   │   ├── library/
│   │   ├── renders/
│   │   └── feedback.json
│   ├── white-retail/
│   └── yashica-film/
├── exports/
└── feedback_log.json
```

### Testing Checklist

- [ ] ComfyUI running at `127.0.0.1:8188`
- [ ] `curl http://127.0.0.1:8188/api/` returns JSON
- [ ] Backend starts: `python src/main.py`
- [ ] Frontend loads: `http://localhost:5000`
- [ ] iPhone can reach: `http://<mac-ip>:5000`
- [ ] Preset data directory exists: `~/JewelRender/`
- [ ] No errors in server console

### Troubleshooting

**ComfyUI Connection Fails**
- Check ComfyUI is running: `ps aux | grep comfy`
- Check port: `lsof -i :8188`
- Verify checkpoint exists

**Python Module Errors**
- Ensure venv activated: `source venv/bin/activate`
- Reinstall requirements: `pip install --upgrade -r requirements.txt`

**iPhone Can't Reach Mac**
- Check same Wi-Fi network
- Check firewall: System Preferences > Security & Privacy
- Try Tailscale as fallback

**Port Already in Use**
- Kill process: `lsof -i :5000` then `kill -9 <PID>`
- Or use different port: `uvicorn main:app --port 5001`

---

## Next Steps

1. Set up backend with FastAPI
2. Create ComfyUI client in `backend/src/comfyui/`
3. Implement API endpoints for each mode (Edit, Generate, 360 Video)
4. Test with ComfyUI workflows
5. Add image processing utilities
6. Implement file persistence (presets, RIL, feedback)
7. Wire frontend controls to backend API

See `docs/API.md` for endpoint specifications.
