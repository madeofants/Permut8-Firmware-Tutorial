# Build Your First Filter Plugin - Complete Step-by-Step Tutorial

## What We're Building
A complete low-pass filter plugin with cutoff frequency control, resonance, and LED feedback. By the end of this tutorial, you'll have a working plugin and understand every line of code.

## Before We Start
- ✅ Make sure PikaCmd.exe is in your Permut8 Firmware Code directory
- ✅ Have Permut8 loaded in your DAW
- ✅ Some audio playing through Permut8 to test with

---

## Step 1: Create the Empty Plugin File

### 1.1 Create the File
Create a new text file called `my_filter.impala` in your Permut8 Firmware Code directory.

### 1.2 Add the Basic Structure
Copy this exact code into your file:

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


global int lastOutput = 0


function process()
locals int cutoffParam, int filterMix, int input, int output
{
    loop {

        



        

        yield()
    }
}

```

### 1.3 Test the Empty Plugin
1. Open command prompt in your Permut8 Firmware Code directory
2. Compile: `PikaCmd.exe -compile my_filter.impala`
3. You should see `my_filter.gazl` created
4. In Permut8 console: `patch my_filter.gazl`
5. Audio should pass through unchanged - **this means it's working!**

**What just happened?** You created a plugin that loads successfully but doesn't modify the audio yet. This is your foundation.

---

## Step 2: Add Basic Low-Pass Filtering

### 2.1 Understand the Filter Math
A simple low-pass filter works like this:
```
output = (input * mix) + (lastOutput * (1 - mix))
```
When `mix` is small, more of the previous output is used = more filtering.

### 2.2 Replace the Process Function
Replace the entire `process()` function with this:

```impala
function process()
locals int cutoffParam, int filterMix, int input, int output
{
    loop {

        cutoffParam = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]
        

        filterMix = (cutoffParam * 200) / 255
        

        input = signal[0]
        output = ((input * filterMix) + (lastOutput * (255 - filterMix))) / 255
        

        lastOutput = output
        

        signal[0] = output
        signal[1] = output
        
        yield()
    }
}
```

### 2.3 Test the Filter
1. Compile: `PikaCmd.exe -compile my_filter.impala`
2. Load: `patch my_filter.gazl`
3. **Turn the first knob** - you should hear the high frequencies being filtered!
   - Knob left (low values) = more filtering, duller sound
   - Knob right (high values) = less filtering, brighter sound

**What's happening?** The filter is mixing the current input with the previous output. Lower knob values keep more of the previous output, which smooths out fast changes (high frequencies).

---

## Step 3: Add LED Feedback

### 3.1 Add LED Visualization
Replace the `process()` function with this enhanced version:

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
locals int cutoffParam, int filterMix, int input, int output, int filterAmount, int ledPattern
{
    loop {

        cutoffParam = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]
        filterMix = (cutoffParam * 200) / 255
        

        input = signal[0]
        output = ((input * filterMix) + (lastOutput * (255 - filterMix))) / 255
        lastOutput = output
        

        filterAmount = 255 - cutoffParam
        ledPattern = 0
        

        if (filterAmount > 200) ledPattern = 0xFF
        else if (filterAmount > 150) ledPattern = 0x7F
        else if (filterAmount > 100) ledPattern = 0x3F
        else if (filterAmount > 80) ledPattern = 0x1F
        else if (filterAmount > 60) ledPattern = 0x0F
        else if (filterAmount > 40) ledPattern = 0x07
        else if (filterAmount > 20) ledPattern = 0x03
        else if (filterAmount > 0) ledPattern = 0x01
        
        displayLEDs[0] = ledPattern
        

        signal[0] = output
        signal[1] = output
        
        yield()
    }
}
```

### 3.2 Test LED Feedback
1. Compile and load as before
2. **Watch the LEDs while turning the knob:**
   - More LEDs = more filtering (duller sound)
   - Fewer LEDs = less filtering (brighter sound)

**Visual feedback complete!** Now you can see what the filter is doing.

---

## Step 4: Add Resonance Control

### 4.1 Understand Resonance
Resonance adds a peak at the cutoff frequency by feeding some output back to the input. This makes the filter "ring" at its cutoff frequency.

### 4.2 Add Resonance Variables
Add this line after the existing global variables:

```impala
global int feedbackAmount = 0
```

### 4.3 Enhanced Process Function with Resonance
Replace `process()` with this complete version:

```impala
function process()
locals int cutoffParam, int resonanceParam, int filterMix, int resonance, int input, int output, int ledIntensity, int ledPattern
{
    loop {

        cutoffParam = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]
        resonanceParam = (int)global params[OPERAND_1_LOW_PARAM_INDEX]
        

        filterMix = (cutoffParam * 200) / 255
        resonance = (resonanceParam * 150) / 255
        

        input = signal[0] + ((lastOutput * resonance) / 255)
        

        if (input > AUDIO_MAX) input = AUDIO_MAX
        else if (input < -AUDIO_MAX) input = -AUDIO_MAX
        

        output = ((input * filterMix) + (lastOutput * (255 - filterMix))) / 255
        lastOutput = output
        

        ledIntensity = (cutoffParam + resonanceParam) / 2
        ledPattern = 0
        
        if (ledIntensity > 220) ledPattern = 0xFF
        else if (ledIntensity > 180) ledPattern = 0x7F
        else if (ledIntensity > 140) ledPattern = 0x3F
        else if (ledIntensity > 100) ledPattern = 0x1F
        else if (ledIntensity > 60) ledPattern = 0x0F
        else if (ledIntensity > 30) ledPattern = 0x07
        else ledPattern = 0x01
        
        displayLEDs[0] = ledPattern
        

        signal[0] = output
        signal[1] = output
        
        yield()
    }
}
```

