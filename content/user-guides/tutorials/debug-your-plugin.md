# Debug Your Plugin - Complete Troubleshooting Guide

## What This Tutorial Does
Learn systematic debugging techniques for Permut8 plugins. We'll create a deliberately broken plugin, then fix it step by step, teaching you how to identify and solve the most common problems.

## Common Problems We'll Solve
- Plugin won't compile
- Plugin loads but no sound comes through
- Plugin makes horrible noises
- Controls don't work
- LEDs don't respond
- Performance issues and dropouts

---

## Step 1: Create a Broken Plugin (On Purpose!)

### 1.1 The "Broken" Reverb
Create `broken_reverb.impala` with these deliberate mistakes:

```impala
// Broken Reverb - Full of Common Mistakes!
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required parameter constants
const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT


global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

// Delay buffers for reverb
global array delayBuffer1[500]
global array delayBuffer2[750]
global array delayBuffer3[1000]
global int delayIndex = 0

// Missing global for output buffer!
// global array outputBuffer[2]

function process()
{
    loop {
        // BUG 1: Not reading parameters correctly
        int roomSize = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]    // Should be scaled
        int decay = (int)global params[OPERAND_1_LOW_PARAM_INDEX]       // Should be limited
        
        // BUG 2: Delay index not bounded
        delayIndex = delayIndex + 1  // Will overflow!
        
        // BUG 3: Array access without bounds checking
        int delay1 = delayBuffer1[delayIndex]
        int delay2 = delayBuffer2[delayIndex]  
        int delay3 = delayBuffer3[delayIndex]
        
        // BUG 4: Math that can overflow
        int reverb = delay1 * decay + delay2 * decay + delay3 * decay
        
        // BUG 5: Not storing new samples in delay buffers
        // (reverb will be silent after initial buffer contents are used)
        
        // BUG 6: Output without proper clipping
        signal[0] = signal[0] + reverb  // Can overflow
        signal[1] = signal[1] + reverb
        
        // BUG 7: Missing yield()!
    }
}

```

### 1.2 Try to Compile the Broken Plugin
1. Save the file and try: `PikaCmd.exe -compile broken_reverb.impala`
2. **You should get compilation errors!** This is normal - we'll fix them step by step.

---

## Step 2: Fix Compilation Errors

### 2.1 Read the Error Messages
When compilation fails, PikaCmd gives you specific error messages. Common ones:

- **"Undefined variable"** - You used a variable you didn't declare
- **"Missing semicolon"** - Forgot a semicolon somewhere
- **"Unexpected token"** - Syntax error (wrong brackets, etc.)
- **"Array index out of bounds"** - Tried to access an array element that doesn't exist

### 2.2 Fix the Missing yield()
The most common error: **missing `yield()`**. Add it:

```impala
function process()
{
    loop {
        // ... all the same buggy code ...
        
        // BUG 7 FIX: Add missing yield()
        yield()
    }
}
```

### 2.3 Fix Syntax Errors
If you still get compilation errors, check these common issues:

```impala
// WRONG: Missing semicolon
int value = 42
int other = 24

// RIGHT: Every statement needs semicolon
int value = 42;
int other = 24;

// WRONG: Mismatched brackets
if (condition {
    // code
}

// RIGHT: Matching brackets
if (condition) {
    // code
}
```

### 2.4 Compile Again
Fix any syntax errors and compile until you get `broken_reverb.gazl` successfully created.

**Success!** Compilation passed, but the plugin is still broken. Let's fix the runtime issues.

---

## Step 3: Fix "No Sound" Problems

### 3.1 Load and Test
1. Load: `patch broken_reverb.gazl`
2. **Problem:** No sound comes through, or very quiet sound

### 3.2 Debugging "No Sound" Issues

**Check 1: Are you calling yield()?**
```impala
// If you don't call yield(), the plugin hangs
function process() {
    loop {
        // ... processing code ...
        yield();  // MUST be here!
    }
}
```

**Check 2: Are you preserving the signal?**
```impala
// WRONG: This destroys the input signal
signal[0] = someEffect;

// RIGHT: This adds effect to the original signal
signal[0] = signal[0] + someEffect;
// OR mix them:
signal[0] = (signal[0] * dryAmount + someEffect * wetAmount) / 255;
```

