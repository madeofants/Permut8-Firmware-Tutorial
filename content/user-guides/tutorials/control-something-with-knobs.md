# Control Something with Knobs - Instant Parameter Response

## What This Tutorial Does
Connect Permut8's hardware knobs to your plugin for instant, real-time control. In 10 minutes, you'll turn knobs and immediately hear or see the results. This is the foundation for making your plugins musical and expressive.

## What You'll Learn
- How to read values from Permut8's hardware knobs
- Convert knob values to useful parameter ranges
- Create instant, responsive parameter control
- The foundation for all interactive effects and instruments
- How parameters make plugins musical rather than static

**Prerequisites**: [Getting Audio In and Out](getting-audio-in-and-out.md)  
**Time Required**: 10 minutes  
**Difficulty**: Beginner

---

## Step 1: Understanding Hardware Knobs

### 1.1 How Knob Values Work
**Permut8 gives you 8 knobs** that your plugin can read:
```impala
global array params[8]  // params[0] through params[7]

// Knob positions are converted to numbers:
// Fully left (minimum) = 0
// Fully right (maximum) = 255
// Middle position = approximately 127
```

### 1.2 Which Knobs Do What
**Hardware mapping** (check your Permut8 manual for exact layout):
- `params[0]` through `params[7]` = 8 hardware knobs
- Values always range from 0 to 255
- Values update in real-time as you turn knobs

### 1.3 The Challenge: Scaling Parameters
**Raw knob values (0-255) rarely match what you need:**
```impala
// Raw knob value
int knobValue = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]  // 0 to 255

// What you actually want
int volume = ?             // 0 to 1000 (for volume control)
int frequency = ?          // 100 to 2000 (for oscillator pitch)
int delayTime = ?          // 1000 to 20000 (for delay samples)
```

**Solution: Parameter scaling math**

---

## Step 2: Your First Knob Control

### 2.1 Volume Control with Knob 1
Create `knob_volume_control.impala`:

```impala
// Knob-Controlled Volume - Instant Response
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]

function process()
{
    loop {
        // Read knob 1 value (0-255)
        int knobValue = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]  // First knob
        
        // Convert knob to volume (0-255 works fine for volume)
        int volume = knobValue
        
        // Apply volume control to audio
        signal[0] = (signal[0] * volume) / 255  // Left channel
        signal[1] = (signal[1] * volume) / 255  // Right channel
        
        // Show knob value on LED
        displayLEDs[0] = knobValue
        
        yield()
    }
}
```

### 2.2 Test Knob Response
1. **Compile**: `PikaCmd.exe -compile knob_volume_control.impala`
2. **Load**: `patch knob_volume_control.gazl`
3. **Play audio** through Permut8
4. **Turn knob 1** (first knob) and listen
   - **Expected**: Volume changes immediately as you turn the knob
   - **LED should change** to show knob position

**🎉 Success!** You just created real-time parameter control!

---

## Step 3: Understanding Parameter Scaling

### 3.1 The Scaling Formula
**Basic scaling pattern:**
```impala
// Scale 0-255 to any range you want
int scaledValue = minValue + ((knobValue * (maxValue - minValue)) / 255)

// Examples:
int volume = 0 + ((knobValue * (1000 - 0)) / 255)      // 0 to 1000
int frequency = 100 + ((knobValue * (2000 - 100)) / 255) // 100 to 2000
int delayTime = 1000 + ((knobValue * (20000 - 1000)) / 255) // 1000 to 20000
```

### 3.2 Common Scaling Examples
**Different parameter types need different ranges:**

```impala
// Volume control (0 = silent, 255 = full volume)
int volume = knobValue  // Direct use: 0-255

// Frequency control (100Hz to 2000Hz)
int frequency = 100 + ((knobValue * 1900) / 255)

// Delay time (0.1 to 1.0 seconds at 44.1kHz)
int delaySamples = 4410 + ((knobValue * 39690) / 255)  // 4410 to 44100

// Filter cutoff (musical scaling)
int cutoff = 50 + ((knobValue * knobValue) / 32)  // Exponential scaling
```

---

## Step 4: Multi-Knob Control

### 4.1 Control Multiple Parameters
Let's control an oscillator with 3 knobs:

