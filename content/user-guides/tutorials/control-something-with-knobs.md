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
global array params[8]





```

### 1.2 Which Knobs Do What
**Hardware mapping** (check your Permut8 manual for exact layout):
- `params[0]` through `params[7]` = 8 hardware knobs
- Values always range from 0 to 255
- Values update in real-time as you turn knobs

### 1.3 The Challenge: Scaling Parameters
**Raw knob values (0-255) rarely match what you need:**
```impala

int knobValue = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]


int volume = ?
int frequency = ?
int delayTime = ?
```

**Solution: Parameter scaling math**

---

## Step 2: Your First Knob Control

### 2.1 Volume Control with Knob 1
Create `knob_volume_control.impala`:

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]

function process()
{
    loop {

        int knobValue = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        

        int volume = knobValue
        

        signal[0] = (signal[0] * volume) / 255
        signal[1] = (signal[1] * volume) / 255
        

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

int scaledValue = minValue + ((knobValue * (maxValue - minValue)) / 255)


int volume = 0 + ((knobValue * (1000 - 0)) / 255)
int frequency = 100 + ((knobValue * (2000 - 100)) / 255)
int delayTime = 1000 + ((knobValue * (20000 - 1000)) / 255)
```

### 3.2 Common Scaling Examples
**Different parameter types need different ranges:**

```impala

int volume = knobValue


int frequency = 100 + ((knobValue * 1900) / 255)


int delaySamples = 4410 + ((knobValue * 39690) / 255)


int cutoff = 50 + ((knobValue * knobValue) / 32)
```

---

## Step 4: Multi-Knob Control

### 4.1 Control Multiple Parameters
Let's control an oscillator with 3 knobs:

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]

global int phase = 0

function process()
{
    loop {

        int frequencyKnob = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        int volumeKnob = (int)global params[OPERAND_2_LOW_PARAM_INDEX]
        int waveformKnob = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]
        

        int frequency = 50 + ((frequencyKnob * 950) / 255)
        int volume = volumeKnob
        int waveform = waveformKnob / 64
        

        int amplitude = 0
        if (waveform == 0) {

            if (phase < 32768) {
                amplitude = phase - 16384
            } else {
                amplitude = 49152 - phase
            }
        } else if (waveform == 1) {

            if (phase < 32768) {
                amplitude = 16384
            } else {
                amplitude = -16384
            }
        } else if (waveform == 2) {

            amplitude = (phase / 2) - 16384
        } else {

            amplitude = (phase * 7919) % 32768 - 16384
        }
        

        int output = (amplitude * volume) / 2048
        signal[0] = output
        signal[1] = output
        

        phase = (phase + frequency) % 65536
        

        displayLEDs[0] = frequencyKnob
        displayLEDs[1] = volumeKnob
        displayLEDs[2] = waveformKnob
        displayLEDs[3] = waveform * 64
        
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

global int smoothedFrequency = 500
global int smoothedVolume = 128


function process()
{
    loop {

        int frequencyKnob = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        int volumeKnob = (int)global params[OPERAND_2_LOW_PARAM_INDEX]
        

        int targetFrequency = 50 + ((frequencyKnob * 950) / 255)
        int targetVolume = volumeKnob
        

        int freqDiff = targetFrequency - smoothedFrequency
        smoothedFrequency = smoothedFrequency + (freqDiff / 8)
        
        int volDiff = targetVolume - smoothedVolume
        smoothedVolume = smoothedVolume + (volDiff / 8)
        

        int frequency = smoothedFrequency
        int volume = smoothedVolume
        

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

int frequency = 50 + ((knobValue * 1950) / 255)


int scaledKnob = (knobValue * knobValue) / 255
int frequency = 50 + ((scaledKnob * 1950) / 255)
```

### 6.2 Parameter Ranges with Detents
**Create "notches" or preferred positions:**

```impala

int rawValue = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
int quantizedValue = (rawValue / 32) * 32


int noteKnob = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
int note = noteKnob / 21
```

### 6.3 Parameter Interaction
**Make knobs affect each other:**

```impala

int baseFreq = 100 + ((params[OPERAND_1_HIGH_PARAM_INDEX] * 400) / 255)
int modDepth = (params[OPERAND_1_LOW_PARAM_INDEX] * 200) / 255
int finalFreq = baseFreq + (modDepth * sin(phase/100))
```

---

## Step 7: Complete Interactive Plugin

### 7.1 Full-Featured Knob-Controlled Synthesizer
Here's a complete example using all techniques:

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]


global int phase = 0
global int lfoPhase = 0


global int smoothedFrequency = 500
global int smoothedVolume = 128
global int smoothedFilterCutoff = 1000
global int smoothedLFODepth = 0

function process()
{
    loop {

        int frequencyKnob = params[3]
        int volumeKnob = params[4]
        int filterKnob = params[5]
        int lfoKnob = params[6]
        

        int targetFrequency = 100 + ((frequencyKnob * frequencyKnob) / 64)
        int targetVolume = volumeKnob
        int targetFilter = 200 + ((filterKnob * 1800) / 255)
        int targetLFODepth = (lfoKnob * 100) / 255
        

        smoothedFrequency = smoothedFrequency + (targetFrequency - smoothedFrequency) / 16
        smoothedVolume = smoothedVolume + (targetVolume - smoothedVolume) / 16
        smoothedFilterCutoff = smoothedFilterCutoff + (targetFilter - smoothedFilterCutoff) / 16
        smoothedLFODepth = smoothedLFODepth + (targetLFODepth - smoothedLFODepth) / 16
        

        lfoPhase = (lfoPhase + 50) % 65536
        int lfoValue = 0
        if (lfoPhase < 32768) {
            lfoValue = lfoPhase - 16384
        } else {
            lfoValue = 49152 - lfoPhase
        }
        

        int modulatedFreq = smoothedFrequency + ((lfoValue * smoothedLFODepth) / 16384)
        

        int amplitude = 0
        if (phase < 32768) {
            amplitude = phase - 16384
        } else {
            amplitude = 49152 - phase
        }
        

        static int filterState = 0
        int filterMix = (smoothedFilterCutoff * 200) / 2000
        filterState = ((amplitude * filterMix) + (filterState * (255 - filterMix))) / 255
        

        int output = (filterState * smoothedVolume) / 2048
        signal[0] = output
        signal[1] = output
        

        phase = (phase + modulatedFreq) % 65536
        

        displayLEDs[0] = frequencyKnob
        displayLEDs[1] = volumeKnob
        displayLEDs[2] = filterKnob
        displayLEDs[3] = lfoKnob
        
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

int logValue = (knobValue * knobValue * knobValue) / 65536


int bipolar = ((knobValue - 127) * 200) / 127


int stepped = (knobValue / 32) * 32
```

**Parameter Modulation:**
```impala

int baseValue = params[OPERAND_1_HIGH_PARAM_INDEX]
int modAmount = params[OPERAND_1_LOW_PARAM_INDEX]
int finalValue = baseValue + ((someOscillator * modAmount) / 255)
```

**Parameter Memory:**
```impala

static int savedFreq = 500
if (params[OPERAND_2_LOW_PARAM_INDEX] > 200) {
    savedFreq = smoothedFrequency
}
if (params[OPERAND_2_LOW_PARAM_INDEX] < 50) {
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