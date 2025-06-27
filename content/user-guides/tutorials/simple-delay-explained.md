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

global array delayBuffer[1000]
global int writePosition = 0
global int readPosition = 500


delayBuffer[writePosition] = currentInput
delayedOutput = delayBuffer[readPosition]
```

### 1.3 The Challenge: Circular Buffers
What happens when we reach the end of the array? We need to wrap around to the beginning:

```impala

writePosition = writePosition + 1
delayBuffer[writePosition] = input


writePosition = (writePosition + 1) % 1000
delayBuffer[writePosition] = input
```

---

## Step 2: Build the Simplest Delay

### 2.1 Create Basic Structure
Create `simple_delay.impala`:

```impala



const int PARAM_MAX = 255
const int PARAM_MIN = 0
const int PARAM_MID = 128
const int PARAM_SWITCH_THRESHOLD = 127


const int AUDIO_MAX = 2047
const int AUDIO_MIN = -2047
const int AUDIO_ZERO = 0


const int SAMPLE_RATE_44K1 = 44100
const int SAMPLE_RATE_HALF = 22050
const int SAMPLE_RATE_QUARTER = 11025


const int AUDIO_FULL_RANGE = 65536
const int AUDIO_HALF_RANGE = 32768
const int AUDIO_QUARTER_RANGE = 16384


const float PI = 3.14159265
const float TWO_PI = 6.28318531
const float PI_OVER_2 = 1.57079633


const int SMALL_BUFFER = 128
const int MEDIUM_BUFFER = 512
const int LARGE_BUFFER = 1024
const int MAX_BUFFER = 2048


const int BITS_PER_BYTE = 8
const int SHIFT_DIVIDE_BY_2 = 1
const int SHIFT_DIVIDE_BY_4 = 2
const int SHIFT_DIVIDE_BY_8 = 3


const int LED_OFF = 0x00
const int LED_ALL_ON = 0xFF
const int LED_SINGLE = 0x01
const int LED_DOUBLE = 0x03
const int LED_QUAD = 0x0F
const int LED_BRIGHTNESS_FULL = 255
const int LED_BRIGHTNESS_HALF = 127


const int STANDARD_BPM = 120
const int QUARTER_NOTE_DIVISIONS = 4
const int SEMITONES_PER_OCTAVE = 12
const float A4_FREQUENCY = 440.0


const int PRAWN_FIRMWARE_PATCH_FORMAT = 2


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


global array delayBuffer[SAMPLE_RATE_HALF]
global int bufferPosition = 0

