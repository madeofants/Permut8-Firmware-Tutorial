# Simple Delay Explained - Step-by-Step Tutorial

## What This Tutorial Does
Learn how delays work by building one from scratch. We'll start with the simplest possible delay and gradually add features, explaining every concept along the way. By the end, you'll understand how all time-based effects work.

## What You'll Learn
- How digital delays store and retrieve audio
- Circular buffer concepts and implementation
- Memory management for audio effects
- Parameter control for musical delays
- The foundation for reverb, chorus, and all time-based effects

**Prerequisites**: Basic Impala syntax  
**Time Required**: 30-45 minutes  
**Difficulty**: Beginner

---

## Step 1: Understanding How Delays Work

### 1.1 The Basic Concept
A delay effect is like an audio tape recorder that plays back what you recorded a moment ago:

```
Input Audio --> [Store in Memory] --> [Wait Some Time] --> [Play Back] --> Output
                     ^                                                      |
                     |                                                      |
                     +------------------ Mix with Input ------------------+
```

### 1.2 Digital Implementation
In digital audio, we store samples in an array and read them back later:

```impala
// Conceptual delay (not working code yet)
global array delayBuffer[1000]    // Store 1000 samples
global int writePosition = 0      // Where to write new audio
global int readPosition = 500     // Where to read old audio (500 samples ago)

// Each audio sample:
delayBuffer[writePosition] = currentInput    // Store current audio
delayedOutput = delayBuffer[readPosition]    // Get old audio
```

### 1.3 The Challenge: Circular Buffers
What happens when we reach the end of the array? We need to wrap around to the beginning:

```impala
// Without wrapping: CRASHES when position > 999
writePosition = writePosition + 1
delayBuffer[writePosition] = input  // CRASH when writePosition = 1000!

// With wrapping: Safe circular buffer
writePosition = (writePosition + 1) % 1000
delayBuffer[writePosition] = input  // Always stays 0-999
```

---

## Step 2: Build the Simplest Delay

### 2.1 Create Basic Structure
Create `simple_delay.impala`:

```impala
// ===== STANDARD PERMUT8 CONSTANTS =====

// Parameter System Constants
const int PARAM_MAX = 255                    // Maximum knob/parameter value (8-bit)
const int PARAM_MIN = 0                      // Minimum knob/parameter value
const int PARAM_MID = 128                    // Parameter midpoint for bipolar controls
const int PARAM_SWITCH_THRESHOLD = 127       // Boolean parameter on/off threshold

// Audio Sample Range Constants (12-bit signed audio)
const int AUDIO_MAX = 2047                   // Maximum audio sample value (+12-bit)
const int AUDIO_MIN = -2047                  // Minimum audio sample value (-12-bit)
const int AUDIO_ZERO = 0                     // Audio silence/center value

// Sample Rate Constants
const int SAMPLE_RATE_44K1 = 44100          // Standard audio sample rate (Hz)
const int SAMPLE_RATE_HALF = 22050          // Half sample rate (0.5 second buffer at 44.1kHz)
const int SAMPLE_RATE_QUARTER = 11025       // Quarter sample rate (0.25 second buffer)

// Audio Scaling Constants (16-bit ranges for phase accumulators)
const int AUDIO_FULL_RANGE = 65536          // 16-bit full scale range (0-65535)
const int AUDIO_HALF_RANGE = 32768          // 16-bit half scale (bipolar center)
const int AUDIO_QUARTER_RANGE = 16384       // 16-bit quarter scale (triangle wave peaks)

// Mathematical Constants
const float PI = 3.14159265                 // Mathematical pi constant
const float TWO_PI = 6.28318531             // 2 * pi (full circle radians)
const float PI_OVER_2 = 1.57079633          // pi/2 (quarter circle radians)

// Buffer Size Constants (powers of 2 for efficiency)
const int SMALL_BUFFER = 128                // Small buffer size
const int MEDIUM_BUFFER = 512               // Medium buffer size  
const int LARGE_BUFFER = 1024               // Large buffer size
const int MAX_BUFFER = 2048                 // Maximum buffer size

// Bit Manipulation Constants
const int BITS_PER_BYTE = 8                 // Standard byte size
const int SHIFT_DIVIDE_BY_2 = 1             // Bit shift for divide by 2
const int SHIFT_DIVIDE_BY_4 = 2             // Bit shift for divide by 4
const int SHIFT_DIVIDE_BY_8 = 3             // Bit shift for divide by 8

// LED Display Constants
const int LED_OFF = 0x00                    // All LEDs off
const int LED_ALL_ON = 0xFF                 // All 8 LEDs on
const int LED_SINGLE = 0x01                 // Single LED pattern
const int LED_DOUBLE = 0x03                 // Two LED pattern
const int LED_QUAD = 0x0F                   // Four LED pattern
const int LED_BRIGHTNESS_FULL = 255         // Full LED brightness
const int LED_BRIGHTNESS_HALF = 127         // Half LED brightness

// Musical/Timing Constants
const int STANDARD_BPM = 120                // Standard tempo reference
const int QUARTER_NOTE_DIVISIONS = 4        // Divisions per quarter note
const int SEMITONES_PER_OCTAVE = 12         // Musical semitones in octave
const float A4_FREQUENCY = 440.0            // A4 reference frequency (Hz)

// Simple Delay - Step by Step
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

global int clock = 0
global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clockFreqLimit = 132300

// Delay buffer - SAMPLE_RATE_HALF samples (timing varies with sample rate)
global array delayBuffer[SAMPLE_RATE_HALF]
global int bufferPosition = 0

function process()
locals int input, int readPosition, int delayed, int mixed
{
    loop {
        // Step 1: Get input audio
        input = signal[0]
        
        // Step 2: Store input in delay buffer
        delayBuffer[bufferPosition] = input
        
        // Step 3: Calculate where to read delayed audio from
        // Read from SAMPLE_RATE_QUARTER samples ago (0.25 seconds ago)
        readPosition = (bufferPosition - SAMPLE_RATE_QUARTER + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF
        
        // Step 4: Get delayed audio
        delayed = delayBuffer[readPosition]
        
        // Step 5: Mix input and delayed audio (50/50 mix)
        mixed = (input + delayed) / 2
        
        // Step 6: Output mixed audio
        signal[0] = mixed
        signal[1] = mixed  // Same for both channels
        
        // Step 7: Move to next buffer position (circular)
        bufferPosition = (bufferPosition + 1) % SAMPLE_RATE_HALF
        
        yield()
    }
}
```

### 2.2 Test the Basic Delay
1. Compile: `PikaCmd.exe -compile simple_delay.impala`
2. Load: `patch simple_delay.gazl`
3. **You should hear a 0.25-second delay echo!**

### 2.3 Understanding the Math
**Why `(bufferPosition - SAMPLE_RATE_QUARTER + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF`?**

```impala
// Problem: Simple subtraction can go negative
int readPos = bufferPosition - SAMPLE_RATE_QUARTER  // NEGATIVE when bufferPosition < SAMPLE_RATE_QUARTER!

// Solution: Add buffer size before modulo
int readPos = (bufferPosition - SAMPLE_RATE_QUARTER + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF

// Examples:
// bufferPosition = 5000, want to read SAMPLE_RATE_QUARTER behind:
// (5000 - SAMPLE_RATE_QUARTER + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF = 16025 % SAMPLE_RATE_HALF = 16025 ✓

// bufferPosition = 15000, want to read SAMPLE_RATE_QUARTER behind:  
// (15000 - SAMPLE_RATE_QUARTER + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF = 25975 % SAMPLE_RATE_HALF = 3925 ✓
```

---

## Step 3: Add Controllable Delay Time

### 3.1 Map Parameter to Delay Time
Replace the process function with this enhanced version:

```impala
// ===== STANDARD PERMUT8 CONSTANTS =====

// Parameter System Constants
const int PARAM_MAX = 255                    // Maximum knob/parameter value (8-bit)
const int PARAM_MIN = 0                      // Minimum knob/parameter value
const int PARAM_MID = 128                    // Parameter midpoint for bipolar controls
const int PARAM_SWITCH_THRESHOLD = 127       // Boolean parameter on/off threshold

// Audio Sample Range Constants (12-bit signed audio)
const int AUDIO_MAX = 2047                   // Maximum audio sample value (+12-bit)
const int AUDIO_MIN = -2047                  // Minimum audio sample value (-12-bit)
const int AUDIO_ZERO = 0                     // Audio silence/center value

// Sample Rate Constants
const int SAMPLE_RATE_44K1 = 44100          // Standard audio sample rate (Hz)
const int SAMPLE_RATE_HALF = 22050          // Half sample rate (0.5 second buffer at 44.1kHz)
const int SAMPLE_RATE_QUARTER = 11025       // Quarter sample rate (0.25 second buffer)

// Audio Scaling Constants (16-bit ranges for phase accumulators)
const int AUDIO_FULL_RANGE = 65536          // 16-bit full scale range (0-65535)
const int AUDIO_HALF_RANGE = 32768          // 16-bit half scale (bipolar center)
const int AUDIO_QUARTER_RANGE = 16384       // 16-bit quarter scale (triangle wave peaks)

// Mathematical Constants
const float PI = 3.14159265                 // Mathematical pi constant
const float TWO_PI = 6.28318531             // 2 * pi (full circle radians)
const float PI_OVER_2 = 1.57079633          // pi/2 (quarter circle radians)

// Buffer Size Constants (powers of 2 for efficiency)
const int SMALL_BUFFER = 128                // Small buffer size
const int MEDIUM_BUFFER = 512               // Medium buffer size  
const int LARGE_BUFFER = 1024               // Large buffer size
const int MAX_BUFFER = 2048                 // Maximum buffer size

// Bit Manipulation Constants
const int BITS_PER_BYTE = 8                 // Standard byte size
const int SHIFT_DIVIDE_BY_2 = 1             // Bit shift for divide by 2
const int SHIFT_DIVIDE_BY_4 = 2             // Bit shift for divide by 4
const int SHIFT_DIVIDE_BY_8 = 3             // Bit shift for divide by 8

// LED Display Constants
const int LED_OFF = 0x00                    // All LEDs off
const int LED_ALL_ON = 0xFF                 // All 8 LEDs on
const int LED_SINGLE = 0x01                 // Single LED pattern
const int LED_DOUBLE = 0x03                 // Two LED pattern
const int LED_QUAD = 0x0F                   // Four LED pattern
const int LED_BRIGHTNESS_FULL = 255         // Full LED brightness
const int LED_BRIGHTNESS_HALF = 127         // Half LED brightness

// Musical/Timing Constants
const int STANDARD_BPM = 120                // Standard tempo reference
const int QUARTER_NOTE_DIVISIONS = 4        // Divisions per quarter note
const int SEMITONES_PER_OCTAVE = 12         // Musical semitones in octave
const float A4_FREQUENCY = 440.0            // A4 reference frequency (Hz)

function process()
locals int input, int delayTimeParam, int delaySamples, int readPosition, int delayed, int mixed
{
    loop {
        // Step 1: Get input
        input = signal[0]
        
        // Step 2: Get delay time from knob 1
        delayTimeParam = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]  // 0-255 from knob
        
        // Step 3: Convert to delay samples
        // Map 0-255 to 1000-20000 samples (about 0.02-0.45 seconds)
        delaySamples = 1000 + ((delayTimeParam * 19000) / 255)
        
        // Step 4: Store input in buffer
        delayBuffer[bufferPosition] = input
        
        // Step 5: Calculate read position with variable delay
        readPosition = (bufferPosition - delaySamples + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF
        
        // Step 6: Get delayed audio
        delayed = delayBuffer[readPosition]
        
        // Step 7: Mix (still 50/50 for now)
        mixed = (input + delayed) / 2
        
        // Step 8: Output
        signal[0] = mixed
        signal[1] = mixed
        
        // Step 9: Advance buffer position
        bufferPosition = (bufferPosition + 1) % SAMPLE_RATE_HALF
        
        yield()
    }
}
```

