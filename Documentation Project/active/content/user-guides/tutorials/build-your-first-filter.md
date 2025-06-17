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
// My First Filter Plugin
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Global variables that Permut8 provides
global array signal[2]          // Left/Right audio samples  
global array params[8]          // Knob values (0-255)
global array displayLEDs[4]     // LED displays (0-255)

// Our filter state variables
global int lastOutput = 0       // Remember last output sample

// Main processing function
function process()
{
    loop {
        // Audio processing goes here
        
        // For now, just pass audio through unchanged
        // signal[0] = left channel, signal[1] = right channel
        // (we don't need to change anything - audio passes through automatically)
        
        // Return control to Permut8 after processing each sample
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
{
    loop {
        // Get cutoff frequency from first knob (0-255)
        int cutoffParam = params[3]
        
        // Convert to filter coefficient (0-200 for stability)
        int filterMix = (cutoffParam * 200) / 255
        
        // Apply low-pass filter to left channel
        int input = signal[0]
        int output = ((input * filterMix) + (lastOutput * (255 - filterMix))) / 255
        
        // Store output for next sample
        lastOutput = output
        
        // Send filtered audio back
        signal[0] = output
        signal[1] = output  // Use same filter for both channels
        
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
function process()
{
    loop {
        // Get cutoff frequency from first knob
        int cutoffParam = params[3]
        int filterMix = (cutoffParam * 200) / 255
        
        // Apply filter
        int input = signal[0]
        int output = ((input * filterMix) + (lastOutput * (255 - filterMix))) / 255
        lastOutput = output
        
        // LED visualization - show filter activity
        int filterAmount = 255 - cutoffParam  // More LEDs = more filtering
        int ledPattern = 0
        
        // Light up LEDs based on filter amount
        if (filterAmount > 200) ledPattern = 0xFF        // All 8 LEDs
        else if (filterAmount > 150) ledPattern = 0x7F   // 7 LEDs
        else if (filterAmount > 100) ledPattern = 0x3F   // 6 LEDs
        else if (filterAmount > 80) ledPattern = 0x1F    // 5 LEDs
        else if (filterAmount > 60) ledPattern = 0x0F    // 4 LEDs
        else if (filterAmount > 40) ledPattern = 0x07    // 3 LEDs
        else if (filterAmount > 20) ledPattern = 0x03    // 2 LEDs
        else if (filterAmount > 0) ledPattern = 0x01     // 1 LED
        
        displayLEDs[0] = ledPattern
        
        // Send audio
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
global int feedbackAmount = 0   // For resonance feedback
```

### 4.3 Enhanced Process Function with Resonance
Replace `process()` with this complete version:

```impala
function process()
{
    loop {
        // Get controls from knobs
        int cutoffParam = params[3]     // Knob 1: Cutoff frequency
        int resonanceParam = params[4]  // Knob 2: Resonance amount
        
        // Convert to usable values
        int filterMix = (cutoffParam * 200) / 255
        int resonance = (resonanceParam * 150) / 255  // Limit for stability
        
        // Add resonance feedback to input
        int input = signal[0] + ((lastOutput * resonance) / 255)
        
        // Prevent runaway feedback
        if (input > 2047) input = 2047
        else if (input < -2047) input = -2047
        
        // Apply low-pass filter
        int output = ((input * filterMix) + (lastOutput * (255 - filterMix))) / 255
        lastOutput = output
        
        // LED feedback - show both cutoff and resonance
        int ledIntensity = (cutoffParam + resonanceParam) / 2
        int ledPattern = 0
        
        if (ledIntensity > 220) ledPattern = 0xFF
        else if (ledIntensity > 180) ledPattern = 0x7F
        else if (ledIntensity > 140) ledPattern = 0x3F
        else if (ledIntensity > 100) ledPattern = 0x1F
        else if (ledIntensity > 60) ledPattern = 0x0F
        else if (ledIntensity > 30) ledPattern = 0x07
        else ledPattern = 0x01
        
        displayLEDs[0] = ledPattern
        
        // Output filtered audio
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
global int lastOutputR = 0      // Right channel filter memory
```

### 5.2 Complete Stereo Filter
Replace `process()` one final time:

```impala
function process()
{
    loop {
        // Get parameters
        int cutoffParam = params[3]
        int resonanceParam = params[4]
        int filterMix = (cutoffParam * 200) / 255
        int resonance = (resonanceParam * 150) / 255
        
        // LEFT CHANNEL
        int inputL = signal[0] + ((lastOutput * resonance) / 255)
        if (inputL > 2047) inputL = 2047
        else if (inputL < -2047) inputL = -2047
        
        int outputL = ((inputL * filterMix) + (lastOutput * (255 - filterMix))) / 255
        lastOutput = outputL
        
        // RIGHT CHANNEL  
        int inputR = signal[1] + ((lastOutputR * resonance) / 255)
        if (inputR > 2047) inputR = 2047
        else if (inputR < -2047) inputR = -2047
        
        int outputR = ((inputR * filterMix) + (lastOutputR * (255 - filterMix))) / 255
        lastOutputR = outputR
        
        // LED feedback
        int activity = ((outputL > 100 || outputL < -100) || 
                       (outputR > 100 || outputR < -100)) ? 0xFF : 0x01
        displayLEDs[0] = activity
        
        // Output stereo audio
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
// My First Filter Plugin - Complete Version
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]

// Filter state variables
global int lastOutput = 0       // Left channel filter memory
global int lastOutputR = 0      // Right channel filter memory

function process()
{
    loop {
        // Get parameters from hardware knobs
        int cutoffParam = params[3]     // Knob 1: Cutoff frequency (0-255)
        int resonanceParam = params[4]  // Knob 2: Resonance amount (0-255)
        
        // Convert to filter coefficients
        int filterMix = (cutoffParam * 200) / 255      // 0-200 range for stability
        int resonance = (resonanceParam * 150) / 255   // 0-150 range to prevent runaway
        
        // LEFT CHANNEL PROCESSING
        int inputL = signal[0] + ((lastOutput * resonance) / 255)
        
        // Prevent clipping from resonance feedback
        if (inputL > 2047) inputL = 2047
        else if (inputL < -2047) inputL = -2047
        
        // Apply low-pass filter: mix input with previous output
        int outputL = ((inputL * filterMix) + (lastOutput * (255 - filterMix))) / 255
        lastOutput = outputL
        
        // RIGHT CHANNEL PROCESSING (identical but separate state)
        int inputR = signal[1] + ((lastOutputR * resonance) / 255)
        
        if (inputR > 2047) inputR = 2047
        else if (inputR < -2047) inputR = -2047
        
        int outputR = ((inputR * filterMix) + (lastOutputR * (255 - filterMix))) / 255
        lastOutputR = outputR
        
        // LED feedback - show when filter is active
        int activity = ((outputL > 100 || outputL < -100) || 
                       (outputR > 100 || outputR < -100)) ? 0xFF : 0x01
        displayLEDs[0] = activity
        
        // Send processed audio back to Permut8
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
