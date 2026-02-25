# DTMB-MCS TACTICAL HUD — README
## Ultra-Wide 1920×440 Dashboard · Portable USB Edition

---

### CONTENTS
```
USB Drive:\HUD\
  ├── dashboard.html    ← The entire dashboard (single file)
  ├── LAUNCH_HUD.bat    ← 1-click launcher
  └── README.txt        ← This file
```

---

### QUICK START (30 seconds)

1. Plug in your 1920×440 bar display via HDMI + USB-C (power)
2. Windows should detect it as a secondary monitor
3. Double-click **LAUNCH_HUD.bat**
4. Drag the Chrome window to your bar display
5. Press **F11** → fullscreen

---

### ONE-TIME SETUP: Auto-Position on Launch

To have the HUD snap to your bar display automatically without dragging:

1. Open **LAUNCH_HUD.bat** in Notepad
2. Find the line: `set "WIN_POS=1920,0"`
3. Change the coordinates to match your display layout:

**Finding your coordinates:**
- Right-click Desktop → **Display Settings**
- Click **Identify** to see monitor numbers
- Drag monitors to match physical layout
- The bar display's top-left pixel position = your WIN_POS value

**Common scenarios:**
| Bar Display Location | WIN_POS value |
|---------------------|---------------|
| Right of 1920×1080  | `1920,0`      |
| Right of 2560×1440  | `2560,0`      |
| Below 1920×1080     | `0,1080`      |
| Left of primary     | `-1920,0`     |

---

### DATA SOURCES (all free, no API key required)

| Panel | Source | Refresh |
|-------|--------|---------|
| Weather | open-meteo.com (free, no key) | 10 min |
| US/World News | NPR + NY Times RSS | 5 min |
| Security/Threats | The Hacker News + BleepingComputer + Krebs | 5 min |
| IT/Tech | Ars Technica + Wired | 5 min |
| Local MI | MLive Kalamazoo + WoodTV8 Grand Rapids | 5 min |

**RSS feeds used (all public, no scraping):**
- https://feeds.npr.org/1001/rss.xml
- https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml
- https://feeds.feedburner.com/TheHackersNews
- https://www.bleepingcomputer.com/feed/
- https://krebsonsecurity.com/feed/
- https://feeds.arstechnica.com/arstechnica/index
- https://www.wired.com/feed/rss
- https://www.mlive.com/arc/outbound/rss/kalamazoo/
- https://www.woodtv.com/feed/

**RSS Proxy:** rss2json.com (free tier, 10,000 req/day — more than sufficient)

---

### SWAPPING IN CUSTOM RSS FEEDS

Edit `dashboard.html` in Notepad. Find the `const FEEDS = {` section (~line 280).
Each feed category has a `urls: [ ]` array — add or replace any RSS URL there.

---

### REQUIREMENTS

- Windows 10/11
- Google Chrome or Microsoft Edge (both portable-compatible)
- Internet connection (for live data)
- Machine running at 100% OS display scaling (recommended)

---

### TROUBLESHOOTING

**"Feeds show LOADING forever"**
→ Check internet connection. Some corporate proxies block rss2json.com.
→ Try opening dashboard.html directly in Chrome first.

**"Weather won't load"**
→ open-meteo.com is occasionally down. Retries every 10 minutes automatically.

**"Window won't fit the display"**
→ Ensure OS display scaling is 100% for the bar display.
→ Right-click bar display in Display Settings → Scale = 100%.

**"Chrome not found"**
→ Edit LAUNCH_HUD.bat and set CHROME_EXE manually to your Chrome path.
→ Or install Chrome Portable on the same USB drive and update the path.

---

### PORTABILITY NOTES

This dashboard requires NO installation. Everything runs from the USB drive.
The only requirement on the host machine is a Chromium-based browser (Chrome/Edge),
which is pre-installed on virtually all Windows 10/11 machines.

If you need 100% offline capability:
- The weather panel requires internet (Open-Meteo API)
- RSS feeds require internet
- The clock/layout works fully offline

---

*DTMB-MCS Tactical HUD · Kalamazoo, MI*
