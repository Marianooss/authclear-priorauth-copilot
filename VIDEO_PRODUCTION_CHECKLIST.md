# 🎬 AuthClear Video Production Checklist

**Deadline:** May 11, 2026 @ 11:59 PM ET
**Target Duration:** 2:55 (under 3:00 requirement)
**Format:** 1920x1080, 30fps, MP4, <500MB

---

## 📋 PHASE 1: Pre-Production Setup (30 minutes)

### Visual Assets Creation

- [ ] Open `video_assets/title_card.html` in Chrome
  - [ ] Press F12 → Ctrl+Shift+P → "Capture full size screenshot"
  - [ ] Save as `title_card.png` (1920x1080)

- [ ] Open `video_assets/architecture_diagram.html`
  - [ ] Screenshot → Save as `architecture_diagram.png` (1920x1080)

- [ ] Resize browser window to 960x1080 (half width)
  - [ ] Open `compliance_badges.html` → Screenshot as `compliance_badges.png`
  - [ ] Open `roi_calculator.html` → Screenshot as `roi_calculator.png`

**Verify all 4 PNG files created in `video_assets/` folder**

---

### OBS Studio Configuration

- [ ] Install OBS Studio 30.0+ from https://obsproject.com/download
- [ ] Open OBS → Settings → Video
  - [ ] Base Resolution: 1920x1080
  - [ ] Output Resolution: 1920x1080
  - [ ] FPS: 30

- [ ] Settings → Output
  - [ ] Output Mode: Advanced
  - [ ] Encoder: x264
  - [ ] Bitrate: 5000 Kbps
  - [ ] CPU Preset: veryfast

- [ ] Settings → Audio
  - [ ] Sample Rate: 48 kHz
  - [ ] Mic/Aux Device: Select your microphone

- [ ] Add audio filters (Mic → Gear icon → Filters)
  - [ ] Add: Noise Suppression (RNNoise)
  - [ ] Add: Noise Gate (Threshold -40dB)
  - [ ] Add: Compressor (Ratio 3:1, Threshold -18dB)
  - [ ] Add: Gain (+5dB if needed)

**Test recording:** Record 10 seconds of voice, verify audio clear

---

### OBS Scene Setup

**Scene 1: Title Card**
- [ ] Add Scene → Name: "1_Title"
- [ ] Add Source → Image → Select `title_card.png`
- [ ] Right-click source → Transform → Fit to Screen

**Scene 2: Architecture**
- [ ] Add Scene → Name: "2_Architecture"
- [ ] Add Source → Image → Select `architecture_diagram.png`
- [ ] Right-click → Transform → Fit to Screen

**Scene 3: Terminal Demo**
- [ ] Add Scene → Name: "3_Terminal"
- [ ] Add Source → Window Capture
  - [ ] Window: "Windows PowerShell" or "Windows Terminal"
  - [ ] Capture method: Windows 10 (1903+)
  - [ ] Check "Capture Cursor"
- [ ] Right-click → Transform → Stretch to Screen

**Scene 4: Split Screen**
- [ ] Add Scene → Name: "4_Split"
- [ ] Add Source → Window Capture (VS Code)
  - [ ] Transform → Edit → Position X=0, Y=0, Width=960, Height=1080
- [ ] Add Source → Window Capture (Terminal)
  - [ ] Transform → Edit → Position X=960, Y=0, Width=960, Height=1080

**Scene 5: Compliance + ROI**
- [ ] Add Scene → Name: "5_Compliance"
- [ ] Add Source → Browser Source
  - [ ] URL: `file:///c:/Users/user/Desktop/devpost/video_assets/compliance_badges.html`
  - [ ] Width: 960, Height: 1080
  - [ ] Position: X=0, Y=0
- [ ] Add Source → Browser Source
  - [ ] URL: `file:///c:/Users/user/Desktop/devpost/video_assets/roi_calculator.html`
  - [ ] Width: 960, Height: 1080
  - [ ] Position: X=960, Y=0

