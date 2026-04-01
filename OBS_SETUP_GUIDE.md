# OBS Studio Setup Guide for AuthClear Demo Video

**Purpose:** Complete configuration for recording 1920x1080 @ 30fps demo video under 3 minutes

---

## 📥 Installation

**Download:** https://obsproject.com/download
**Version:** OBS Studio 30.0+ (latest stable)
**Platform:** Windows 11

---

## ⚙️ OBS Settings Configuration

### Settings → Output

```
Output Mode: Advanced
Encoder: x264 (software - best quality)
Rate Control: CBR
Bitrate: 5000 Kbps
Keyframe Interval: 2
CPU Usage Preset: veryfast (balance quality/performance)
Profile: high
Tune: (none)
```

### Settings → Video

```
Base (Canvas) Resolution: 1920x1080
Output (Scaled) Resolution: 1920x1080
Downscale Filter: Lanczos (best quality)
FPS: 30
```

### Settings → Audio

```
Sample Rate: 48 kHz
Channels: Stereo
Desktop Audio Device: Default (for system sounds if needed)
Mic/Auxiliary Audio Device: Your microphone
```

### Settings → Advanced

```
Process Priority: High
Color Format: NV12
Color Space: 709
Color Range: Partial
```

---

## 🎬 Scene Configuration

### Scene 1: Title Card

**Sources:**
1. **Image Source:** `video_assets/title_card.html` (rendered as PNG)
   - Right-click → Transform → Fit to Screen
   - Transition: Fade (500ms)

**Duration:** 5 seconds

---

### Scene 2: Architecture Diagram

**Sources:**
1. **Image Source:** `video_assets/architecture_diagram.html` (rendered as PNG)
   - Right-click → Transform → Fit to Screen
   - Transition: Slide from Right (300ms)

**Duration:** 20 seconds

**Text Overlays (add with Text GDI+):**
- Font: Segoe UI Bold, 48pt
- Color: #ffd700 (gold)
- Position: Top center
- Text: "MCP Server - FHIR Terminology Engine" (appears at 0:32)
- Text: "A2A Agent - Prior Auth Copilot" (appears at 0:42)

---

### Scene 3: Terminal Demo

**Sources:**
1. **Window Capture:** PowerShell or Windows Terminal
   - Select window: "Windows PowerShell" or "Windows Terminal"
   - Capture Method: Windows 10 (1903 and up)
   - Check "Capture Cursor"
   - Right-click → Transform → Stretch to Screen

**Terminal Setup Before Recording:**
```powershell
# Set terminal size
$Host.UI.RawUI.WindowSize = New-Object Management.Automation.Host.Size(120, 30)

# Set font (if using Windows Terminal)
# Settings → Profiles → Defaults → Appearance
# Font: Cascadia Code, Size: 16pt
# Color scheme: One Half Dark
```

**Duration:** 40 seconds

---

### Scene 4: Split Screen (VS Code + Terminal)

**Sources:**
1. **Window Capture - VS Code:** (Left 50%)
   - Add Source → Window Capture → "Visual Studio Code"
   - Right-click → Transform → Edit Transform
   - Position: X=0, Y=0
   - Size: Width=960px, Height=1080px

2. **Window Capture - Terminal:** (Right 50%)
   - Add Source → Window Capture → "Windows PowerShell"
   - Right-click → Transform → Edit Transform
   - Position: X=960, Y=0
   - Size: Width=960px, Height=1080px

**Duration:** 60 seconds

**Alternative:** Use Browser Source if showing JSON in browser
```
URL: file:///c:/Users/user/Desktop/devpost/demo_output.html
Width: 960
Height: 1080
```

---

### Scene 5: Compliance + ROI

**Sources:**
1. **Browser Source - Compliance:** (Left 50%)
   - URL: `file:///c:/Users/user/Desktop/devpost/video_assets/compliance_badges.html`
   - Width: 960
   - Height: 1080
   - Position: X=0, Y=0

2. **Browser Source - ROI:** (Right 50%)
   - URL: `file:///c:/Users/user/Desktop/devpost/video_assets/roi_calculator.html`
   - Width: 960
   - Height: 1080
   - Position: X=960, Y=0

