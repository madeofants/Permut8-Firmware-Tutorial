# Test Your Plugin - Complete Validation Guide

## Required Parameter Constants
```impala
// Standard parameter index constants used throughout all examples
const int OPERAND_1_HIGH_PARAM_INDEX = 0
const int OPERAND_1_LOW_PARAM_INDEX = 1
const int OPERAND_2_LOW_PARAM_INDEX = 2
const int OPERAND_2_HIGH_PARAM_INDEX = 3
const int OPERATOR_1_PARAM_INDEX = 4
const int OPERATOR_2_PARAM_INDEX = 5
const int SWITCHES_PARAM_INDEX = 6
const int CLOCK_FREQ_PARAM_INDEX = 7
const int PARAM_COUNT = 8
```

## What This Tutorial Does
Learn how to thoroughly test your Permut8 plugins to ensure they work correctly in all situations. We'll create a comprehensive testing framework and walk through testing a complete plugin from basic functionality to edge cases.

## Why Testing Matters
- **Prevent crashes** in live performance situations
- **Ensure musical usability** across different audio sources  
- **Verify parameter behavior** is intuitive and stable
- **Catch edge cases** before users do
- **Build confidence** in your plugin's reliability

---

## Step 1: Create a Test Subject Plugin

### 1.1 Build a Comprehensive Effect
We'll create a multi-mode delay plugin that we can test thoroughly:

```impala
// Multi-Mode Delay - Complete Test Subject
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required parameter constants
const int OPERAND_1_HIGH_PARAM_INDEX = 0
const int OPERAND_1_LOW_PARAM_INDEX = 1
const int OPERAND_2_LOW_PARAM_INDEX = 2
const int OPERAND_2_HIGH_PARAM_INDEX = 3
const int OPERATOR_1_PARAM_INDEX = 4
const int OPERATOR_2_PARAM_INDEX = 5
const int SWITCHES_PARAM_INDEX = 6
const int CLOCK_FREQ_PARAM_INDEX = 7
const int PARAM_COUNT = 8

// Standard global variables
global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global clock = 0
global clockFreqLimit = 0

// Plugin-specific globals
global array delayBufferL[2000]
global array delayBufferR[2000]
global delayIndex = 0
global maxDelay = 1999

// Function with required native declaration
extern native yield

function process()
locals delayTimeParam, feedbackParam, mixParam, modeParam, delayTime, feedback, wetLevel, dryLevel, mode, readPos, delayedL, delayedR, temp, reversePos, outputL, outputR, newSampleL, newSampleR
{
    loop {
        // Parameters
        delayTimeParam = global params[OPERAND_2_HIGH_PARAM_INDEX]      // Delay time (0-255)
        feedbackParam = global params[OPERAND_2_LOW_PARAM_INDEX]       // Feedback amount (0-255)
        mixParam = global params[OPERAND_1_HIGH_PARAM_INDEX]            // Dry/wet mix (0-255)
        modeParam = global params[OPERAND_1_LOW_PARAM_INDEX]           // Delay mode (0-255)
        
        // Scale parameters
        delayTime = 10 + ((delayTimeParam * (global maxDelay - 10)) / 255)
        feedback = (feedbackParam * 200) / 255  // Max 78% feedback
        wetLevel = mixParam
        dryLevel = 255 - mixParam
        
        // Determine delay mode
        mode = modeParam / 64  // 0, 1, 2, 3 modes
        
        // Calculate read position
        readPos = (global delayIndex - delayTime + 2000) % 2000
        
        // Read delayed samples
        delayedL = global delayBufferL[readPos]
        delayedR = global delayBufferR[readPos]
        
        // Apply mode-specific processing
        if (mode == 0) {
            // Normal delay
            // No additional processing
        } else if (mode == 1) {
            // Ping-pong (swap L/R on feedback)
            temp = delayedL
            delayedL = delayedR
            delayedR = temp
        } else if (mode == 2) {
            // Tape delay (add saturation)
            if (delayedL > 1500) delayedL = 1500 + ((delayedL - 1500) / 3)
            else if (delayedL < -1500) delayedL = -1500 + ((delayedL + 1500) / 3)
            if (delayedR > 1500) delayedR = 1500 + ((delayedR - 1500) / 3)
            else if (delayedR < -1500) delayedR = -1500 + ((delayedR + 1500) / 3)
        } else {
            // Reverse delay (read backwards)
            reversePos = (global delayIndex + delayTime) % 2000
            delayedL = global delayBufferL[reversePos]
            delayedR = global delayBufferR[reversePos]
        }
        
        // Mix dry and wet
        outputL = ((global signal[0] * dryLevel) + (delayedL * wetLevel)) / 255
        outputR = ((global signal[1] * dryLevel) + (delayedR * wetLevel)) / 255
        
        // Clipping protection
        if (outputL > 2047) outputL = 2047
        else if (outputL < -2047) outputL = -2047
        if (outputR > 2047) outputR = 2047
        else if (outputR < -2047) outputR = -2047
        
        // Store new samples with feedback
        newSampleL = global signal[0] + ((delayedL * feedback) / 255)
        newSampleR = global signal[1] + ((delayedR * feedback) / 255)
        
        // Feedback clipping
        if (newSampleL > 2047) newSampleL = 2047
        else if (newSampleL < -2047) newSampleL = -2047
        if (newSampleR > 2047) newSampleR = 2047
        else if (newSampleR < -2047) newSampleR = -2047
        
        global delayBufferL[global delayIndex] = newSampleL
        global delayBufferR[global delayIndex] = newSampleR
        
        // LED feedback
        global displayLEDs[0] = delayTimeParam
        global displayLEDs[1] = feedbackParam  
        global displayLEDs[2] = mixParam
        global displayLEDs[3] = (1 << mode)
        
        // Update delay position
        global delayIndex = (global delayIndex + 1) % 2000
        
        // Output
        global signal[0] = outputL
        global signal[1] = outputR
        
        yield()
    }
}
```