### 3.2 Test Variable Delay Time
1. Compile and load
2. **Turn knob 1** - delay time should change from very short to medium
3. **Notice:** Short delays create flutter effects, longer delays create distinct echoes

---

## Step 4: Add Feedback Control

### 4.1 Understanding Feedback
Feedback creates multiple echoes by feeding the delay output back into the input:

```
Input --> [+] --> [Delay Buffer] --> [Output]
          ^                             |
          |                             |
          +-------- [× Feedback] -------+
```

### 4.2 Add Feedback Parameter
Replace the process function:

```impala
function process()
{
    loop {
        // Get parameters
        int delayTimeParam = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]  // Knob 1: Delay time
        int feedbackParam = (int)global params[OPERAND_2_LOW_PARAM_INDEX]   // Knob 2: Feedback amount
        
        // Convert parameters to useful ranges
        int delaySamples = 1000 + ((delayTimeParam * 19000) / 255)
        int feedbackLevel = (feedbackParam * 200) / 255  // Limit to 200/255 for stability
        
        // Get input audio
        int input = signal[0]
        
        // Get delayed audio
        int readPosition = (bufferPosition - delaySamples + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF
        int delayed = delayBuffer[readPosition]
        
        // Create feedback: delayed audio affects what goes into buffer
        int feedbackAmount = (delayed * feedbackLevel) / 255
        int bufferInput = input + feedbackAmount
        
        // Prevent feedback from getting too loud
        if (bufferInput > AUDIO_MAX) bufferInput = AUDIO_MAX
        else if (bufferInput < -AUDIO_MAX) bufferInput = -AUDIO_MAX
        
        // Store in buffer (input + feedback)
        delayBuffer[bufferPosition] = bufferInput
        
        // Mix original input with delayed signal
        int mixed = (input + delayed) / 2
        
        signal[0] = mixed
        signal[1] = mixed
        
        bufferPosition = (bufferPosition + 1) % SAMPLE_RATE_HALF
        
        yield()
    }
}
```

### 4.3 Test Feedback Control
1. Compile and load
2. **Set delay time** (knob 1) to a medium value
3. **Slowly turn up feedback** (knob 2)
   - Low feedback: Single echo
   - Medium feedback: Multiple echoes that fade out
   - High feedback: Long, sustained echoes
4. **⚠️ Be careful:** Too much feedback can get very loud!

---

## Step 5: Add Dry/Wet Mix Control

### 5.1 Understanding Mix Control
- **Dry**: Original, unprocessed audio
- **Wet**: Processed (delayed) audio  
- **Mix**: Balance between dry and wet

```impala
// Mix examples:
// 100% dry, 0% wet = no effect
// 50% dry, 50% wet = balanced mix
// 0% dry, 100% wet = only delay, no original
```

### 5.2 Add Mix Parameter
Final process function with all controls:

```impala
function process()
locals int delayTimeParam, int feedbackParam, int mixParam, int delaySamples, int feedbackLevel, int wetLevel, int dryLevel, int input, int readPosition, int delayed, int feedbackAmount, int bufferInput, int drySignal, int wetSignal, int finalOutput
{
    loop {
        // Get all three parameters
        delayTimeParam = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]  // Knob 1: Delay time
        feedbackParam = (int)global params[OPERAND_2_LOW_PARAM_INDEX]   // Knob 2: Feedback
        mixParam = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]        // Knob 3: Dry/wet mix
        
        // Convert to useful ranges
        delaySamples = 1000 + ((delayTimeParam * 19000) / 255)
        feedbackLevel = (feedbackParam * 200) / 255
        wetLevel = mixParam              // 0-255 wet amount
        dryLevel = 255 - mixParam        // 255-0 dry amount
        
        // Get audio
        input = signal[0]
        
        // Calculate delay
        readPosition = (bufferPosition - delaySamples + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF
        delayed = delayBuffer[readPosition]
        
        // Apply feedback
        feedbackAmount = (delayed * feedbackLevel) / 255
        bufferInput = input + feedbackAmount
        
        // Clip feedback
        if (bufferInput > AUDIO_MAX) bufferInput = AUDIO_MAX
        else if (bufferInput < -AUDIO_MAX) bufferInput = -AUDIO_MAX
        
        // Store in buffer
        delayBuffer[bufferPosition] = bufferInput
        
        // Mix dry and wet signals
        drySignal = (input * dryLevel) / 255
        wetSignal = (delayed * wetLevel) / 255
        finalOutput = drySignal + wetSignal
        
        // Output
        signal[0] = finalOutput
        signal[1] = finalOutput
        
        bufferPosition = (bufferPosition + 1) % SAMPLE_RATE_HALF
        
        yield()
    }
}
```

