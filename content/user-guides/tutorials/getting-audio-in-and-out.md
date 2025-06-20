# Getting Audio In and Out - Your First Working Plugin

## What This Tutorial Does
Create the simplest possible working plugin that proves your Permut8 setup is working. In just 10 minutes, you'll have audio passing through your own custom firmware and understand the basic structure every plugin needs.

## What You'll Learn
- Essential plugin structure that every firmware needs
- How audio flows into and out of your plugin
- The minimal code required for a working plugin
- How to verify your development environment is working
- Foundation concepts for all future plugin development

**Prerequisites**: None - this is your starting point!  
**Time Required**: 10 minutes  
**Difficulty**: Absolute Beginner

---

## Step 1: Understanding the Goal

### 1.1 What We're Building
A plugin that:
- ✅ Loads successfully into Permut8
- ✅ Passes audio through unchanged
- ✅ Proves your development environment works
- ✅ Gives you the foundation for all future plugins

### 1.2 Success Criteria
**When this tutorial is complete:**
- You hear audio playing through your custom plugin
- The audio sounds identical to the original (no changes)
- You understand the basic structure every plugin needs
- You're ready to start modifying and creating effects

---

## Step 2: Create Your First Plugin

### 2.1 The Absolute Minimum Code
Create a new text file called `audio_passthrough.impala`:

```impala
// My First Plugin - Audio Passthrough
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

function process()
locals int inputL, int inputR
{
    loop {
        // Audio automatically passes through - we don't need to do anything!
        yield()
    }
}
```

### 2.2 Understanding Each Line

**Line 1: Comment**
```impala
// My First Plugin - Audio Passthrough
```
- Comments start with `//` and help you remember what your code does
- Always document your plugins for future reference

**Line 2: Format Declaration**
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2
```
- **REQUIRED** - tells Permut8 this is a valid plugin
- Must be exactly this line in every plugin you create
- Version 2 is for Permut8 v1.1 and later

**Lines 4-6: Global Variables**
```impala
global array signal[2]      // Audio input and output
global array params[PARAM_COUNT]      // Knob values from hardware
global array displayLEDs[4] // LED display control
```
- **REQUIRED** - these connect your plugin to Permut8 hardware
- `signal[2]` = left and right audio channels
- `params[PARAM_COUNT]` = values from 8 knobs (we'll use these later)
- `displayLEDs[4]` = control for LED displays (we'll use these later)

**Lines 8-14: Main Processing Function**
```impala
function process()
{
    loop {
        // Audio automatically passes through
        yield()
    }
}
```
- **REQUIRED** - this function runs continuously while your plugin is active
- `loop { }` = infinite loop that processes audio forever
- `yield()` = **CRITICAL** - gives control back to Permut8 after each audio sample
- Audio passes through automatically - you don't need to copy it manually

---

## Step 3: Compile and Test

### 3.1 Compile Your Plugin
1. Open command prompt in your Permut8 Firmware Code directory
2. Type: `PikaCmd.exe -compile audio_passthrough.impala`
3. **Expected result**: You should see `audio_passthrough.gazl` created
4. **If compilation fails**: Check that you typed the code exactly as shown

### 3.2 Load Into Permut8
1. Open your DAW with Permut8 loaded
2. Click the **console button** (bottom-right of Permut8 interface)
3. In the console, type: `patch audio_passthrough.gazl`
4. Press Enter

### 3.3 Test Audio Passthrough
1. **Play audio** through Permut8 (any audio source will work)
2. **Expected result**: You should hear the audio exactly as it was before
3. **Success indicator**: Audio plays normally with no changes
4. **If no audio**: Check your DAW routing and Permut8 input/output settings

**🎉 Congratulations!** You just created and loaded your first custom Permut8 plugin!

---

## Step 4: Understanding What Just Happened

### 4.1 The Audio Flow
```
Audio Input → Your Plugin → Audio Output
```

**Behind the scenes:**
1. Permut8 receives audio from your DAW
2. Permut8 puts audio samples into `signal[0]` (left) and `signal[1]` (right)
3. Your `process()` function runs once per audio sample
4. Since you didn't change `signal[0]` or `signal[1]`, audio passes through unchanged
5. Permut8 sends the audio back to your DAW

### 4.2 The Real-Time Loop
```impala
loop {
    // This runs 44,100 times per second (at 44.1kHz sample rate)
    // Each time, it processes one audio sample
    yield()  // Give control back so next sample can be processed
}
```

**Key concept:** Your plugin processes one tiny audio sample at a time, 44,100 times per second. The `yield()` is essential - without it, your plugin would hang and no audio would play.

### 4.3 Why This Matters
**This simple structure is the foundation for EVERY plugin:**
- Want to make a volume control? Modify `signal[0]` and `signal[1]` before `yield()`
- Want to add delay? Store samples in a buffer before outputting them
- Want to add distortion? Apply math to the signal values
- Want LED feedback? Set values in `displayLEDs[]`

---

## Step 5: Make a Simple Modification

### 5.1 Add a Volume Control
Let's prove you can modify audio. Replace your `process()` function:

```impala
function process()
locals int inputL, int inputR
{
    loop {
        // Reduce volume to half (simple volume control)
        signal[0] = signal[0] / 2  // Left channel half volume
        signal[1] = signal[1] / 2  // Right channel half volume
        
        yield()
    }
}
```

### 5.2 Test the Volume Control
1. **Compile**: `PikaCmd.exe -compile audio_passthrough.impala`
2. **Load**: `patch audio_passthrough.gazl`
3. **Expected result**: Audio should now be quieter (half volume)
4. **Success indicator**: Clear volume reduction while maintaining audio quality

### 5.3 Understanding the Change
```impala
signal[0] = signal[0] / 2  // Take left audio, divide by 2, put it back
signal[1] = signal[1] / 2  // Take right audio, divide by 2, put it back
```

**What this does:**
- Reads the current audio sample from `signal[0]` (left channel)
- Divides it by 2 (making it half as loud)
- Puts the modified sample back into `signal[0]`
- Does the same for the right channel
- Audio flows out to your DAW with reduced volume

---

## Step 6: Add LED Feedback

### 6.1 Visual Confirmation Your Plugin Is Running
Add this line before `yield()`:

```impala
function process()
locals int inputL, int inputR
{
    loop {
        signal[0] = signal[0] / 2
        signal[1] = signal[1] / 2
        
        // Light up first LED to show plugin is active
        displayLEDs[0] = 0xFF  // 0xFF = all LEDs on in first display
        
        yield()
    }
}
```

### 6.2 Test LED Feedback
1. **Compile and load** as before
2. **Expected result**: First LED display should light up fully
3. **Success indicator**: Visual confirmation your plugin is running

### 6.3 Understanding LED Control
```impala
displayLEDs[0] = 0xFF  // First LED display, all 8 LEDs on
```

**LED values:**
- `0x00` = all LEDs off
- `0x01` = only first LED on
- `0xFF` = all 8 LEDs on
- `0x0F` = first 4 LEDs on
- You have 4 LED displays: `displayLEDs[0]` through `displayLEDs[3]`

---

## Step 7: Complete Working Plugin

### 7.1 Final Version with Comments
Here's your complete first plugin with full documentation:

```impala
// Audio Passthrough with Volume Control - My First Plugin
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