### 4.4 Test Two-Knob Control
1. Compile and load: `PikaCmd.exe -compile my_filter.impala` then `patch my_filter.gazl`
2. **Test both knobs:**
   - **Knob 1 (cutoff):** Controls brightness/dullness
   - **Knob 2 (resonance):** Adds "ring" or "whistle" at the cutoff frequency
3. **Try extreme settings:** Turn resonance all the way up for dramatic effects!

---

## Step 5: Add Proper Stereo Processing

### 5.1 Add Right Channel Filter State
Add another state variable:

```impala
global int lastOutputR = 0
```

### 5.2 Complete Stereo Filter
Replace `process()` one final time:

```impala
function process()
{
    loop {

        int cutoffParam = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]
        int resonanceParam = (int)global params[OPERAND_1_LOW_PARAM_INDEX]
        int filterMix = (cutoffParam * 200) / 255
        int resonance = (resonanceParam * 150) / 255
        

        inputL = signal[0] + ((lastOutput * resonance) / 255)
        if (inputL > AUDIO_MAX) inputL = AUDIO_MAX
        else if (inputL < -AUDIO_MAX) inputL = -AUDIO_MAX
        
        outputL = ((inputL * filterMix) + (lastOutput * (255 - filterMix))) / 255
        lastOutput = outputL
        

        inputR = signal[1] + ((lastOutputR * resonance) / 255)
        if (inputR > AUDIO_MAX) inputR = AUDIO_MAX
        else if (inputR < -AUDIO_MAX) inputR = -AUDIO_MAX
        
        outputR = ((inputR * filterMix) + (lastOutputR * (255 - filterMix))) / 255
        lastOutputR = outputR
        

        activity = ((outputL > 100 || outputL < -100) || 
                       (outputR > 100 || outputR < -100)) ? 0xFF : 0x01
        displayLEDs[0] = activity
        

        signal[0] = outputL
        signal[1] = outputR
        
        yield()
    }
}
```

---

## Step 6: Final Testing and Polish

### 6.1 Complete Code Review
Your final `my_filter.impala` should look like this:

```impala

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


global int lastOutput = 0
global int lastOutputR = 0

function process()
locals int cutoffParam, int resonanceParam, int filterMix, int resonance, int inputL, int outputL, int inputR, int outputR, int activity
{
    loop {

        cutoffParam = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]
        resonanceParam = (int)global params[OPERAND_1_LOW_PARAM_INDEX]
        

        filterMix = (cutoffParam * 200) / 255
        resonance = (resonanceParam * 150) / 255
        

        inputL = signal[0] + ((lastOutput * resonance) / 255)
        

        if (inputL > AUDIO_MAX) inputL = AUDIO_MAX
        else if (inputL < -AUDIO_MAX) inputL = -AUDIO_MAX
        

        outputL = ((inputL * filterMix) + (lastOutput * (255 - filterMix))) / 255
        lastOutput = outputL
        

        inputR = signal[1] + ((lastOutputR * resonance) / 255)
        
        if (inputR > AUDIO_MAX) inputR = AUDIO_MAX
        else if (inputR < -AUDIO_MAX) inputR = -AUDIO_MAX
        
        outputR = ((inputR * filterMix) + (lastOutputR * (255 - filterMix))) / 255
        lastOutputR = outputR
        

        activity = ((outputL > 100 || outputL < -100) || 
                       (outputR > 100 || outputR < -100)) ? 0xFF : 0x01
        displayLEDs[0] = activity
        

        signal[0] = outputL
        signal[1] = outputR
        
        yield()
    }
}
```

### 6.2 Performance Testing
1. **Compile final version:** `PikaCmd.exe -compile my_filter.impala`
2. **Load and test:** `patch my_filter.gazl`
3. **Test all scenarios:**
   - Low cutoff + high resonance = "analog synth" sound
   - High cutoff + low resonance = subtle warming
   - Medium cutoff + medium resonance = musical filtering
   - Extreme resonance = self-oscillation (makes its own tone!)

### 6.3 Understanding What You Built
**Congratulations!** You just built a complete audio plugin with:
- ✅ **Real-time audio processing** (low-pass filter)
- ✅ **Two-parameter control** (cutoff + resonance)
- ✅ **Visual feedback** (LEDs show activity)
- ✅ **Proper stereo handling** (independent left/right processing)
- ✅ **Stability features** (clipping prevention, safe coefficient ranges)

---

## What's Next?

### Try These Modifications:
1. **High-pass filter:** Change the filter formula to emphasize high frequencies
2. **Band-pass filter:** Combine high-pass and low-pass stages
3. **More parameters:** Use knobs 3 and 4 for additional controls
4. **Modulation:** Make parameters change automatically over time

### Learn More:
- 📖 [Make a Delay](../cookbook/audio-effects/make-a-delay.md) - Add delay effects to your filter
- 📖 [Control LEDs](../cookbook/visual-feedback/control-leds.md) - Advanced LED patterns
- 📖 [Sync to Tempo](../cookbook/timing/sync-to-tempo.md) - Make filter parameters follow the beat

### Common Problems and Solutions:
- **No sound:** Check that you're calling `yield()` and setting `signal[0]` and `signal[1]`
- **Distorted sound:** Reduce resonance amount or add more clipping protection
- **Compilation errors:** Check semicolons, brackets, and variable names
- **LEDs not working:** Make sure LED values are 0-255

You now have the skills to build any audio effect! The pattern is always the same: get parameters, process audio, provide feedback, yield control.