**Duration:** 25 seconds

---

## 🎙️ Audio Recording Setup

### Microphone Configuration

**Recommended hardware:**
- USB condenser mic (Blue Yeti, Audio-Technica AT2020USB+)
- Headset mic (HyperX, SteelSeries)
- Built-in laptop mic (acceptable if quiet environment)

**OBS Audio Settings:**
1. Settings → Audio → Mic/Auxiliary Audio
2. Select your microphone
3. Click gear icon → Filters → Add:
   - **Noise Suppression:** RNNoise (removes background noise)
   - **Noise Gate:** Close Threshold -40dB, Open Threshold -35dB (cuts silence)
   - **Compressor:** Ratio 3:1, Threshold -18dB (evens volume)
   - **Gain:** +5dB if voice is too quiet

**Test recording:**
1. Record 10 seconds of narration
2. Play back to check:
   - Volume: -14 to -12 dB (OBS audio meter should peak in green/yellow)
   - Clarity: No muffling, no echo
   - Background: Minimal room noise

---

## 📹 Recording Workflow

### Pre-Recording Checklist

**Environment:**
- [ ] Close all unnecessary apps (Slack, Discord, email)
- [ ] Disable notifications (Windows Focus Assist → Alarms Only)
- [ ] Close browser tabs except demo pages
- [ ] Clear desktop clutter (move files to temp folder)

**OBS Setup:**
- [ ] All scenes created and tested
- [ ] Transitions configured (Fade, 300ms)
- [ ] Microphone volume tested (-14 to -12 dB)
- [ ] Hotkeys configured (Scenes 1-5 → F1-F5)
- [ ] Recording path set (Documents/OBS_Recordings/)

**Demo Readiness:**
- [ ] MCP Server running (port 8001)
- [ ] Terminal font size 16pt minimum
- [ ] VS Code zoom level 150%
- [ ] Patient JSON open in VS Code
- [ ] `demo_agent_reasoning.py` ready to run
- [ ] Script printed or on second monitor

---

### Recording Process

**Step 1: Start Recording**
1. Open OBS Studio
2. Select Scene 1 (Title Card)
3. Click "Start Recording" (or Ctrl+R)
4. **Start narration immediately** - no silent intro

**Step 2: Scene Transitions**
| Time | Hotkey | Action |
|------|--------|--------|
| 0:00 | F1 | Scene 1 (Title) - start narration |
| 0:30 | F2 | Scene 2 (Architecture) |
| 0:50 | F3 | Scene 3 (Terminal) - run commands |
| 1:30 | F4 | Scene 4 (Split) - show VS Code + terminal |
| 2:30 | F5 | Scene 5 (Compliance) |
| 2:55 | - | Continue narration |
| 3:00 | - | Stop recording (Ctrl+R) |

**Step 3: Execute Commands**
- Scene 3 (0:50): Run 3 terminal commands
- Scene 4 (1:30): Show patient JSON → run `python demo_agent_reasoning.py`
- Scene 4 (2:00): Show final JSON draft

**Step 4: Monitor Audio**
- Watch OBS audio meter during recording
- Voice should peak in green zone (-14 to -12 dB)
- If too quiet: Stop, adjust gain filter, restart
- If too loud: Move farther from mic or reduce gain

---

### Post-Recording

**Immediate Review:**
1. Watch full recording in VLC/Windows Media Player
2. Check for:
   - ✓ Clear audio throughout (no muffling, clipping, or echo)
   - ✓ All commands executed correctly
   - ✓ No typos visible in terminal
   - ✓ Timing under 3:00
   - ✓ All scenes transitioned smoothly

**If re-recording needed:**
- Can record scenes individually and splice in video editor
- Or do full take again (only 3 minutes)

---

## 🎨 Rendering & Export

### OBS Output Location

