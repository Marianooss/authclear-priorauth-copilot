# 🌐 AuthClear Web UI - User Interface

**Professional web interface for AuthClear Prior Authorization System**

---

## 🚀 Quick Start

### Option 1: Easy Launch (Recommended)

```bash
.\start_web_ui.bat
```

This will:
1. Start the web server on http://localhost:3000
2. Open your browser automatically
3. Show the AuthClear UI

### Option 2: Manual Launch

```bash
python run_web_ui.py
```

Then open your browser to: http://localhost:3000

---

## 📋 Prerequisites

**The A2A Agent backend must be running:**

```bash
# In another terminal:
python run_a2a_agent.py
```

The UI expects the backend on http://localhost:8000

---

## 🎨 Features

### Patient Selection
- Choose from 5 synthetic patients
- View patient demographics and diagnosis
- Auto-fill suggested medication

### Real-Time Processing
- See each step of the prior auth process
- Animated progress indicators
- 5-step workflow visualization

### Results Display
- Confidence score (HIGH/MEDIUM/LOW)
- Criteria evaluation (Met vs Gaps)
- Clinical justification
- Human review requirement

### Compliance
- Human-in-the-loop always enforced
- Compliant with TX SB 490, AZ HB 2417, MD HB 1174
- Clear indication that physician review is required

---

## 👥 Available Patients

1. **Maria González** (50F)
   - Type 2 Diabetes
   - Medication: Ozempic (semaglutide)
   - Status: Complete criteria (90% confidence)

2. **John Smith** (57M)
   - Type 2 Diabetes
   - Medication: Ozempic (semaglutide)
   - Status: Missing criteria (70% confidence)

3. **Sarah Johnson** (43F)
   - Rheumatoid Arthritis
   - Medication: Humira (adalimumab)
   - Status: Complete criteria (88% confidence)

4. **Robert Chen** (46M)
   - Obesity/Prediabetes
   - Medication: Ozempic (weight loss)
   - Status: Off-label indication (65% confidence)

5. **William Martinez** (66M)
   - Atrial Fibrillation
   - Medication: Eliquis (apixaban)
   - Status: Medication switch (85% confidence)

---

## 🎬 For Video Recording

### Recommended Scene

Replace **Scene 3** in your video with the Web UI:

**OLD:** `run_live_demo.bat` (terminal)
**NEW:** Web UI in browser (looks more professional)

**Steps to record:**
1. Start the web UI: `.\start_web_ui.bat`
2. Maximize browser window (F11 fullscreen)
3. Win+G → Start recording
4. Select "Maria González"
5. Click "Process Prior Authorization"
6. Watch the animated steps
7. Show the results screen
8. Stop recording (~40 seconds)

**Narration:**
```
"Let's see AuthClear in action. I'll select Maria González,
a 50-year-old with Type 2 Diabetes requesting Ozempic.

The system processes her FHIR data step by step:
loading her records, resolving clinical codes,
retrieving prior auth criteria, evaluating requirements,
and generating a draft.

The result: 90% confidence, all criteria met,
ready for physician review."
```

---

## 🎨 UI Design

- **Colors:** Purple gradient (#667eea → #764ba2)
- **Typography:** Segoe UI, clean and modern
- **Responsive:** Works on different screen sizes
- **Animations:** Smooth transitions and progress indicators
- **Accessibility:** Clear labels and high contrast

---

## 🐛 Troubleshooting

### Port 3000 already in use
```bash
# Change PORT in run_web_ui.py:
PORT = 3001  # or any other available port
```

### A2A Agent not responding
```bash
# Make sure backend is running:
python run_a2a_agent.py

# Check status:
curl http://localhost:8000/health
```

### FHIR files not loading
The UI will work even if FHIR files can't be loaded - it uses mock data as fallback.

---

## 📦 Files Structure

```
web_ui/
├── index.html      # Main HTML interface
├── app.js          # JavaScript logic
└── (styles inline in HTML)

run_web_ui.py       # Python HTTP server
start_web_ui.bat    # Windows launcher
```

---

## ✅ Testing Checklist

- [ ] Web server starts on port 3000
- [ ] Browser opens automatically
- [ ] Patient selection dropdown works
- [ ] Patient info displays correctly
- [ ] Medication auto-fills
- [ ] Process button triggers animation
- [ ] All 5 steps animate properly
- [ ] Results display with correct confidence
- [ ] Different patients show different results
- [ ] Human review warning displays

---

## 🎯 Next Steps

After testing the UI:

1. **Record video** using the web interface (looks more professional)
2. **Screenshot** the UI for Devpost submission images
3. **Include in README** as main demo method

The Web UI provides a much better visual demonstration than terminal output!

---

**Created:** 2026-03-30
**Status:** ✅ Ready for demo
**Video-ready:** Yes