### 5.3 Test Complete Delay
1. Compile and load
2. **Test all three controls:**
   - Knob 1: Delay time (timing of echoes)
   - Knob 2: Feedback (number of echoes)  
   - Knob 3: Mix (dry/wet balance)
3. **Try combinations:**
   - Short delay + high feedback = flutter/chorus
   - Long delay + low feedback = distinct echoes
   - Any delay + low mix = subtle effect

---

## Step 6: Add LED Feedback

### 6.1 Visual Parameter Display
Add this after the audio processing, before `yield()`:

```impala
// LED feedback for each parameter
displayLEDs[0] = delayTimeParam      // LED 1 shows delay time
displayLEDs[1] = feedbackParam       // LED 2 shows feedback amount
displayLEDs[2] = mixParam            // LED 3 shows mix level

// LED 4 shows delay activity (flashes with echoes)
int activity = 0
if (delayed > 100 || delayed < -100) {
    activity = 0xFF  // All LEDs on when delay is active
} else {
    activity = 0x01  // Just one LED when quiet
}
displayLEDs[3] = activity
```

### 6.2 Complete Final Code
Here's your complete delay with all features:

```impala
// Complete Simple Delay with All Features
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

global array delayBuffer[SAMPLE_RATE_HALF]  // 0.5 second maximum delay
global int bufferPosition = 0

function process()
{
    loop {
        // Read parameters from hardware knobs
        int delayTimeParam = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]  // Knob 1: Delay time (0-255)
        int feedbackParam = (int)global params[OPERAND_2_LOW_PARAM_INDEX]   // Knob 2: Feedback amount (0-255)
        int mixParam = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]        // Knob 3: Dry/wet mix (0-255)
        
        // Convert parameters to useful ranges
        int delaySamples = 1000 + ((delayTimeParam * 19000) / 255)  // 1000-20000 samples
        int feedbackLevel = (feedbackParam * 200) / 255             // 0-200 (safe range)
        int wetLevel = mixParam                                      // 0-255 wet
        int dryLevel = 255 - mixParam                               // 255-0 dry
        
        // Get input audio
        int input = signal[0]
        
        // Calculate where to read delayed audio from
        int readPosition = (bufferPosition - delaySamples + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF
        
        // Get delayed audio sample
        int delayed = delayBuffer[readPosition]
        
        // Apply feedback (delayed audio affects buffer input)
        int feedbackAmount = (delayed * feedbackLevel) / 255
        int bufferInput = input + feedbackAmount
        
        // Prevent feedback overflow
        if (bufferInput > AUDIO_MAX) bufferInput = AUDIO_MAX
        else if (bufferInput < -AUDIO_MAX) bufferInput = -AUDIO_MAX
        
        // Store new audio in delay buffer
        delayBuffer[bufferPosition] = bufferInput
        
        // Mix dry (original) and wet (delayed) signals
        int drySignal = (input * dryLevel) / 255
        int wetSignal = (delayed * wetLevel) / 255
        int finalOutput = drySignal + wetSignal
        
        // Send to both audio outputs
        signal[0] = finalOutput
        signal[1] = finalOutput
        
        // LED visual feedback
        displayLEDs[0] = delayTimeParam  // Show delay time setting
        displayLEDs[1] = feedbackParam   // Show feedback setting
        displayLEDs[2] = mixParam        // Show mix setting
        
        // Activity indicator (flashes with delay signal)
        int activity = (delayed > 100 || delayed < -100) ? 0xFF : 0x01
        displayLEDs[3] = activity
        
        // Move to next buffer position (circular)
        bufferPosition = (bufferPosition + 1) % SAMPLE_RATE_HALF
        
        yield()
    }
}
```