```impala
// Multi-Knob Oscillator Control
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]

global int phase = 0  // Oscillator state

function process()
{
    loop {
        // Read multiple knobs
        int frequencyKnob = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]  // Knob 1: Frequency
        int volumeKnob = (int)global params[OPERAND_2_LOW_PARAM_INDEX]     // Knob 2: Volume
        int waveformKnob = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]   // Knob 3: Waveform type
        
        // Scale knob values to useful ranges
        int frequency = 50 + ((frequencyKnob * 950) / 255)  // 50 to 1000
        int volume = volumeKnob                              // 0 to 255
        int waveform = waveformKnob / 64                     // 0 to 3 (4 types)
        
        // Generate different waveforms based on knob 3
        int amplitude = 0
        if (waveform == 0) {
            // Triangle wave
            if (phase < 32768) {
                amplitude = phase - 16384
            } else {
                amplitude = 49152 - phase
            }
        } else if (waveform == 1) {
            // Square wave
            if (phase < 32768) {
                amplitude = 16384
            } else {
                amplitude = -16384
            }
        } else if (waveform == 2) {
            // Sawtooth wave
            amplitude = (phase / 2) - 16384
        } else {
            // Noise (random-ish)
            amplitude = (phase * 7919) % 32768 - 16384
        }
        
        // Apply volume and output
        int output = (amplitude * volume) / 2048  // Scale to reasonable level
        signal[0] = output
        signal[1] = output
        
        // Update oscillator
        phase = (phase + frequency) % 65536
        
        // LED feedback for each knob
        displayLEDs[0] = frequencyKnob  // Show frequency knob
        displayLEDs[1] = volumeKnob     // Show volume knob
        displayLEDs[2] = waveformKnob   // Show waveform knob
        displayLEDs[3] = waveform * 64  // Show selected waveform type
        
        yield()
    }
}
```

### 4.2 Test Multiple Controls
1. **Compile and load** as before
2. **Turn each knob and listen:**
   - **Knob 1**: Changes pitch (frequency)
   - **Knob 2**: Changes volume
   - **Knob 3**: Changes sound character (waveform)
3. **Watch LEDs** to see knob positions

**Experiment:** Try different combinations - low frequency + high volume, different waveforms at different pitches!

---

## Step 5: Smooth Parameter Changes

### 5.1 The Problem: Zipper Noise
**When parameters change too quickly**, you might hear clicks or "zipper" sounds. This happens when values jump suddenly.

### 5.2 Parameter Smoothing
Add smoothing to prevent artifacts:

```impala
// Add these globals at the top
global int smoothedFrequency = 500
global int smoothedVolume = 128

// In your process() function, replace direct scaling with:
function process()
{
    loop {
        // Read knobs
        int frequencyKnob = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        int volumeKnob = (int)global params[OPERAND_2_LOW_PARAM_INDEX]
        
        // Calculate target values
        int targetFrequency = 50 + ((frequencyKnob * 950) / 255)
        int targetVolume = volumeKnob
        
        // Smooth towards target values (prevents clicking)
        int freqDiff = targetFrequency - smoothedFrequency
        smoothedFrequency = smoothedFrequency + (freqDiff / 8)  // Smooth approach
        
        int volDiff = targetVolume - smoothedVolume
        smoothedVolume = smoothedVolume + (volDiff / 8)
        
        // Use smoothed values instead of raw knob values
        int frequency = smoothedFrequency
        int volume = smoothedVolume
        
        // ... rest of oscillator code using smoothed values ...
    }
}
```

### 5.3 Understanding Smoothing
```impala
smoothedValue = smoothedValue + ((targetValue - smoothedValue) / 8)
```

**How this works:**
- Takes difference between current and target value
- Divides by 8 (makes change 1/8 as big)
- Gradually approaches target over several samples
- Higher divisor = slower, smoother changes
- Lower divisor = faster, more responsive changes

---

## Step 6: Advanced Parameter Techniques

### 6.1 Exponential Scaling (Musical Parameters)
**Some parameters feel more natural with exponential scaling:**

```impala
// Linear scaling (feels mechanical)
int frequency = 50 + ((knobValue * 1950) / 255)  // 50 to 2000

// Exponential scaling (feels musical)
int scaledKnob = (knobValue * knobValue) / 255    // 0 to 255, but curved
int frequency = 50 + ((scaledKnob * 1950) / 255) // More control in low range
```

### 6.2 Parameter Ranges with Detents
**Create "notches" or preferred positions:**

```impala
// Quantized parameter (snaps to specific values)
int rawValue = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
int quantizedValue = (rawValue / 32) * 32  // Snaps to 0, 32, 64, 96, 128, etc.

// Musical note quantization
int noteKnob = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
int note = noteKnob / 21  // Snaps to 12 different notes (255/21 ≈ 12)
```

### 6.3 Parameter Interaction
**Make knobs affect each other:**

```impala
// Knob 1 controls base frequency, Knob 2 controls frequency modulation depth
int baseFreq = 100 + ((params[3] * 400) / 255)       // 100-500 base
int modDepth = (params[4] * 200) / 255                // 0-200 modulation
int finalFreq = baseFreq + (modDepth * sin(phase/100)) // Vibrato effect
```

---

## Step 7: Complete Interactive Plugin

### 7.1 Full-Featured Knob-Controlled Synthesizer
Here's a complete example using all techniques:

```impala
// Complete Interactive Synthesizer - 4 Knob Control
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]

// Oscillator state
global int phase = 0
global int lfoPhase = 0

// Smoothed parameters (prevents zipper noise)
global int smoothedFrequency = 500
global int smoothedVolume = 128
global int smoothedFilterCutoff = 1000
global int smoothedLFODepth = 0

function process()
{
    loop {
        // Read all 4 knobs
        int frequencyKnob = params[3]   // Knob 1: Base frequency
        int volumeKnob = params[4]      // Knob 2: Volume
        int filterKnob = params[5]      // Knob 3: Filter cutoff
        int lfoKnob = params[6]         // Knob 4: LFO modulation depth
        
        // Convert to target parameter values
        int targetFrequency = 100 + ((frequencyKnob * frequencyKnob) / 64)  // Exponential
        int targetVolume = volumeKnob
        int targetFilter = 200 + ((filterKnob * 1800) / 255)
        int targetLFODepth = (lfoKnob * 100) / 255
        
        // Smooth all parameters
        smoothedFrequency = smoothedFrequency + (targetFrequency - smoothedFrequency) / 16
        smoothedVolume = smoothedVolume + (targetVolume - smoothedVolume) / 16
        smoothedFilterCutoff = smoothedFilterCutoff + (targetFilter - smoothedFilterCutoff) / 16
        smoothedLFODepth = smoothedLFODepth + (targetLFODepth - smoothedLFODepth) / 16
        
        // Generate LFO for frequency modulation
        lfoPhase = (lfoPhase + 50) % 65536
        int lfoValue = 0
        if (lfoPhase < 32768) {
            lfoValue = lfoPhase - 16384
        } else {
            lfoValue = 49152 - lfoPhase
        }
        
        // Apply LFO to frequency
        int modulatedFreq = smoothedFrequency + ((lfoValue * smoothedLFODepth) / 16384)
        
        // Generate triangle wave oscillator
        int amplitude = 0
        if (phase < 32768) {
            amplitude = phase - 16384
        } else {
            amplitude = 49152 - phase
        }
        
        // Simple low-pass filter
        static int filterState = 0
        int filterMix = (smoothedFilterCutoff * 200) / 2000  // Convert to filter coefficient
        filterState = ((amplitude * filterMix) + (filterState * (255 - filterMix))) / 255
        
        // Apply volume and output
        int output = (filterState * smoothedVolume) / 2048
        signal[0] = output
        signal[1] = output
        
        // Update oscillator phase
        phase = (phase + modulatedFreq) % 65536
        
        // LED feedback shows all 4 parameters
        displayLEDs[0] = frequencyKnob      // Frequency knob position
        displayLEDs[1] = volumeKnob         // Volume knob position
        displayLEDs[2] = filterKnob         // Filter knob position
        displayLEDs[3] = lfoKnob            // LFO depth knob position
        
        yield()
    }
}
```

---

## Step 8: What You've Mastered

### 8.1 Parameter Control Skills
✅ **Real-time knob reading** from Permut8 hardware  
✅ **Parameter scaling** from 0-255 to useful ranges  
✅ **Multiple parameter control** with different scaling types  
✅ **Parameter smoothing** to prevent audio artifacts  
✅ **Advanced scaling techniques** for musical feel  

### 8.2 Interactive Plugin Concepts
**Essential Patterns:**
- Reading hardware state with `params[]` array
- Scaling parameters with mathematical formulas
- Smoothing rapid changes to prevent clicks
- Visual feedback with LED displays
- Real-time responsive control

**Musical Applications:**
- Frequency control with exponential scaling
- Volume control with linear scaling
- Filter cutoff with smooth transitions
- Modulation depth with interactive response

---

## Step 9: Experiments and Extensions

### 9.1 Try These Parameter Ideas

**Different Scaling Types:**
```impala
// Logarithmic scaling (for frequency)
int logValue = (knobValue * knobValue * knobValue) / 65536

// Bipolar scaling (-100 to +100)
int bipolar = ((knobValue - 127) * 200) / 127

// Stepped scaling (discrete values)
int stepped = (knobValue / 32) * 32  // 8 steps
```

**Parameter Modulation:**
```impala
// Use one knob to control how much another knob affects the sound
int baseValue = params[3]
int modAmount = params[4]
int finalValue = baseValue + ((someOscillator * modAmount) / 255)
```

**Parameter Memory:**
```impala
// Remember parameter settings
static int savedFreq = 500
if (params[7] > 200) {  // "Save" button
    savedFreq = smoothedFrequency
}
if (params[7] < 50) {   // "Recall" button
    smoothedFrequency = savedFreq
}
```

### 9.2 Ready for Advanced Control
**Build on your parameter skills:**
- 📖 [Light Up LEDs](light-up-leds.md) - Advanced parameter visualization
- 📖 [Simple Delay Explained](simple-delay-explained.md) - Apply knob control to time-based effects
- 📖 [Build Your First Filter](build-your-first-filter.md) - Interactive filter with multiple parameters
- 📖 [Add Controls to Effects](add-controls-to-effects.md) - Professional parameter mapping techniques

### 9.3 Professional Parameter Design
**Your knob control foundation enables:**
- Multi-parameter effect chains
- Macro controls (one knob controls multiple parameters)
- Parameter automation and sequencing
- Complex modulation routing
- Professional mixing console interfaces

**🎉 You've mastered interactive control!** Your plugins are now responsive, expressive, and musical. This is the foundation that makes electronic instruments feel alive and engaging.