**Check 3: Are you writing to both channels?**
```impala
// WRONG: Only left channel has sound
signal[0] = processedAudio;
// signal[1] forgotten!

// RIGHT: Both channels
signal[0] = processedAudio;
signal[1] = processedAudio;  // Same or different processing
```

### 3.3 Quick Fix for Our Broken Reverb
Replace the signal output lines:

```impala
// BUG 6 FIX: Proper mixing and clipping
int mixedLeft = signal[0] + (reverb / 4);    // Reduce reverb level
int mixedRight = signal[1] + (reverb / 4);

// Clip to prevent overflow
if (mixedLeft > 2047) mixedLeft = 2047;
else if (mixedLeft < -2047) mixedLeft = -2047;
if (mixedRight > 2047) mixedRight = 2047;
else if (mixedRight < -2047) mixedRight = -2047;

signal[0] = mixedLeft;
signal[1] = mixedRight;
```

---

## Step 4: Fix Array Access Crashes

### 4.1 The Problem: Array Bounds
Our broken reverb will crash because `delayIndex` grows without limit and accesses memory outside the arrays.

### 4.2 Debug Array Access
**Always wrap array indices:**

```impala
// WRONG: Index grows forever
delayIndex = delayIndex + 1;
int sample = delayBuffer1[delayIndex];  // CRASH when delayIndex > 499

// RIGHT: Wrap index to array size
delayIndex = (delayIndex + 1) % 500;    // Always stays 0-499
int sample = delayBuffer1[delayIndex];  // Safe
```

### 4.3 Fix Our Reverb's Array Access
Replace the delay buffer access:

```impala
// BUG 2 FIX: Properly wrap delay index
delayIndex = (delayIndex + 1) % 500;    // Keep in bounds

// BUG 3 FIX: Safe array access with different indices
int delay1 = delayBuffer1[delayIndex];
int delay2 = delayBuffer2[delayIndex % 750];   // Wrap to buffer 2 size
int delay3 = delayBuffer3[delayIndex % 1000];  // Wrap to buffer 3 size
```

### 4.4 General Array Safety Rules
```impala
// ALWAYS check array bounds
if (index < 0) index = 0;
if (index >= arraySize) index = arraySize - 1;

// OR use modulo for circular access
index = index % arraySize;

// OR use safe accessor functions
int safeRead(array buffer[], int size, int index) {
    return buffer[index % size];
}
```

---

## Step 5: Fix Math Overflow Issues

### 5.1 The Problem: Integer Overflow
Audio calculations can easily overflow Impala's integer range, causing distortion or wrapping.

### 5.2 Identify Overflow Sources
```impala
// DANGEROUS: Can overflow easily
int result = bigValue1 * bigValue2;

// SAFER: Scale before multiplying
int result = (bigValue1 / 2) * (bigValue2 / 2);

// SAFEST: Check ranges
int result = bigValue1 * bigValue2;
if (result > 2047) result = 2047;
else if (result < -2047) result = -2047;
```

### 5.3 Fix Our Reverb's Math
Replace the reverb calculation:

```impala
// BUG 4 FIX: Prevent overflow in math
// Scale decay parameter to safe range
int safeDecay = decay / 4;  // Limit multiplier

// Safe reverb calculation with scaling
int reverb = ((delay1 * safeDecay) + (delay2 * safeDecay) + (delay3 * safeDecay)) / 255;

// Additional safety clipping
if (reverb > 1000) reverb = 1000;
else if (reverb < -1000) reverb = -1000;
```

---

## Step 6: Fix Missing Functionality

### 6.1 The Problem: Silent Effect
Our reverb will go silent quickly because we're not feeding new audio into the delay buffers.

### 6.2 Debug Missing Functionality
**Always ask: "Where does the processed audio come from?"**

For reverb:
1. New audio goes into delay buffers
2. Old audio comes out of delay buffers  
3. Multiple delay buffers create reverb effect

### 6.3 Fix Our Reverb's Missing Input
Add after reading the delay buffers:

```impala
// BUG 5 FIX: Store new audio in delay buffers
delayBuffer1[delayIndex] = signal[0] + (delay2 / 8);        // Input + some feedback
delayBuffer2[delayIndex % 750] = signal[0] + (delay3 / 8);  // Different mixing
delayBuffer3[delayIndex % 1000] = signal[0] + (delay1 / 8); // Create reverb network
```

### 6.4 General Debugging Questions
- **Where does processed audio come from?**
- **Is the effect state being updated each sample?**
- **Are feedback paths connected correctly?**
- **Is the algorithm actually doing what you think it does?**