**Configure hotkeys:**
- [ ] Settings → Hotkeys → Set F1-F5 for Scenes 1-5
- [ ] Set Ctrl+R for Start/Stop Recording

---

### Demo Environment Preparation

**Terminal Setup:**
- [ ] Open PowerShell or Windows Terminal
- [ ] Set font: Cascadia Code or Fira Code, 16pt
- [ ] Set color scheme: One Half Dark or Dracula
- [ ] Navigate to project: `cd c:\Users\user\Desktop\devpost`
- [ ] Test run: `python demo_agent_reasoning.py` (should work)

**VS Code Setup:**
- [ ] Open VS Code
- [ ] Open file: `shared/fhir/synthetic_patients/patient_t2dm_complete.json`
- [ ] Zoom: Ctrl + "+" to 150%
- [ ] Theme: Dark+ (default dark) or One Dark Pro

**System Cleanup:**
- [ ] Close unnecessary apps (Slack, Discord, email)
- [ ] Windows: Settings → System → Focus Assist → "Alarms only"
- [ ] Clear desktop (move files to temp folder)
- [ ] Close all browser tabs except demo pages

---

### Script Preparation

- [ ] Print `VIDEO_SCRIPT_3MIN.md` or display on second monitor
- [ ] Read through script 2x to familiarize
- [ ] Practice narration with stopwatch (aim for 2:50-2:55)
- [ ] Mark timing checkpoints: 0:30, 0:50, 1:30, 2:30

---

## 📋 PHASE 2: Recording (30 minutes)

### Pre-Recording Final Check (5 min)

**System:**
- [ ] Close all apps except OBS, Terminal, VS Code, Browser
- [ ] Disable Windows notifications (Focus Assist)
- [ ] Set microphone volume (speak normally, meter should peak at -14 to -12 dB)
- [ ] Restart OBS to clear any memory leaks