### 1.2 Compile and Load
1. Save as `test_delay.impala`
2. Compile: `PikaCmd.exe -compile test_delay.impala`
3. Load: `patch test_delay.gazl`

Now we have a complex plugin to test thoroughly!

---

## Step 2: Basic Functionality Testing

### 2.1 Audio Pass-Through Test
**What to test:** Does audio pass through without the effect?

**Test procedure:**
1. Set all knobs to minimum (counterclockwise)
2. Play audio through plugin
3. **Expected result:** Audio should pass through unchanged
4. **Listen for:** Any distortion, volume changes, or artifacts

**✅ Pass criteria:** Audio sounds identical to bypassed plugin

### 2.2 Effect Activation Test  
**What to test:** Does the effect engage when parameters are changed?

**Test procedure:**
1. Start with all knobs at minimum
2. Slowly turn up knob 3 (delay time)
3. Slowly turn up knob 5 (mix level)
4. **Expected result:** You should hear delay repeats gradually appearing

**✅ Pass criteria:** Clear, musical delay effect with smooth parameter changes

### 2.3 All Parameters Test
**What to test:** Does each parameter do what it's supposed to?

**Test each knob systematically:**

| Knob | Expected Effect | Test Method |
|------|----------------|-------------|
| **Knob 4 (Delay Time)** | Changes repeat timing | Turn slowly, listen for timing changes |
| **Knob 3 (Feedback)** | Changes number of repeats | Turn up gradually, should get more repeats |
| **Knob 1 (Mix)** | Balances dry/wet | Full left = no effect, full right = all effect |
| **Knob 2 (Mode)** | Changes delay character | Turn through range, listen for different behaviors |

**✅ Pass criteria:** Each knob produces expected, musical changes

---

## Step 3: Range and Scaling Testing

### 3.1 Parameter Range Test
**What to test:** Do parameters work smoothly across their full range?

**Test procedure for each knob:**
1. **Minimum position:** Turn fully counterclockwise
   - Should produce minimum effect or turn effect off
   - No strange noises or artifacts
2. **Maximum position:** Turn fully clockwise  
   - Should produce maximum effect
   - Should not cause overload or distortion
3. **Sweep test:** Turn slowly from min to max
   - Changes should be smooth and continuous
   - No sudden jumps or dead zones

**Common problems to listen for:**
- **Dead zones:** Parts of knob range that don't change anything
- **Sudden jumps:** Abrupt changes instead of smooth transitions
- **Non-musical ranges:** Too extreme or not useful musically

### 3.2 Parameter Interaction Test
**What to test:** Do parameters work well together?

**Test procedure:**
1. **High delay + high feedback:** Should create lots of repeats
2. **Short delay + high feedback:** Should create flutter or pitch effects
3. **Long delay + low feedback:** Should create single, spaced repeats
4. **Different modes with various settings:** Each mode should sound different

**✅ Pass criteria:** All parameter combinations produce useful, stable results

---

## Step 4: Edge Case Testing

### 4.1 Extreme Parameter Values
**What to test:** Does the plugin handle extreme settings safely?

**Test extreme combinations:**

| Test | Settings | Expected Result |
|------|----------|-----------------|
| **Maximum everything** | All knobs at 100% | Should not crash or produce ear-damaging volumes |
| **Minimum everything** | All knobs at 0% | Should pass audio cleanly with no effect |
| **Maximum feedback** | Feedback at 100% | Should not create runaway feedback or infinite volume |
| **Mode switching** | Rapidly change mode knob | Should switch smoothly without clicks |