---

## Step 7: Fix Parameter Issues

### 7.1 The Problem: Raw Parameter Values
Parameters come in as 0-255 but need to be scaled for different uses.

### 7.2 Debug Parameter Scaling
```impala
// WRONG: Raw parameter value
int feedback = (int)global params[OPERAND_1_LOW_PARAM_INDEX];           // 0-255, often too much
effect = input * feedback;          // Huge multiplication!

// RIGHT: Scale to useful range
int feedback = (int)global params[OPERAND_1_LOW_PARAM_INDEX] / 4;       // 0-63, safer range
effect = (input * feedback) / 64;  // Controlled multiplication
```

### 7.3 Fix Our Reverb's Parameters
Replace the parameter reading:

```impala
// BUG 1 FIX: Properly scale parameters
int roomSize = (int)global params[OPERAND_1_HIGH_PARAM_INDEX] / 2;       // 0-127 range
int decay = (int)global params[OPERAND_1_LOW_PARAM_INDEX] / 4;          // 0-63 range for safety
```

---

## Step 8: Complete Fixed Version

### 8.1 The Corrected Reverb
Here's our reverb with all bugs fixed:

```impala
// Fixed Reverb - All Problems Solved!
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

global array delayBuffer1[500]
global array delayBuffer2[750]
global array delayBuffer3[1000]
global int delayIndex = 0

function process()
{
    loop {
        // FIX 1: Properly scale parameters
        int roomSize = (int)global params[OPERAND_1_HIGH_PARAM_INDEX] / 2;       // 0-127 range
        int decay = (int)global params[OPERAND_1_LOW_PARAM_INDEX] / 4;          // 0-63 range for safety
        
        // FIX 2: Bound delay index  
        delayIndex = (delayIndex + 1) % 500;
        
        // FIX 3: Safe array access with proper indices
        int delay1 = delayBuffer1[delayIndex];
        int delay2 = delayBuffer2[delayIndex % 750];
        int delay3 = delayBuffer3[delayIndex % 1000];
        
        // FIX 5: Store new audio in delay buffers (reverb network)
        delayBuffer1[delayIndex] = signal[0] + (delay2 * decay / 255);
        delayBuffer2[delayIndex % 750] = signal[0] + (delay3 * decay / 255);
        delayBuffer3[delayIndex % 1000] = signal[0] + (delay1 * decay / 255);
        
        // FIX 4: Safe reverb calculation  
        int reverb = ((delay1 + delay2 + delay3) * roomSize) / 255;
        
        // Additional safety clipping
        if (reverb > 1000) reverb = 1000;
        else if (reverb < -1000) reverb = -1000;
        
        // FIX 6: Proper mixing and clipping
        int mixedLeft = signal[0] + (reverb / 4);
        int mixedRight = signal[1] + (reverb / 4);
        
        if (mixedLeft > 2047) mixedLeft = 2047;
        else if (mixedLeft < -2047) mixedLeft = -2047;
        if (mixedRight > 2047) mixedRight = 2047;
        else if (mixedRight < -2047) mixedRight = -2047;
        
        signal[0] = mixedLeft;
        signal[1] = mixedRight;
        
        // LED feedback for debugging
        displayLEDs[0] = (reverb > 100 || reverb < -100) ? 0xFF : 0x01;
        
        // FIX 7: Always call yield()
        yield();
    }
}
```

### 8.2 Test the Fixed Version
1. Compile: `PikaCmd.exe -compile broken_reverb.impala`
2. Load: `patch broken_reverb.gazl`  
3. **Should work now!** Try both knobs to control room size and decay.

---

## Step 9: Systematic Debugging Process

### 9.1 The Debug Checklist
When your plugin doesn't work, follow this order:

**1. Compilation Issues:**
- [ ] Missing semicolons?
- [ ] Bracket mismatches?
- [ ] Undefined variables?
- [ ] Correct function signatures?

**2. No Sound Issues:**
- [ ] Is `yield()` called in the main loop?
- [ ] Are you writing to `signal[0]` and `signal[1]`?
- [ ] Are you preserving input audio?
- [ ] Is the effect level reasonable?

**3. Crash/Noise Issues:**
- [ ] Array bounds checking?
- [ ] Math overflow protection?
- [ ] Parameter scaling?
- [ ] Initialization of variables?