function process()
locals int input, int readPosition, int delayed, int mixed
{
    loop {

        input = signal[0]
        

        delayBuffer[bufferPosition] = input
        


        readPosition = (bufferPosition - SAMPLE_RATE_QUARTER + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF
        

        delayed = delayBuffer[readPosition]
        

        mixed = (input + delayed) / 2
        

        signal[0] = mixed
        signal[1] = mixed
        

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

int readPos = bufferPosition - SAMPLE_RATE_QUARTER


int readPos = (bufferPosition - SAMPLE_RATE_QUARTER + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF







```

---

## Step 3: Add Controllable Delay Time

### 3.1 Map Parameter to Delay Time
Replace the process function with this enhanced version:

```impala



const int PARAM_MAX = 255
const int PARAM_MIN = 0
const int PARAM_MID = 128
const int PARAM_SWITCH_THRESHOLD = 127


const int AUDIO_MAX = 2047
const int AUDIO_MIN = -2047
const int AUDIO_ZERO = 0


const int SAMPLE_RATE_44K1 = 44100
const int SAMPLE_RATE_HALF = 22050
const int SAMPLE_RATE_QUARTER = 11025


const int AUDIO_FULL_RANGE = 65536
const int AUDIO_HALF_RANGE = 32768
const int AUDIO_QUARTER_RANGE = 16384


const float PI = 3.14159265
const float TWO_PI = 6.28318531
const float PI_OVER_2 = 1.57079633


const int SMALL_BUFFER = 128
const int MEDIUM_BUFFER = 512
const int LARGE_BUFFER = 1024
const int MAX_BUFFER = 2048


const int BITS_PER_BYTE = 8
const int SHIFT_DIVIDE_BY_2 = 1
const int SHIFT_DIVIDE_BY_4 = 2
const int SHIFT_DIVIDE_BY_8 = 3


const int LED_OFF = 0x00
const int LED_ALL_ON = 0xFF
const int LED_SINGLE = 0x01
const int LED_DOUBLE = 0x03
const int LED_QUAD = 0x0F
const int LED_BRIGHTNESS_FULL = 255
const int LED_BRIGHTNESS_HALF = 127


const int STANDARD_BPM = 120
const int QUARTER_NOTE_DIVISIONS = 4
const int SEMITONES_PER_OCTAVE = 12
const float A4_FREQUENCY = 440.0

function process()
locals int input, int delayTimeParam, int delaySamples, int readPosition, int delayed, int mixed
{
    loop {

        input = signal[0]
        

        delayTimeParam = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        


        delaySamples = 1000 + ((delayTimeParam * 19000) / 255)
        

        delayBuffer[bufferPosition] = input
        

        readPosition = (bufferPosition - delaySamples + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF
        

        delayed = delayBuffer[readPosition]
        

        mixed = (input + delayed) / 2
        

        signal[0] = mixed
        signal[1] = mixed
        

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

        int delayTimeParam = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        int feedbackParam = (int)global params[OPERAND_2_LOW_PARAM_INDEX]
        

        int delaySamples = 1000 + ((delayTimeParam * 19000) / 255)
        int feedbackLevel = (feedbackParam * 200) / 255
        

        int input = signal[0]
        

        int readPosition = (bufferPosition - delaySamples + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF
        int delayed = delayBuffer[readPosition]
        

        int feedbackAmount = (delayed * feedbackLevel) / 255
        int bufferInput = input + feedbackAmount
        

        if (bufferInput > AUDIO_MAX) bufferInput = AUDIO_MAX
        else if (bufferInput < -AUDIO_MAX) bufferInput = -AUDIO_MAX
        

        delayBuffer[bufferPosition] = bufferInput
        

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




```

### 5.2 Add Mix Parameter
Final process function with all controls:

```impala
function process()
locals int delayTimeParam, int feedbackParam, int mixParam, int delaySamples, int feedbackLevel, int wetLevel, int dryLevel, int input, int readPosition, int delayed, int feedbackAmount, int bufferInput, int drySignal, int wetSignal, int finalOutput
{
    loop {

        delayTimeParam = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        feedbackParam = (int)global params[OPERAND_2_LOW_PARAM_INDEX]
        mixParam = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]
        

        delaySamples = 1000 + ((delayTimeParam * 19000) / 255)
        feedbackLevel = (feedbackParam * 200) / 255
        wetLevel = mixParam
        dryLevel = 255 - mixParam
        

        input = signal[0]
        

        readPosition = (bufferPosition - delaySamples + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF
        delayed = delayBuffer[readPosition]
        

        feedbackAmount = (delayed * feedbackLevel) / 255
        bufferInput = input + feedbackAmount
        

        if (bufferInput > AUDIO_MAX) bufferInput = AUDIO_MAX
        else if (bufferInput < -AUDIO_MAX) bufferInput = -AUDIO_MAX
        

        delayBuffer[bufferPosition] = bufferInput
        

        drySignal = (input * dryLevel) / 255
        wetSignal = (delayed * wetLevel) / 255
        finalOutput = drySignal + wetSignal
        

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

displayLEDs[0] = delayTimeParam
displayLEDs[1] = feedbackParam
displayLEDs[2] = mixParam


int activity = 0
if (delayed > 100 || delayed < -100) {
    activity = 0xFF
} else {
    activity = 0x01
}
displayLEDs[3] = activity
```

### 6.2 Complete Final Code
Here's your complete delay with all features:

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

global array delayBuffer[SAMPLE_RATE_HALF]
global int bufferPosition = 0

function process()
{
    loop {

        int delayTimeParam = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        int feedbackParam = (int)global params[OPERAND_2_LOW_PARAM_INDEX]
        int mixParam = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]
        

        int delaySamples = 1000 + ((delayTimeParam * 19000) / 255)
        int feedbackLevel = (feedbackParam * 200) / 255
        int wetLevel = mixParam
        int dryLevel = 255 - mixParam
        

        int input = signal[0]
        

        int readPosition = (bufferPosition - delaySamples + SAMPLE_RATE_HALF) % SAMPLE_RATE_HALF
        

        int delayed = delayBuffer[readPosition]
        

        int feedbackAmount = (delayed * feedbackLevel) / 255
        int bufferInput = input + feedbackAmount
        

        if (bufferInput > AUDIO_MAX) bufferInput = AUDIO_MAX
        else if (bufferInput < -AUDIO_MAX) bufferInput = -AUDIO_MAX
        

        delayBuffer[bufferPosition] = bufferInput
        

        int drySignal = (input * dryLevel) / 255
        int wetSignal = (delayed * wetLevel) / 255
        int finalOutput = drySignal + wetSignal
        

        signal[0] = finalOutput
        signal[1] = finalOutput
        

        displayLEDs[0] = delayTimeParam
        displayLEDs[1] = feedbackParam
        displayLEDs[2] = mixParam
        

        int activity = (delayed > 100 || delayed < -100) ? 0xFF : 0x01
        displayLEDs[3] = activity
        

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

int delaySamples = 10 + ((delayTimeParam * 500) / 255)


int delaySamples = 5000 + ((delayTimeParam * 40000) / 255)
```

**Different Feedback Curves:**
```impala

int feedbackLevel = (feedbackParam * feedbackParam) / 255


int feedbackLevel = (feedbackParam * 180) / 255
```

**Stereo Processing:**
```impala

signal[0] = processChannel(signal[0], bufferPosition)
signal[1] = processChannel(signal[1], (bufferPosition + 100) % SAMPLE_RATE_HALF)
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