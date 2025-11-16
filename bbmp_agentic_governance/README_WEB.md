# BBMP Agentic Governance System - BRUTALIST WEB INTERFACE

**Eye-popping brutalist design meets government transparency!**

## 🎨 What You're Getting

A **spectacular brutalist React interface** showcasing the BBMP corruption detection system:

### Design Features:
- **Raw concrete aesthetics** - Grey/black color scheme
- **Heavy borders & shadows** - Brutal box shadows everywhere
- **Monospace fonts** - IBM Plex Mono for that technical feel
- **ASCII art banners** - Terminal-style visualizations
- **No rounded corners** - Pure geometric brutalism
- **Harsh contrasts** - Black on white, green terminals
- **Exposed systems** - See the raw data, nothing hidden

### What It Does:
- **Dashboard** - System stats, agent status, corruption log
- **DPR Analysis** - Validate project proposals in real-time
- **Contractor Database** - Reputation scores, cartel detection
- **Live Demo** - Run scenarios and watch AI agents work

## 🚀 Quick Start

### Option 1: One-Command Launch
```bash
cd /home/user/AIAgents/bbmp_agentic_governance
./START.sh
```

Then open: **http://localhost:3000**

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
python api.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open: **http://localhost:3000**

## 📱 Interface Overview

### Dashboard Tab
- ASCII art system banner
- Real-time agent status
- Impact metrics (₹1,500 Cr savings/year)
- Corruption detection log
- System statistics

### DPR Analysis Tab
- List all project proposals
- Click to see detailed analysis
- Budget variance calculations
- Documentation validation
- Anomaly detection

### Contractors Tab
- Contractor database with reputation scores
- Performance metrics
- Red flag indicators
- Cartel network detection
- Visual score bars

### Live Demo Tab
- 3 demo scenarios:
  1. **Legitimate Project** → APPROVED
  2. **Suspicious Project** → REJECTED (35% budget inflation!)
  3. **Cartel Detection** → REJECTED (shared directors!)
- Click to run
- See AI agents analyze in real-time
- Detailed breakdown of decisions

## 🎨 Brutalist Design Elements

```
┌─────────────────────────────┐
│  ▣ HEAVY BORDERS            │
│  ▦ HARSH SHADOWS            │
│  ◼ RAW CONCRETE             │
│  ◾ MONOSPACE EVERYTHING     │
│  ▪ NO GRADIENTS             │
│  • BLACK & WHITE            │
│  ⚫ GEOMETRIC SHAPES         │
└─────────────────────────────┘
```

**Color Palette:**
- `#0a0a0a` - Deep black
- `#171717` - Dark grey
- `#f5f5f5` - Concrete grey
- `#ffffff` - Pure white
- Accent: Green terminals, yellow warnings, red alerts

**Typography:**
- IBM Plex Mono (primary)
- Arial/Helvetica (fallback)
- All caps headers
- Tight tracking

**Interactions:**
- Instant color inversions (black↔white)
- Heavy box-shadow on hover
- No transitions (except button states)
- Harsh, immediate feedback

## 🛠️ Tech Stack

**Frontend:**
- React 18
- Vite (blazing fast dev server)
- Tailwind CSS (brutalist config)
- No UI libraries - raw components

**Backend:**
- Flask REST API
- BBMP mock data
- Python validation tools

## 📊 What the Demo Shows

### Corruption Caught:
1. **Budget Inflation** - DPR-2025-BOM-002 → 35% over SoR → REJECTED
2. **Duplicate Project** - DPR-2025-BOM-004 → Same road proposed twice → REJECTED
3. **Bid Rigging** - CONT-2024-004 & 005 → Shared director "Rajesh Gupta" → CARTEL DETECTED

### Legitimate Approvals:
1. **Good Project** - DPR-2025-BOM-001 → 245 citizen complaints, proper docs → APPROVED

## 🎤 Perfect for Your Podcast!

**Screen share this and show:**
1. **Brutalist aesthetics** - Eye-catching design
2. **Live Demo tab** - Click scenarios, watch AI work
3. **Dashboard** - ₹1,500 Cr savings counter
4. **Contractor analysis** - Cartel detection with red flags

**Talking points:**
- "This is what government transparency looks like"
- "Brutalist design = honest, raw, no-nonsense"
- "Every decision is visible, auditable, permanent"
- "AI catches what humans miss"

## 🐛 Troubleshooting

**Frontend won't start?**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**Backend errors?**
```bash
cd backend
pip install --upgrade flask flask-cors
python api.py
```

**Port 3000 in use?**
Edit `frontend/vite.config.js` and change `port: 3000` to another port.

**CORS errors?**
Make sure backend is running on port 5000 and frontend on port 3000.

## 🎯 Next Steps

**Want to customize?**
- Edit `frontend/src/index.css` for brutalist styles
- Modify `frontend/tailwind.config.js` for colors
- Update `backend/api.py` for real BBMP data

**Deploy to production?**
- Build: `cd frontend && npm run build`
- Serve the `dist` folder
- Use Gunicorn for Flask backend

## 📜 License

MIT - Build it, fork it, deploy it anywhere!

---

**Built with ❤️ and heavy borders**

*"Form follows function. Corruption follows transparency."*