Default: `C:\Users\[user]\Videos\`
File format: `.mkv` (OBS default)

### Convert to MP4 (YouTube-ready)

**Option 1: OBS Remux**
1. File → Remux Recordings
2. Select `.mkv` file
3. Click "Remux"
4. Output: `.mp4` in same folder

**Option 2: FFmpeg (if you have it)**
```bash
ffmpeg -i authclear_demo.mkv -c copy authclear_demo.mp4
```

**Option 3: Handbrake (free video converter)**
- Download: https://handbrake.fr/
- Load `.mkv` → Preset: "Fast 1080p30" → Start

---

## 📐 Creating Visual Assets (HTML to PNG)

### Method 1: Browser Screenshot (Built-in)

**Chrome/Edge:**
1. Open `title_card.html` in browser
2. Press F12 (DevTools)
3. Press Ctrl+Shift+P → "Capture full size screenshot"
4. Save as `title_card.png`

**Repeat for:**
- `architecture_diagram.html`
- `compliance_badges.html` (resize browser to 960x1080 first)
- `roi_calculator.html` (resize browser to 960x1080 first)

### Method 2: Online Tool

**Website:** https://www.screenshotmachine.com/
1. Upload HTML file or paste URL
2. Set resolution: 1920x1080 (or 960x1080 for split screens)
3. Download PNG

---

## ⚠️ Common Issues & Fixes

### Issue: Black screen when recording window
**Fix:** OBS Settings → Advanced → Color Format → Change to I420

### Issue: Audio desyncs with video
**Fix:** Settings → Video → FPS → Change to "Integer FPS" → 30

### Issue: Laggy recording
**Fix:**
1. Close background apps (Chrome, Discord)
2. Lower CPU preset to "faster" or "fast"
3. Or use GPU encoder (NVENC if you have NVIDIA GPU)

### Issue: Video over 3 minutes
**Fix:**
1. Speed up narration pace (165-170 wpm)
2. Cut 2-3 seconds from each scene transition
3. Or edit video post-recording to trim pauses

### Issue: File size too large (>500MB)
**Fix:**
1. Use x264 encoder with CRF 23 (Settings → Output → Recording)
2. Or compress with Handbrake after recording

---

## 🎯 Hotkey Configuration

**Recommended OBS hotkeys:**

| Action | Hotkey |
|--------|--------|
| Start/Stop Recording | Ctrl+R |
| Scene 1 (Title) | F1 |
| Scene 2 (Architecture) | F2 |
| Scene 3 (Terminal) | F3 |
| Scene 4 (Split) | F4 |
| Scene 5 (Compliance) | F5 |

**Setup:** OBS → Settings → Hotkeys → Assign keys

---

## ✅ Final Quality Check

Before uploading to YouTube, verify:

- [ ] Resolution: 1920x1080
- [ ] Duration: Under 3:00
- [ ] Audio: Clear, no clipping, even volume
- [ ] Video: No lag, all text readable
- [ ] File format: .mp4 (not .mkv)
- [ ] File size: Under 500MB (YouTube upload limit)
- [ ] Subtitles: `authclear_demo_subtitles.srt` ready to upload

---

## 📤 YouTube Upload Settings

**Video title:** AuthClear - AI Prior Authorization Copilot (Agents Assemble 2026)

**Description:**
```
AuthClear: AI-powered prior authorization system for healthcare

🏆 Submission for: Agents Assemble Hackathon 2026
🔗 GitHub: https://github.com/[yourusername]/authclear
🏗️ Built with: FastMCP, Claude Sonnet 4, FHIR R4, FastAPI

Architecture:
- MCP Server: FHIR clinical terminology engine (ICD-10, RxNorm, LOINC)
- A2A Agent: Prior authorization copilot with human-in-the-loop

Compliant with TX SB 490, AZ HB 2417, MD HB 1174

Tech stack: Python, FastMCP 3.2, Anthropic Claude API, FHIR Resources, Railway

Tags: #AI #Healthcare #PriorAuthorization #FHIR #AgentsAssemble
```

**Visibility:** Unlisted
**Category:** Science & Technology
**Thumbnail:** Upload `title_card.png` (1280x720 crop)
**Subtitles:** Upload `authclear_demo_subtitles.srt`

---

**Total setup time:** 30-45 minutes
**Recording time:** 3 attempts × 3 min = 10 minutes
**Post-production:** 15 minutes
**Upload:** 5 minutes

**Total:** ~1.5 hours for complete video production
