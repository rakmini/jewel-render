# JewelRender Setup Guide

## Development Environment

### Machine
- **Mac Mini M4** (hostname: `Raks-Mac-mini`)
- **macOS 14.x or later** (Sonoma or newer recommended)

### Required Software

#### 1. OpenAI API Key
- **Sign up**: platform.openai.com (separate from ChatGPT subscription)
- **Add credits**: Pay-as-you-go billing
- **Get API key**: Settings > API Keys > Create new secret key
- **Note**: ChatGPT Plus subscription does NOT include API access — they're billed separately

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

#### 2. Configure OpenAI API

Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Test your API key**:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer sk-your-key-here" | python3 -m json.tool
```

#### 3. Run Backend

```bash
cd jewelrender/backend
source venv/bin/activate
python src/main.py

# Server runs at http://0.0.0.0:5000
# Access from Mac: http://localhost:5000
# Access from iPhone: http://<mac-mini-ip>:5000
```

#### 4. Test Connection

Once the server is running:
```bash
# Health check
curl http://localhost:5000/health | python3 -m json.tool

# Test OpenAI connection
curl -X POST http://localhost:5000/api/settings/test-connection | python3 -m json.tool
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

### AI Models Used

| Model | Purpose | When it runs | Cost |
|-------|---------|-------------|------|
| GPT-4.1-mini | Brain — vision analysis, tagging, quality | Every image | ~$0.003/image |
| GPT Image 1.5 | Stills — generate & edit jewelry photos | On render | $0.02-$0.20/image |
| Sora 2 | Video — 360 rotation loops | On video render | Higher per-gen |

All three models use the same API key and bill to the same OpenAI Platform account.

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
│   │   ├── openai_client.py     # OpenAI API client (generate, edit, video)
│   │   ├── brain.py             # AI brain (GPT-4.1-mini vision analysis)
│   │   ├── utils/
│   │   │   └── image.py         # Local image processing (Pillow/OpenCV)
│   │   ├── models.py            # Pydantic data models
│   │   └── config.py            # Configuration
│   ├── tests/
│   ├── requirements.txt
│   └── .env                     # OpenAI API key (not committed)
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

- [ ] OpenAI API key set in `.env`
- [ ] `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"` returns models
- [ ] Backend starts: `python src/main.py`
- [ ] Health check passes: `curl http://localhost:5000/health`
- [ ] OpenAI connection test: `POST /api/settings/test-connection` returns `connected: true`
- [ ] Frontend loads: `http://localhost:5000`
- [ ] iPhone can reach: `http://<mac-ip>:5000`
- [ ] Preset data directory exists: `~/JewelRender/`
- [ ] No errors in server console

### Troubleshooting

**OpenAI API Key Issues**
- Ensure key starts with `sk-`
- Check you have API credits at platform.openai.com/account/billing
- ChatGPT Plus does NOT give API access — they're separate billing

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

1. Get OpenAI API key from platform.openai.com
2. Set up backend with `pip install -r requirements.txt`
3. Configure `.env` with API key
4. Test connection via `/api/settings/test-connection`
5. Implement render endpoints (Generate, Edit, Video)
6. Wire AI brain to analyze every image on entry
7. Implement file persistence (presets, RIL, feedback)
8. Wire frontend controls to backend API

See `docs/API.md` for endpoint specifications.
