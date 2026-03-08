# Bespoke Testing Guide - Phase 3 Checkpoint

## Critical Testing Required Before Phase 4

This document outlines comprehensive testing for all newly implemented visualizer widgets and integrations. **All tests must pass before proceeding to Phase 4.**

---

## Test Environment Setup

### Prerequisites
```bash
cd /home/nova/.local/projects/bespoke
source venv/bin/activate
python main.py
```

### Required Hardware
- **Microphone**: Active and accessible
- **Audio input**: Working system audio
- **Display**: Minimum 1280x720 resolution

---

## 1. Application Launch Tests

### Test 1.1: Clean Startup
**Objective**: Verify application launches without errors

**Steps**:
1. Launch application: `python main.py`
2. Observe console output
3. Check that main window appears

**Expected Results**:
- ✅ No Python exceptions in console
- ✅ Main window displays with header
- ✅ Dashboard view loads
- ✅ No missing import errors

**Edge Cases**:
- Launch with no microphone connected
- Launch with multiple audio devices
- Launch on fresh install (no database file)

**Failure Indicators**:
- ImportError for Qt widgets
- Missing module errors for new widgets
- Segmentation fault on startup

---

## 2. Dashboard Tests

### Test 2.1: Dashboard Rendering
**Objective**: Verify dashboard widgets render correctly

**Steps**:
1. Navigate to Dashboard (should be default view)
2. Observe all dashboard components

**Expected Results**:
- ✅ Streak calendar displays 30-day grid
- ✅ Progress rings show 4 modules
- ✅ Session recommendations visible
- ✅ No layout overflow or clipping

**Edge Cases**:
- Dashboard with no session history (empty database)
- Dashboard with 30+ days of sessions
- Resize window to minimum size

**Failure Indicators**:
- Blank calendar cells
- Progress rings not painting
- Layout breaks on resize

---

## 3. Settings View Tests

### Test 3.1: Microphone Selection
**Objective**: Verify mic dropdown populates and persists

**Steps**:
1. Navigate to Settings
2. Check microphone dropdown
3. Select a different device
4. Click "Save Settings"
5. Restart application
6. Return to Settings

**Expected Results**:
- ✅ Dropdown lists available input devices
- ✅ Selection persists after restart
- ✅ No crashes when changing devices

**Edge Cases**:
- No microphones available
- USB mic plugged in during runtime
- Default device changes

### Test 3.2: Voice Threshold Calibration
**Objective**: Verify auto-calibration works

**Steps**:
1. Navigate to Settings
2. Click "Auto-Calibrate"
3. Speak normally for 5 seconds
4. Observe threshold adjustment

**Expected Results**:
- ✅ Live level indicator updates during speech
- ✅ Threshold slider adjusts automatically
- ✅ Calibration completes after 5 seconds
- ✅ Settings save successfully

**Edge Cases**:
- Calibrate in complete silence
- Calibrate with very loud input
- Cancel calibration mid-process (close settings)

**Failure Indicators**:
- Level stuck at -60 dB
- Calibration never completes
- Audio engine doesn't stop after calibration

---

## 4. Module 1: Pitch Control Tests (Baseline)

### Test 4.1: Exercise 1a - Pitch Hold
**Objective**: Verify pitch graph still works (regression test)

**Steps**:
1. Navigate to Modules → Module 1
2. Launch Exercise 1a (Pitch Hold)
3. Click "Start Exercise"
4. Hum at ~200 Hz for 10 seconds
5. Click "Stop Exercise"

**Expected Results**:
- ✅ Pitch graph displays scrolling trace
- ✅ Target line and tolerance bands visible
- ✅ Real-time updates during recording
- ✅ Score displays after completion
- ✅ Session saves to database

**Edge Cases**:
- No voice input (silence)
- Pitch outside 60-600 Hz range
- Very short exercise (<1 second)

**Failure Indicators**:
- Graph doesn't update
- Application freezes during recording
- Score calculation crashes

---

## 5. Module 2: Amplitude Visualizer Tests

### Test 5.1: AmplitudeBar Widget
**Objective**: Verify vertical amplitude meter renders and updates

**Steps**:
1. Launch any Module 2 exercise using `amplitude_bar` visualizer
2. Start exercise
3. Speak at varying volumes (quiet → loud → quiet)
4. Observe meter behavior