**⚠️ Safety note:** Use moderate listening levels for extreme tests!

### 4.2 Audio Input Testing
**What to test:** Does the plugin work with different types of audio?

**Test with different audio sources:**

| Audio Type | What to Listen For |
|------------|-------------------|
| **Sine wave** | Clean delay repeats, no distortion |
| **Drums** | Tight, rhythmic repeats |
| **Bass** | Low-end stays clean, no mud |
| **Vocals** | Intelligible repeats, natural sound |
| **White noise** | Consistent delay texture |
| **Silence** | No background noise or artifacts |

### 4.3 Rapid Parameter Changes
**What to test:** Can parameters be changed quickly without problems?

**Test procedure:**
1. **Rapid knob turns:** Turn knobs quickly while audio plays
2. **Parameter automation:** If your DAW supports it, automate rapid parameter changes
3. **Mode switching:** Rapidly switch between delay modes

**✅ Pass criteria:** No clicks, pops, or crashes during rapid changes

---

## Step 5: Performance and Stability Testing

### 5.1 Extended Runtime Test
**What to test:** Does the plugin remain stable over time?

**Test procedure:**
1. Load the plugin and start audio playback
2. Let it run for 10+ minutes with various parameter settings
3. Try different modes and parameter combinations
4. **Listen for:** Drift, noise buildup, or performance degradation

**✅ Pass criteria:** Plugin sounds identical after extended use

### 5.2 CPU Load Test
**What to test:** Does the plugin use reasonable CPU resources?

**Observation points:**
- **DAW CPU meter:** Should not spike excessively
- **Audio dropouts:** Should not cause stuttering
- **Multiple instances:** Can you run several copies simultaneously?

**Performance expectations:**
- Single instance should use <5% CPU on modern systems
- Should run smoothly alongside other plugins
- No audio dropouts during normal use

### 5.3 Memory Usage Test
**What to test:** Does the plugin manage memory correctly?

**Test procedure:**
1. Load and unload the plugin multiple times
2. Check if memory usage grows each time (memory leak)
3. Run multiple instances and check total memory usage

**Expected behavior:**
- Memory usage should be consistent across loads
- Multiple instances should use predictable memory amounts
- No memory leaks over time

---

## Step 6: User Experience Testing

### 6.1 Musical Usability Test
**What to test:** Is the plugin actually useful for making music?

**Test scenarios:**
1. **Vocal delay:** Add subtle delay to vocals
2. **Guitar slapback:** Short delay for guitar
3. **Drum echoes:** Delay on snare or clap
4. **Ambient textures:** Long delays with high feedback
5. **Rhythmic effects:** Tempo-synced delay patterns

**✅ Pass criteria:** Plugin enhances the music and feels natural to use

### 6.2 LED Feedback Test
**What to test:** Do LEDs provide useful visual feedback?

**Test each LED:**
1. **LED 1:** Should reflect delay time parameter
2. **LED 2:** Should reflect feedback parameter  
3. **LED 3:** Should reflect mix parameter
4. **LED 4:** Should show current mode

**✅ Pass criteria:** LEDs help you understand what the plugin is doing

### 6.3 Intuitive Operation Test
**What to test:** Can someone use the plugin without instructions?

**Test procedure:**
1. Have someone else try the plugin without explanation
2. Observe what they try to do
3. Note any confusion or unexpected behavior
4. Ask what they think each knob should do

**✅ Pass criteria:** Plugin operation is self-explanatory

---

## Step 7: Regression Testing

### 7.1 Create a Test Checklist
Create a standardized test that you can repeat each time you modify the plugin:

```
PLUGIN TEST CHECKLIST - Multi-Mode Delay

□ BASIC FUNCTIONALITY
  □ Audio passes through when effect is off
  □ Delay effect engages when parameters are changed
  □ All four knobs affect the sound appropriately

□ PARAMETER RANGES  
  □ Knob 1 (Delay Time): Smooth changes from short to long
  □ Knob 2 (Feedback): Clean to multiple repeats
  □ Knob 3 (Mix): Dry to wet balance works correctly
  □ Knob 4 (Mode): Four distinct delay modes audible

□ EDGE CASES
  □ Maximum feedback does not cause runaway or crashes
  □ All knobs at minimum: clean audio pass-through
  □ All knobs at maximum: stable, musical extreme effect
  □ Rapid parameter changes: no clicks or artifacts

□ STABILITY
  □ 10-minute runtime test: no drift or degradation
  □ Multiple plugin instances load without issues
  □ No memory leaks after repeated load/unload

□ VISUAL FEEDBACK
  □ All four LED displays respond to their respective parameters
  □ LED patterns are helpful for understanding plugin state

□ MUSICAL USABILITY
  □ Works well on vocal material
  □ Works well on drum material  
  □ Works well on harmonic material
  □ Parameter ranges are musically useful

OVERALL RESULT: □ PASS  □ FAIL
NOTES: ________________________________
```