---

## Step 7: Understanding What You Built

### 7.1 Key Concepts You Learned

**Circular Buffers:**
- Store audio samples in a fixed-size array
- Use modulo arithmetic to wrap around at the end
- Essential for all time-based audio effects

**Parameter Mapping:**
- Convert 0-255 knob values to musically useful ranges
- Different parameters need different scaling (linear, exponential, etc.)

**Audio Feedback Systems:**
- Feedback creates multiple echoes
- Must limit feedback to prevent runaway amplification
- Feedback + delay = the foundation for reverb

**Real-time Audio Processing:**
- Process one sample at a time
- Always call `yield()` to return control
- Keep processing predictable and efficient

### 7.2 How This Applies to Other Effects

**This delay is the foundation for:**

```impala
// Reverb = Multiple delays with different times and feedback
// Chorus = Short delay with modulated delay time
// Flanger = Very short delay with swept delay time  
// Echo = Long delay with controlled feedback
// Ping-pong delay = Stereo delay with left/right alternation
```

### 7.3 Performance Analysis

**Your delay uses:**
- 22,050 integers of memory (about 88KB)
- 4 parameter reads per sample
- 2 buffer accesses per sample  
- 6 arithmetic operations per sample

**This is very efficient** - you could run multiple copies simultaneously.

---

## Step 8: Experiment and Extend

### 8.1 Try These Modifications

**Different Delay Times:**
```impala
// Shorter delays (chorus/flanger territory)
int delaySamples = 10 + ((delayTimeParam * 500) / 255)  // 10-510 samples

// Longer delays (echo territory)  
int delaySamples = 5000 + ((delayTimeParam * 40000) / 255)  // 5000-45000 samples
```

**Different Feedback Curves:**
```impala
// Exponential feedback (more musical)
int feedbackLevel = (feedbackParam * feedbackParam) / 255  // Exponential curve

// Limited feedback (always safe)
int feedbackLevel = (feedbackParam * 180) / 255  // Never exceeds 70%
```

**Stereo Processing:**
```impala
// Process left and right independently
signal[0] = processChannel(signal[0], bufferPosition)
signal[1] = processChannel(signal[1], (bufferPosition + 100) % SAMPLE_RATE_HALF)  // Slight offset
```

### 8.2 Build From Here

**Next Steps:**
1. Add high-frequency damping for analog tape sound
2. Implement ping-pong delay (left/right alternation)
3. Add modulation for chorus/flanger effects
4. Create multi-tap delays with multiple read positions
5. Build reverb using multiple delay lines

---

## What's Next?

### You Now Understand:
- ✅ **Circular buffer management** - The core of all time-based effects
- ✅ **Parameter mapping** - Converting knobs to musical values  
- ✅ **Feedback systems** - How to create multiple echoes safely
- ✅ **Audio mixing** - Balancing dry and wet signals
- ✅ **Real-time constraints** - Processing one sample at a time efficiently

### Apply This Knowledge To:
- 📖 [Reverb Simple](../cookbook/audio-effects/reverb-simple.md) - Multiple delays = reverb
- 📖 [Chorus Effect](../cookbook/audio-effects/chorus-effect.md) - Modulated delay = chorus
- 📖 [Make a Delay](../cookbook/audio-effects/make-a-delay.md) - More advanced delay features

**You now understand the foundation of all time-based audio effects!** Every reverb, chorus, flanger, and echo effect uses these same circular buffer and feedback principles.