**Expected Results**:
- ✅ Bar fills from bottom to top
- ✅ Color gradient: green → yellow → red
- ✅ Peak hold indicator appears
- ✅ Threshold line visible
- ✅ Real-time updates (no lag)
- ✅ Current dB value displays at top

**Edge Cases**:
- Complete silence (should show -60 dB)
- Clipping/very loud input (0 dB)
- Rapid volume changes
- Window resize during exercise

**Failure Indicators**:
- Bar doesn't fill
- Gradient colors missing
- Peak hold stuck
- Paint errors in console
- Widget doesn't resize properly

### Test 5.2: AmplitudeEnvelope Widget
**Objective**: Verify scrolling amplitude trace works

**Steps**:
1. Launch Module 2 exercise using `amplitude_envelope` visualizer
2. Start exercise
3. Speak with varying volume patterns
4. Observe trace scrolling

**Expected Results**:
- ✅ Trace scrolls left to right
- ✅ 10-second time window visible
- ✅ Amplitude range -60 to 0 dB
- ✅ Grid lines visible
- ✅ Target line (if applicable) displays
- ✅ Smooth scrolling at 60fps

**Edge Cases**:
- Long exercise (>10 seconds)
- No voice input
- Sustained tone (flat line)

**Failure Indicators**:
- Trace doesn't scroll
- Data points missing
- Pyqtgraph errors
- Memory leak (check with long exercises)

---

## 6. Module 3: WPM Gauge Tests

### Test 6.1: WPMGauge Widget
**Objective**: Verify circular WPM gauge renders correctly

**Steps**:
1. Launch any Module 3 exercise
2. Start exercise
3. Speak continuously
4. Observe gauge behavior

**Expected Results**:
- ✅ Circular gauge displays (240° arc)
- ✅ WPM value shows in center (large font)
- ✅ Speaking indicator lights up during speech
- ✅ Target marker visible
- ✅ Color changes based on accuracy (green/yellow/red)
- ✅ Scale labels (60-200 WPM) visible

**Edge Cases**:
- WPM = 0 (silence)
- WPM > 200 (very fast speech)
- WPM < 60 (very slow speech)
- Widget resize

**Failure Indicators**:
- Gauge arc doesn't draw
- WPM stuck at 0
- Speaking indicator doesn't toggle
- Paint coordinate errors
- Gauge doesn't update during speech

**Note**: WPM calculation requires Whisper transcription (post-exercise). During recording, only speaking status should update.

---

## 7. Module 4: Dynamics Visualizer Tests

### Test 7.1: DBMeter Widget
**Objective**: Verify dual peak/RMS meter works

**Steps**:
1. Launch Module 4 exercise using `db_meter` visualizer
2. Start exercise
3. Speak at varying volumes
4. Observe both meters

**Expected Results**:
- ✅ Two vertical bars (Peak and RMS)
- ✅ Both bars fill independently
- ✅ Peak hold line on Peak bar
- ✅ Dynamic range value displays at top
- ✅ Current values show at bottom
- ✅ Color gradient on both bars

**Edge Cases**:
- Silence (both at -60 dB)
- Loud input (peak near 0 dB)
- Rapid dynamics (staccato speech)

**Failure Indicators**:
- Only one bar updates
- Peak hold doesn't work
- Range calculation incorrect
- Bars don't reset between exercises

### Test 7.2: CentroidBar Widget
**Objective**: Verify spectral centroid horizontal bar works

**Steps**:
1. Launch Module 4 exercise using `centroid_bar` visualizer
2. Start exercise
3. Speak with varying tone (dark → bright)
4. Observe bar behavior

**Expected Results**:
- ✅ Horizontal bar fills left to right
- ✅ Gradient: purple (dark) → teal → amber (bright)
- ✅ Current Hz value displays at top
- ✅ Brightness label updates (Warm/Balanced/Bright)
- ✅ Baseline marker (if set)
- ✅ Comparison text vs baseline

**Edge Cases**:
- No voice input (centroid = 0)
- Very low frequency voice
- Very high frequency voice
- No baseline set

**Failure Indicators**:
- Bar doesn't fill
- Gradient missing
- Centroid value stuck at 0
- Baseline marker doesn't appear

---

## 8. Exercise Instructions Tests

### Test 8.1: Dynamic Instructions
**Objective**: Verify instructions update per phase

**Steps**:
1. Launch any exercise
2. Observe "Ready" phase instructions
3. Click "Start Exercise"
4. Observe "Recording" phase instructions
5. Complete exercise
6. Observe "Completed" phase instructions