**Demo Readiness:**
- [ ] MCP Server NOT running (we'll simulate with commands)
- [ ] Terminal clear: Type `cls` or `clear`
- [ ] VS Code showing patient JSON
- [ ] `DEMO_COMMANDS.md` open on second monitor

**Environment:**
- [ ] Room quiet (no background noise, AC, fans)
- [ ] Glass of water nearby
- [ ] Phone on silent

---

### Recording Session (3-5 takes × 3 min each)

**Take 1: Dry Run**
- [ ] Start recording (Ctrl+R)
- [ ] Read script at normal pace
- [ ] Execute all commands
- [ ] Switch scenes with F1-F5
- [ ] Stop at 3:00 (or earlier if finished)
- [ ] **Review:** Check audio, timing, command execution

**Take 2: Quality Take**
- [ ] Clear terminal (`cls`)
- [ ] Reset VS Code to patient JSON
- [ ] Start recording
- [ ] Speak clearly, confidently
- [ ] Execute commands deliberately (not rushed)
- [ ] **Review:** Should be close to final quality

**Take 3: Final (if needed)**
- [ ] Only if Take 2 had major issues
- [ ] Focus on clearest narration
- [ ] Smooth command execution
- [ ] Stay under 2:55

**Select best take:** Review all recordings, choose clearest audio + smoothest demo

---

### Detailed Recording Timeline

**0:00-0:30 (Scene 1 → Scene 2) - Title + Problem**
- [ ] Start with Scene 1 (Title Card)
- [ ] Begin narration: "Physicians spend 12 hours..."
- [ ] At 0:30: Press F2 (Architecture scene)

**0:30-0:50 (Scene 2) - Architecture**
- [ ] Continue narration: "AuthClear consists of two agents..."
- [ ] At 0:50: Press F3 (Terminal scene)

**0:50-1:30 (Scene 3) - MCP Server Demo**
- [ ] At 0:50: Paste + run ICD-10 command
- [ ] Narrate while command runs
- [ ] At 1:00: Paste + run RxNorm command
- [ ] At 1:10: Paste + run Prior Auth criteria command
- [ ] At 1:30: Press F4 (Split scene)

**1:30-2:30 (Scene 4) - A2A Agent Demo**
- [ ] VS Code visible on left, terminal on right
- [ ] Narrate patient overview
- [ ] At 1:45: Run `python demo_agent_reasoning.py`
- [ ] Let script output scroll (should take ~15 seconds)
- [ ] At 2:00: Show or type final JSON
- [ ] At 2:25: Highlight `"human_review_required": true`
- [ ] At 2:30: Press F5 (Compliance scene)

**2:30-2:55 (Scene 5) - Compliance + Impact**
- [ ] Narrate compliance badges
- [ ] Narrate ROI calculator
- [ ] At 2:55: Finish with "...keeps physicians in control"
- [ ] Stop recording (Ctrl+R)

---

## 📋 PHASE 3: Post-Production (15 minutes)

### Immediate Review

- [ ] Watch full recording start to finish
- [ ] Check audio:
  - [ ] Clear speech (no muffling)
  - [ ] Even volume throughout
  - [ ] No background noise or echo
- [ ] Check video:
  - [ ] All text readable (terminal, VS Code)
  - [ ] Commands executed correctly
  - [ ] No typos visible
  - [ ] Scene transitions smooth
- [ ] Check timing:
  - [ ] Total duration under 3:00
  - [ ] No long awkward pauses

**If issues found:** Re-record that scene or full take

---

### Video Export

- [ ] Locate recording: `C:\Users\[user]\Videos\` (usually `.mkv` format)
- [ ] OBS → File → Remux Recordings
  - [ ] Select `.mkv` file
  - [ ] Click "Remux"
  - [ ] Output: `.mp4` in same folder
- [ ] Rename to: `authclear_demo_final.mp4`

**Verify MP4:**
- [ ] Right-click → Properties → Details
  - [ ] Frame width: 1920
  - [ ] Frame height: 1080
  - [ ] Frame rate: 30
  - [ ] File size: <500MB

---

### Optional: Video Editing (if needed)

**If minor issues need fixing:**
- [ ] Use DaVinci Resolve (free) or Windows Video Editor
- [ ] Import `authclear_demo_final.mp4`
- [ ] Trim awkward pauses
- [ ] Normalize audio levels
- [ ] Add fade in/out (1 second each)
- [ ] Export as MP4, 1920x1080, 30fps

---

### Create Thumbnail

- [ ] Open `title_card.png` in Paint or Photoshop
- [ ] Resize to 1280x720 (YouTube thumbnail size)
- [ ] Optionally add text overlay: "3 MIN DEMO" or "LIVE DEMO"
- [ ] Save as `authclear_thumbnail.jpg`

---

## 📋 PHASE 4: YouTube Upload (10 minutes)

### Upload to YouTube

- [ ] Go to https://studio.youtube.com
- [ ] Click "Create" → "Upload video"
- [ ] Select `authclear_demo_final.mp4`

**Video details:**
- [ ] **Title:** `AuthClear - AI Prior Authorization Copilot (Agents Assemble 2026)`
- [ ] **Description:** (paste from `OBS_SETUP_GUIDE.md`)
  ```
  AuthClear: AI-powered prior authorization system for healthcare

  🏆 Submission for: Agents Assemble Hackathon 2026
  🔗 GitHub: https://github.com/[yourusername]/authclear
  🏗️ Built with: FastMCP, Claude Sonnet 4, FHIR R4, FastAPI

  Architecture:
  - MCP Server: FHIR clinical terminology engine (ICD-10, RxNorm, LOINC)
  - A2A Agent: Prior authorization copilot with human-in-the-loop

  Compliant with TX SB 490, AZ HB 2417, MD HB 1174

  Tech stack: Python, FastMCP 3.2, Anthropic Claude API, FHIR Resources

  Tags: #AI #Healthcare #PriorAuthorization #FHIR #AgentsAssemble
  ```
- [ ] **Thumbnail:** Upload `authclear_thumbnail.jpg`
- [ ] **Playlist:** Create "Hackathon Submissions 2026"
- [ ] **Audience:** Not made for kids
- [ ] **Visibility:** Unlisted

**Subtitles:**
- [ ] Click "Subtitles" tab
- [ ] Upload file → Select `authclear_demo_subtitles.srt`
- [ ] Language: English
- [ ] Verify sync by scrubbing through video

**Video elements:**
- [ ] End screen: Add subscribe button (optional)
- [ ] Cards: Add link to GitHub repo (optional)

- [ ] Click "Publish"
- [ ] Wait for processing (1-2 minutes)
- [ ] Copy video URL (e.g., `https://youtube.com/watch?v=...`)

---

## 📋 PHASE 5: Devpost Submission (5 minutes)

### Add Video to Devpost

- [ ] Go to https://agents-assemble.devpost.com/
- [ ] Click "Edit Submission"
- [ ] Scroll to "Video Demo URL"
- [ ] Paste YouTube URL
- [ ] Click "Save"

**Verify:**
- [ ] Video embeds correctly in Devpost preview
- [ ] Video plays without errors
- [ ] Duration shows as under 3:00
- [ ] Subtitles visible when enabled

---

## ✅ FINAL VERIFICATION

Before submission deadline:

**Video Quality:**
- [ ] Duration: Under 3:00 ✓
- [ ] Resolution: 1920x1080 ✓
- [ ] Audio: Clear, professional ✓
- [ ] Subtitles: Synced correctly ✓
- [ ] Content: Shows project functioning on Prompt Opinion platform ✓

**Devpost Submission:**
- [ ] Video URL added ✓
- [ ] Video embeds correctly ✓
- [ ] Video publicly visible (unlisted, not private) ✓

**Content Requirements:**
- [ ] Shows both MCP Server and A2A Agent ✓
- [ ] Demonstrates FHIR parsing ✓
- [ ] Demonstrates code resolution ✓
- [ ] Demonstrates prior auth generation ✓
- [ ] Highlights human-in-the-loop ✓
- [ ] Mentions compliance (TX, AZ, MD laws) ✓
- [ ] Shows ROI/impact ✓

---

## 🎯 Time Estimates

| Phase | Duration | Total |
|-------|----------|-------|
| Pre-production | 30 min | 0:30 |
| Recording | 30 min | 1:00 |
| Post-production | 15 min | 1:15 |
| YouTube upload | 10 min | 1:25 |
| Devpost submission | 5 min | 1:30 |

**Total time:** ~1.5 hours (with buffer for retakes)

---

## 📞 Support Resources

**OBS Issues:**
- OBS Forums: https://obsproject.com/forum/
- YouTube tutorials: Search "OBS Studio tutorial 2024"

**Video Editing:**
- DaVinci Resolve: https://www.blackmagicdesign.com/products/davinciresolve (free)
- Shotcut: https://shotcut.org/ (free, simpler)

**Audio Issues:**
- Audacity: https://www.audacityteam.org/ (free audio editor)
- Can export from OBS → edit audio → re-sync in video editor

---

## 🚨 Emergency Backup Plan

**If video recording fails completely:**

**Option 1: Screen record with built-in Windows tool**
- Windows + G → Record game clip
- Works for fullscreen demos
- Lower quality but acceptable

**Option 2: Simple slide deck video**
- Create PowerPoint with screenshots
- Record narration over slides
- Export as video
- Less impressive but meets requirements

**Option 3: Loom (online screen recorder)**
- https://www.loom.com/ (free for <5 min)
- Browser-based, no install
- Quick and easy

---

**Last updated:** 2026-03-30
**Status:** Ready for production
**Estimated completion:** 1.5 hours from start to Devpost submission