### 7.2 Document Test Results
Keep a log of test results for each plugin version:

```
TEST LOG - Multi-Mode Delay

Version 1.0 - Initial Release
Date: [Current Date]
Result: PASS
Notes: All tests passed. Ready for use.

Version 1.1 - Added tape mode
Date: [Future Date]  
Result: FAIL - Mode 2 causes distortion at high feedback
Notes: Need to adjust tape saturation algorithm

Version 1.2 - Fixed tape saturation  
Date: [Future Date]
Result: PASS
Notes: Tape mode now stable at all settings
```

---

## Step 8: Testing Tools and Techniques

### 8.1 Test Audio Generation
Create standard test signals for consistent testing:

**For testing in your DAW:**
1. **Sine wave generator:** Test clean delay repeats
2. **White noise generator:** Test for artifacts
3. **Metronome/click track:** Test timing accuracy
4. **Silence:** Test for background noise

### 8.2 Parameter Testing Shortcuts
**Systematic parameter testing:**
```
1. Set all knobs to 0 (minimum)
2. Test knob 1: 0%, 25%, 50%, 75%, 100%
3. Reset knob 1, test knob 2: 0%, 25%, 50%, 75%, 100%
4. Continue for all knobs
5. Test key combinations
```

### 8.3 Automated Testing Ideas
**For advanced testing:**
- Use DAW automation to sweep parameters automatically
- Record parameter sweeps and compare different plugin versions
- Create test projects with different audio sources
- Set up template tests you can run quickly

---

## Step 9: Common Test Failures and Fixes

### 9.1 Parameter Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| **Knob does nothing** | Parameter not used in processing | Check parameter is read and applied |
| **Knob range too small** | Scaling factor too conservative | Increase parameter scaling range |
| **Knob range too extreme** | Scaling factor too aggressive | Reduce parameter scaling or add limits |
| **Dead zones in knob** | Integer precision issues | Use better scaling math |

### 9.2 Audio Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| **No audio output** | Not writing to signal[] arrays | Ensure signal[0] and signal[1] are set |
| **Distorted output** | Math overflow | Add clipping protection |
| **Clicks on parameter changes** | Sudden value jumps | Add parameter smoothing |
| **Background noise** | Uninitialized buffers | Initialize arrays to zero |

### 9.3 Stability Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| **Plugin crashes** | Array bounds violation | Add bounds checking to all array access |
| **Runaway feedback** | Unconstrained feedback loop | Limit feedback amounts and add clipping |
| **Performance issues** | Too much computation | Optimize algorithms, reduce unnecessary math |

---

## Step 10: Release Checklist

### 10.1 Pre-Release Validation
Before sharing your plugin with others:

```
□ Complete test checklist passes 100%
□ Plugin tested on different audio sources
□ Parameter ranges are musical and intuitive  
□ LED feedback is helpful and accurate
□ No crashes under any parameter settings
□ Performance is acceptable for normal use
□ Documentation/instructions are clear
```

### 10.2 Beta Testing
Consider having others test your plugin:
- **Fresh ears:** Others will find issues you missed
- **Different use cases:** Others may use it differently than intended
- **Different systems:** Test on different DAWs and computers

### 10.3 Version Control
Keep track of plugin versions:
- **Number your versions:** v1.0, v1.1, etc.
- **Document changes:** What changed between versions
- **Keep test results:** Track which versions passed which tests
- **Archive working versions:** Don't lose a working version

---

## You're Now a Plugin Testing Expert!

### What You Learned:
- ✅ **Systematic testing methodology** for any plugin
- ✅ **Edge case identification** and testing
- ✅ **Performance and stability validation**
- ✅ **User experience testing** techniques
- ✅ **Test documentation** and regression testing
- ✅ **Common failure patterns** and their fixes

### Apply This to Every Plugin:
1. **Test early and often** - Don't wait until the end
2. **Be systematic** - Use checklists to ensure thorough testing
3. **Test edge cases** - Users will find the extreme settings
4. **Document your tests** - Know what works and what doesn't
5. **Get feedback** - Others will use your plugin differently

**Your plugins will now be reliable, stable, and ready for real-world use!** Good testing is what separates professional plugins from bedroom experiments.