**Expected Results**:
- ✅ Instructions change for each phase
- ✅ Tier-specific details included
- ✅ Reading passages display (exercises 1c, 1d)
- ✅ Text wraps properly

**Edge Cases**:
- All 20 exercises (1a-1e, 2a-2e, 3a-3e, 4a-4e)
- All 3 tiers per exercise
- Long instruction text

### Test 8.2: Reading Passages
**Objective**: Verify passages display for relevant exercises

**Steps**:
1. Launch Exercise 1c (Variation Reading)
2. Check for reading passage
3. Launch Exercise 1d (Emotional Contrast)
4. Check for emotional cues

**Expected Results**:
- ✅ Passage displays in text area
- ✅ Different passages per tier
- ✅ Text is readable (font size, contrast)
- ✅ Passage hidden for non-reading exercises

**Edge Cases**:
- Foundation tier (short passages)
- Advanced tier (long passages)
- Exercises without passages (should hide widget)

---

## 9. Audio Engine Integration Tests

### Test 9.1: Real-time Data Flow
**Objective**: Verify audio engine feeds all visualizers

**Steps**:
1. Launch exercises from each module
2. Speak during each
3. Verify visualizer updates

**Expected Results**:
- ✅ Pitch data → PitchGraph
- ✅ Amplitude data → AmplitudeBar/Envelope
- ✅ Voice activity → WPMGauge speaking indicator
- ✅ Peak/RMS → DBMeter
- ✅ Centroid → CentroidBar
- ✅ No data lag (< 100ms)

**Edge Cases**:
- Switch between exercises rapidly
- Long-running exercises (>60 seconds)
- Multiple start/stop cycles

**Failure Indicators**:
- Visualizer doesn't update
- Data delayed by >1 second
- Audio engine crashes
- Memory leak

---

## 10. Graceful Degradation Tests

### Test 10.1: Whisper Unavailable
**Objective**: Verify app works without faster-whisper

**Steps**:
1. Ensure faster-whisper is NOT installed
2. Launch Module 3 exercise
3. Complete exercise
4. Check post-exercise results

**Expected Results**:
- ✅ Exercise runs normally
- ✅ WPM shows 0 or error message
- ✅ No crash
- ✅ Fallback message displayed

**Test Command**:
```bash
pip uninstall faster-whisper -y
python main.py
# Test Module 3 exercise
pip install faster-whisper  # Restore
```

### Test 10.2: Ollama Unavailable
**Objective**: Verify app works without Ollama

**Steps**:
1. Ensure Ollama is NOT installed/running
2. Complete any exercise
3. Check for coaching feedback

**Expected Results**:
- ✅ Exercise completes normally
- ✅ Fallback feedback displays
- ✅ No crash
- ✅ Generic coaching message shown

---

## 11. Performance Tests

### Test 11.1: CPU Usage
**Objective**: Verify reasonable CPU usage during exercises

**Steps**:
1. Monitor CPU with `top` or `htop`
2. Launch exercise
3. Record for 30 seconds
4. Observe CPU usage

**Expected Results**:
- ✅ CPU usage < 50% on modern hardware
- ✅ No CPU spikes
- ✅ Smooth 60fps updates

**Failure Indicators**:
- CPU usage > 80%
- UI stuttering
- Dropped frames in visualizers

### Test 11.2: Memory Leaks
**Objective**: Verify no memory leaks in long sessions

**Steps**:
1. Monitor memory with `top`
2. Run 5 consecutive exercises
3. Check memory growth

**Expected Results**:
- ✅ Memory usage stable
- ✅ No continuous growth
- ✅ Memory released after exercise

**Failure Indicators**:
- Memory grows >100MB per exercise
- Memory never released
- Application slows over time

---

## 12. Database Integration Tests

### Test 12.1: Session Saving
**Objective**: Verify all exercise types save correctly

**Steps**:
1. Complete one exercise from each module
2. Click "Save Session" for each
3. Check database file

**Expected Results**:
- ✅ Sessions appear in database
- ✅ Scores stored as JSON
- ✅ Timestamps correct
- ✅ Module/exercise IDs correct

**Verification**:
```bash
sqlite3 ~/.bespoke/bespoke.db
SELECT * FROM sessions ORDER BY id DESC LIMIT 5;
```

### Test 12.2: Settings Persistence
**Objective**: Verify settings save and load

**Steps**:
1. Change microphone in Settings
2. Adjust voice threshold
3. Save settings
4. Restart application
5. Check Settings view

