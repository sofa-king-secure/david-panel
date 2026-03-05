# MIR // TACTICAL HUD
### Real-Time Situational Awareness Dashboard
*Version 1.0 · david-panel · sofa-king-secure*

---

## WHAT IS THIS

A full-screen tactical dashboard designed for a secondary bar display (1920×440). Displays live weather, RSS news feeds across four categories, a real-time clock with sunrise/sunset, and cycles automatically to a live US radar map. Built as a single HTML file — no server, no install, no dependencies.

---

## FILES

| File | Purpose |
|------|---------|
| `hud_controller.html` | **Launch this.** Cycles between HUD and radar automatically |
| `dashboard.html` | Main HUD — clock, weather, news feeds |
| `radar.html` | Live US NEXRAD radar via Windy embed |
| `LAUNCH_HUD.bat` | One-click launcher — opens in app mode (no browser chrome) |

---

## QUICK START

**Option A — Batch launcher (recommended)**
```
Double-click LAUNCH_HUD.bat
```
Automatically finds Chrome or Edge, opens in borderless app mode on your bar display.

**Option B — Manual**
```
Open hud_controller.html in Chrome or Edge
```

---

## DISPLAY SETUP

The HUD targets a **1920×440 secondary display** (horizontal bar monitor).

To set your display position, edit `LAUNCH_HUD.bat`:
```bat
set "WIN_POS=1920,0"    ← X,Y offset of your bar display
set "WIN_SIZE=1920,440" ← width x height
```

Common positions:
- Bar display **right** of a 1920×1080 primary → `1920,0`
- Bar display **right** of a 2560×1440 primary → `2560,0`
- Bar display **below** a 1920×1080 primary → `0,1080`

Find your exact offset: **Settings → System → Display → drag to match layout**

---

## PANELS

### ◈ CHRONO (Clock)
- 12-hour time with AM/PM
- Day name, date
- GMT/UTC time
- Sunrise ↑ and Sunset ↓ times (pulled from weather API for your location)

### ◈ ENVIRON (Weather)
- **Top half:** Current conditions — temperature, wind, humidity, feels like
- **Bottom half:** 7-day forecast slideshow with animated page transitions
- Click **ENVIRON // [CITY] ▾** to change location
- **Auto-detect:** Browser asks for GPS permission on first load → shows your actual city name

Available preset locations:
- Kalamazoo, MI · Detroit, MI · Lansing, MI
- Chicago, IL · New York, NY · Washington, DC
- AUTO (GPS) — uses browser geolocation

### ◈ US · WORLD NEWS
Live RSS feed — BBC World, NPR, NYT

### ◈ SEC · THREATS
Cybersecurity feed — The Hacker News, CISA alerts

### ◈ IT · TECH
Tech feed — Hacker News, Slashdot, Ars Technica

### ◈ LOCAL (Michigan)
Google News filtered for Kalamazoo and Michigan

---

## RADAR MODE

The HUD automatically cycles to a full-screen live US radar map (Windy NEXRAD composite) and back.

**Default timing:**
- HUD: **5 minutes**
- Radar: **3 minutes**

To change timing, edit `hud_controller.html`:
```javascript
const PAGES = [
  { id: 'frame-hud',   duration: 5 * 60 * 1000 },  // ← change 5 to desired minutes
  { id: 'frame-radar', duration: 3 * 60 * 1000 },  // ← change 3 to desired minutes
];
```

---

## KEYBOARD SHORTCUTS

| Key | Action |
|-----|--------|
| `Space` | Jump to next page immediately |
| `→` (Right Arrow) | Jump to next page immediately |

After a manual switch, the new page's full timer resets — so hitting Space on the radar gives you the full 3 minutes before it auto-returns.

---

## DATA SOURCES

| Data | Source | Refresh |
|------|--------|---------|
| Weather & forecast | Open-Meteo API (free, no key) | Every 10 min |
| Sunrise / Sunset | Open-Meteo daily forecast | With weather |
| City name (GPS) | OpenStreetMap Nominatim | On location change |
| RSS Feeds | Via rss2json proxy | Every 15 min |
| Radar | Windy embed (NEXRAD composite) | Live / animated |

---

## PRIVACY & LOCATION

- GPS location is requested once on load — you can deny and use presets instead
- Location is saved to **sessionStorage only** — cleared when browser closes, never sent anywhere except the weather API
- All data fetched client-side — no backend, no tracking

---

## UPDATING

Push changes with git-manager:
```powershell
python D:\git_manager.py --push --project david-panel
```

---

## TROUBLESHOOTING

**Feeds show empty / loading forever**
- Running as `file://` can cause CORS issues with some proxies
- Open in Chrome with `--allow-file-access-from-files` (the .bat does this automatically)
- The HUD tries 4 different proxy services in sequence — if all fail, check your internet connection

**Weather shows WX ERROR**
- Open-Meteo is free and occasionally has brief outages
- Refreshes automatically every 10 minutes

**Radar shows wrong area**
- The radar is centered on Kalamazoo, MI by default at US zoom level
- Use mouse/touch to pan and zoom within the Windy embed

**Install as App greyed out in Edge/Chrome**
- Expected — PWA install requires HTTPS, `file://` pages can't install as PWA
- The `.bat` launcher is the equivalent — it opens in `--app` mode which removes all browser chrome

**Window appears on wrong monitor**
- Edit `WIN_POS` in `LAUNCH_HUD.bat` to match your display offset

---

*MIR // TACTICAL HUD · sofa-king-secure/david-panel*