// Required global variables that connect to Permut8 hardware
global array signal[2]      // Audio I/O: signal[0] = left, signal[1] = right
global array params[PARAM_COUNT]      // Knob values: params[0] through params[7] (0-255 each)
global array displayLEDs[4] // LED displays: displayLEDs[0] through displayLEDs[3]

// Main processing function - runs continuously while plugin is active
function process()
locals int inputL, int inputR
{
    loop {
        // Process audio: reduce volume to half
        signal[0] = signal[0] / 2  // Left channel volume control
        signal[1] = signal[1] / 2  // Right channel volume control
        
        // Visual feedback: light up LED to show plugin is running
        displayLEDs[0] = 0xFF      // All LEDs on in first display
        
        // CRITICAL: Return control to Permut8 for next audio sample
        yield()
    }
}
```

### 7.2 What You've Accomplished
✅ **Created a working plugin** that modifies audio in real-time  
✅ **Understood the basic structure** every plugin needs  
✅ **Modified audio samples** with simple mathematical operations  
✅ **Added visual feedback** with LED control  
✅ **Verified your development environment** is working correctly  

---

## Step 8: What's Next

### 8.1 You Now Know
**Essential Concepts:**
- Every plugin needs the same basic structure
- Audio flows through `signal[0]` and `signal[1]`
- `yield()` is required for real-time operation
- You can modify audio with simple math
- LEDs provide visual feedback

**Foundation Skills:**
- Compiling plugins with PikaCmd
- Loading plugins into Permut8
- Testing audio modifications
- Basic audio sample manipulation

### 8.2 Ready For Next Steps
**Build on this foundation:**
- 📖 [Make Your First Sound](make-your-first-sound.md) - Generate audio instead of just modifying it
- 📖 [Control Something with Knobs](control-something-with-knobs.md) - Use hardware knobs to control your effects
- 📖 [Light Up LEDs](light-up-leds.md) - Advanced LED patterns and feedback
- 📖 [Build Your First Filter](build-your-first-filter.md) - Create your first real audio effect

### 8.3 Experiment Ideas
**Try these modifications:**
```impala
// Different volume levels
signal[0] = signal[0] * 2    // Double volume (be careful - can be loud!)
signal[0] = signal[0] / 4    // Quarter volume

// Mute one channel
signal[0] = 0               // Mute left channel
signal[1] = signal[1]       // Keep right channel

// Swap left and right
int temp = signal[0]
signal[0] = signal[1]       // Left gets right audio
signal[1] = temp            // Right gets left audio

// Different LED patterns
displayLEDs[0] = 0x01       // Only first LED
displayLEDs[0] = 0xAA       // Alternating LEDs (10101010)
displayLEDs[0] = 0x0F       // First 4 LEDs
```

**🎉 You're now ready to start creating real audio effects!** Every complex plugin starts with these same basic concepts - you've mastered the foundation.