**Expected Results**:
- ✅ Microphone selection persists
- ✅ Threshold value persists
- ✅ No errors on load

---

## 13. Edge Case Stress Tests

### Test 13.1: Rapid Exercise Switching
**Objective**: Verify no crashes when switching exercises quickly

**Steps**:
1. Launch Exercise 1a
2. Immediately click "Back"
3. Launch Exercise 2a
4. Immediately click "Back"
5. Repeat 5 times

**Expected Results**:
- ✅ No crashes
- ✅ Audio engine stops/starts cleanly
- ✅ Visualizers clean up properly

**Failure Indicators**:
- Segmentation fault
- Audio engine doesn't stop
- Multiple audio streams running

### Test 13.2: Window Resize During Exercise
**Objective**: Verify visualizers handle resize

**Steps**:
1. Start any exercise
2. Resize window while recording
3. Maximize/minimize window
4. Observe visualizer behavior

**Expected Results**:
- ✅ Visualizers resize smoothly
- ✅ No layout breaks
- ✅ Paint events handle new dimensions
- ✅ No crashes

### Test 13.3: No Microphone Input
**Objective**: Verify graceful handling of no audio

**Steps**:
1. Mute microphone or set input to 0%
2. Start exercise
3. Let it run for 10 seconds
4. Stop exercise

**Expected Results**:
- ✅ Visualizers show baseline values
- ✅ No crashes
- ✅ Score reflects no input
- ✅ Appropriate feedback message

---

## 14. Cross-Module Consistency Tests

### Test 14.1: All 20 Exercises Launch
**Objective**: Verify every exercise can be started

**Steps**:
1. Navigate to each module
2. Launch each exercise (1a-1e, 2a-2e, 3a-3e, 4a-4e)
3. Verify visualizer loads
4. Click "Back" without completing

**Expected Results**:
- ✅ All 20 exercises launch
- ✅ Correct visualizer for each
- ✅ Instructions display
- ✅ No import errors

**Failure Indicators**:
- Exercise doesn't launch
- Wrong visualizer displayed
- Missing instructions
- KeyError for exercise ID

---

## Priority Testing Order

### High Priority (Must Pass)
1. ✅ Application Launch (Test 1.1)
2. ✅ Module 1 Regression (Test 4.1)
3. ✅ AmplitudeBar (Test 5.1)
4. ✅ WPMGauge (Test 6.1)
5. ✅ DBMeter (Test 7.1)
6. ✅ All 20 Exercises Launch (Test 14.1)

### Medium Priority (Should Pass)
7. ✅ Dashboard Rendering (Test 2.1)
8. ✅ Settings Persistence (Test 3.1, 3.2)
9. ✅ AmplitudeEnvelope (Test 5.2)
10. ✅ CentroidBar (Test 7.2)
11. ✅ Dynamic Instructions (Test 8.1)

### Low Priority (Nice to Have)
12. ✅ Graceful Degradation (Tests 10.1, 10.2)
13. ✅ Performance Tests (Tests 11.1, 11.2)
14. ✅ Edge Cases (Tests 13.1-13.3)

---

## Known Limitations to Document

1. **WPM Calculation**: Only works post-exercise with Whisper installed
2. **Ollama Coaching**: Requires Ollama running locally
3. **Baseline Comparison**: Requires baseline assessment (Phase 4)
4. **Module 3 Transcription**: Requires faster-whisper for full functionality

---

## Bug Reporting Template

When reporting issues, include:

```
**Test**: [Test number and name]
**Exercise**: [Exercise ID if applicable]
**Visualizer**: [Widget type]
**Steps to Reproduce**:
1. 
2. 
3. 

**Expected**: 
**Actual**: 
**Error Messages**: 
**Console Output**: 
```

---

## Success Criteria

Phase 3 is ready for Phase 4 when:
- ✅ All High Priority tests pass
- ✅ At least 80% of Medium Priority tests pass
- ✅ No critical bugs (crashes, data loss)
- ✅ All visualizers render without paint errors
- ✅ Audio engine integrates cleanly with all widgets

---

## Next Steps After Testing

1. **If all tests pass**: Proceed to Phase 4 (Baseline Assessment, Final Polish)
2. **If bugs found**: Create bug list, prioritize, fix critical issues
3. **If major issues**: Refactor problematic widgets before Phase 4

**Testing complete? Report results and we'll proceed!**