**4. Control Issues:**
- [ ] Reading correct parameter indices?
- [ ] Scaling parameters to useful ranges?
- [ ] LED feedback working?

### 9.2 Debug by Elimination
**Start Simple:**
```impala
// Test 1: Just pass audio through
signal[0] = signal[0];
signal[1] = signal[1];
yield();
// If this doesn't work, you have basic setup issues

// Test 2: Add simple effect
signal[0] = signal[0] / 2;  // Half volume
signal[1] = signal[1] / 2;
yield();
// If this works, your effect processing has the problem

// Test 3: Add one parameter
int volume = (int)global params[OPERAND_1_HIGH_PARAM_INDEX] / 2;
signal[0] = (signal[0] * volume) / 128;
signal[1] = (signal[1] * volume) / 128;
yield();
// If this works, parameter scaling is correct
```

**Build Up Complexity Gradually:**
1. Get basic audio passing through
2. Add simple effect  
3. Add first parameter
4. Add more parameters
5. Add LED feedback
6. Add advanced features

### 9.3 Common Debugging Tricks

**Use LEDs for Debugging:**
```impala
// Show parameter values
displayLEDs[0] = (int)global params[OPERAND_1_HIGH_PARAM_INDEX];

// Show if processing is happening
displayLEDs[1] = (signal[0] > 100) ? 0xFF : 0x00;

// Show internal state
displayLEDs[2] = internalVariable % 256;
```

**Add Safety Everywhere:**
```impala
// Clip all audio outputs
if (output > 2047) output = 2047;
else if (output < -2047) output = -2047;

// Bound all array access
index = index % arraySize;

// Scale all parameters
param = (int)global params[OPERAND_1_HIGH_PARAM_INDEX] / scaleFactor;
```

---

## Step 10: Performance Debugging

### 10.1 Identify Performance Problems
**Symptoms:**
- Audio dropouts or stuttering
- Plugin causes DAW to slow down
- Clicks and pops in audio

### 10.2 Common Performance Issues

**Too Much Math:**
```impala
// SLOW: Complex math every sample
int result = sqrt(value1 * value1 + value2 * value2);

// FAST: Approximate or use lookup tables
int result = fastApproximateDistance(value1, value2);
```

**Large Array Operations:**
```impala
// SLOW: Processing huge arrays every sample
int i;
for (i = 0 to 10000) {
    bigArray[i] = bigArray[i] * 2;
}

// FAST: Process smaller chunks or fewer operations
```

**Unnecessary Calculations:**
```impala
// SLOW: Recalculating constants
int coefficient = ((int)global params[OPERAND_1_HIGH_PARAM_INDEX] * 3.14159) / 255;  // Every sample!

// FAST: Calculate only when parameter changes
static int lastParam = -1;
static int coefficient = 0;
if ((int)global params[OPERAND_1_HIGH_PARAM_INDEX] != lastParam) {
    coefficient = ((int)global params[OPERAND_1_HIGH_PARAM_INDEX] * 314) / 255;  // Use integer approximation
    lastParam = (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
}
```

### 10.3 Performance Optimization Tips
- **Use integer math** instead of floating point
- **Pre-calculate lookup tables** for complex functions
- **Only update when parameters change**
- **Limit array sizes** to what you actually need
- **Use bit shifts** instead of multiplication by powers of 2

---

## Quick Reference: Problem → Solution

| Problem | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| **Won't compile** | Syntax error | Check semicolons, brackets, variable names |
| **No sound** | Missing `yield()` or not writing to `signal[]` | Add `yield()`, write to both channels |
| **Distorted/noisy** | Math overflow | Add clipping, scale parameters |
| **Crashes** | Array bounds | Use modulo `%` for array access |
| **Controls don't work** | Parameter scaling | Scale `params[]` to useful ranges |
| **LEDs don't work** | Wrong values | Ensure LED values are 0-255 |
| **Performance issues** | Too much computation | Optimize math, use lookup tables |

## You're Now a Plugin Debugging Expert!

You learned:
- ✅ **Systematic debugging process** from compilation to performance
- ✅ **Most common mistakes** and how to avoid them
- ✅ **Safety patterns** for robust plugin development
- ✅ **Performance optimization** techniques
- ✅ **Debug-by-elimination** methodology

**These skills apply to ANY plugin you build!** Follow the checklist, build complexity gradually, and use LEDs for debugging feedback.
