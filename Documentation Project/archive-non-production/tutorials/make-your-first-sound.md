# Make Your First Sound - Simple Tone Generator

## What This Tutorial Does
Create your first sound-generating plugin! Instead of just processing incoming audio, you'll build a simple tone generator that creates audio from scratch. In 15 minutes, you'll hear your own custom-generated sound coming from Permut8.

## What You'll Learn
- How to generate audio instead of just processing it
- Basic oscillator principles and digital synthesis
- How to create musical frequencies and tones
- The difference between processing audio vs. generating audio
- Foundation concepts for all synthesizers and tone generators

**Prerequisites**: None - this tutorial stands alone!  
**Time Required**: 15 minutes  
**Difficulty**: Beginner

---

## Step 1: Understanding Sound Generation

### 1.1 Processing vs. Generating
**What you did before** (processing):
```impala
signal[0] = signal[0] / 2  // Take incoming audio, modify it
```

**What you'll do now** (generating):
```impala
signal[0] = myGeneratedSound  // Create audio from scratch, replace input
```

### 1.2 How Digital Oscillators Work
**Basic concept:** Repeatedly output numbers that, when played fast enough, create sound waves.

```
For a musical tone:
- Need to complete multiple wave cycles per second to create pitch
- At Permut8's variable sample rate (0-352kHz), cycle length varies with sample rate
- Create a repeating pattern: 0, 500, 1000, 500, 0, -500, -1000, -500, repeat...
```

### 1.3 Simple Waveforms
**Sine wave:** Smooth, pure tone (like a flute)  
**Triangle wave:** Bright but smooth (like a simple synthesizer)  
**Square wave:** Harsh, buzzy (like old video games)  

We'll start with a triangle wave because it's simple to calculate.

---

## Step 2: Build a Simple Tone Generator

### 2.1 Create the Basic Structure
Create `tone_generator.impala`:

```impala
// Simple Tone Generator - My First Sound
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

global array signal[2]
global array params[8]
global array displayLEDs[4]

// Oscillator state
global int phase = 0        // Current position in the waveform
global int frequency = 100  // How fast the wave repeats

function process()
{
    loop {
        // Generate triangle wave
        int amplitude = 0
        if (phase < 32768) {
            amplitude = phase - 16384      // Rising part: -16384 to +16384
        } else {
            amplitude = 49152 - phase      // Falling part: +16384 to -16384
        }
        
        // Scale to audio range and output
        int output = amplitude / 8  // Scale down to reasonable volume
        signal[0] = output          // Left channel
        signal[1] = output          // Right channel (same sound)
        
        // Update phase for next sample
        phase = (phase + frequency) % 65536
        
        yield()
    }
}
```

### 2.2 Test Your First Generated Sound
1. **Compile**: `PikaCmd.exe -compile tone_generator.impala`
2. **Load**: `patch tone_generator.gazl`
3. **Expected result**: You should hear a low-pitched tone!
4. **Success indicator**: Steady tone playing regardless of input audio

**🎉 You just created sound from nothing!** Your plugin is now generating audio instead of processing it.

---

## Step 3: Understanding the Oscillator

### 3.1 The Phase Variable
```impala
global int phase = 0  // Current position in waveform (0 to 65535)
```

**Think of phase as:** A position on a circular track
- `0` = start of waveform cycle
- `32768` = halfway through cycle  
- `65535` = end of cycle (wraps back to 0)

### 3.2 The Triangle Wave Math
```impala
if (phase < 32768) {
    amplitude = phase - 16384      // First half: rises from -16384 to +16384
} else {
    amplitude = 49152 - phase      // Second half: falls from +16384 to -16384
}
```

**Visualization:**
```
Phase:     0    16384   32768   49152   65536
           |       |       |       |       |
Amplitude: -16384   0    +16384    0    -16384
Wave:       \      /\      /\      /
             \    /  \    /  \    /
              \  /    \  /    \  /
               \/      \/      \/
```

### 3.3 Frequency Control
```impala
phase = (phase + frequency) % 65536
```

**How frequency works:**
- `frequency = 100`: Phase increases slowly → low-pitched sound
- `frequency = 1000`: Phase increases quickly → high-pitched sound
- The `% 65536` wraps phase back to 0 when it exceeds 65535

---

## Step 4: Add Pitch Control

### 4.1 Make the Frequency Variable
Replace your `process()` function:

```impala
function process()
{
    loop {
        // Simple frequency control (we'll add knob control later)
        frequency = 200  // Try different values: 100=low, 500=medium, 1000=high
        
        // Generate triangle wave (same as before)
        int amplitude = 0
        if (phase < 32768) {
            amplitude = phase - 16384
        } else {
            amplitude = 49152 - phase
        }
        
        int output = amplitude / 8
        signal[0] = output
        signal[1] = output
        
        // Update phase
        phase = (phase + frequency) % 65536
        
        yield()
    }
}
```

### 4.2 Experiment with Different Frequencies
**Try these values** by changing the `frequency = 200` line:

| Frequency Value | Approximate Pitch | Sound Character |
|----------------|-------------------|-----------------|
| `50` | Very low bass | Deep rumble |
| `100` | Low bass | Bass note |
| `200` | Medium-low | Comfortable listening |
| `400` | Medium | Clear tone |
| `800` | Medium-high | Bright tone |
| `1200` | High | Piercing tone |

**Recompile and test** each time you change the frequency value.

---

## Step 5: Add Volume Control

### 5.1 Controllable Volume
Add volume control to prevent ear damage and allow for musical dynamics:

```impala
function process()
{
    loop {
        frequency = 200
        
        // Volume control (0 = silent, 1000 = loud)
        int volume = 500  // Medium volume - adjust as needed
        
        // Generate triangle wave
        int amplitude = 0
        if (phase < 32768) {
            amplitude = phase - 16384
        } else {
            amplitude = 49152 - phase
        }
        
        // Apply volume control
        int output = (amplitude * volume) / 8000  // Scale by volume and reduce overall level
        
        signal[0] = output
        signal[1] = output
        
        phase = (phase + frequency) % 65536
        
        yield()
    }
}
```

### 5.2 Safe Volume Levels
**Volume guidelines:**
- `0` = Silent
- `100` = Very quiet
- `500` = Comfortable listening level
- `1000` = Loud but safe
- `2000+` = Use caution - can be very loud!

**Always start with low volumes** when testing new sounds.

---

## Step 6: Add Musical Frequencies

### 6.1 Make Musical Notes
Replace the frequency calculation with musical note frequencies:

```impala
function process()
{
    loop {
        // Musical note selection
        int note = 5  // Try values 0-11 for different notes
        
        // Convert note to frequency (approximate musical scale)
        if (note == 0) frequency = 65   // C
        else if (note == 1) frequency = 73   // C#
        else if (note == 2) frequency = 82   // D
        else if (note == 3) frequency = 87   // D#
        else if (note == 4) frequency = 98   // E
        else if (note == 5) frequency = 110  // F
        else if (note == 6) frequency = 123  // F#
        else if (note == 7) frequency = 131  // G
        else if (note == 8) frequency = 147  // G#
        else if (note == 9) frequency = 165  // A
        else if (note == 10) frequency = 175 // A#
        else frequency = 196                 // B
        
        int volume = 500
        
        // Generate triangle wave (same as before)
        int amplitude = 0
        if (phase < 32768) {
            amplitude = phase - 16384
        } else {
            amplitude = 49152 - phase
        }
        
        int output = (amplitude * volume) / 8000
        signal[0] = output
        signal[1] = output
        
        phase = (phase + frequency) % 65536
        
        yield()
    }
}
```

### 6.2 Try Different Musical Notes
**Change the `note = 5` line** to hear different pitches:
- `note = 0` = C (low)
- `note = 4` = E (major third)
- `note = 7` = G (perfect fifth)
- `note = 9` = A (musical reference note)
- `note = 11` = B (leading tone)

**Musical tip:** Notes 0, 4, and 7 together make a C major chord!

---

## Step 7: Add LED Visualization

### 7.1 Visual Feedback for Your Oscillator
Add this before `yield()`:

```impala
// LED visualization
displayLEDs[0] = note * 20        // Show current note selection
displayLEDs[1] = volume / 4       // Show volume level
displayLEDs[2] = (phase / 8192)   // Show oscillator phase (creates moving pattern)

// Activity indicator
if (output > 100 || output < -100) {
    displayLEDs[3] = 0xFF  // Flash when sound is playing
} else {
    displayLEDs[3] = 0x01  // Dim when quiet
}
```

### 7.2 Understanding the LED Display
- **LED 1**: Shows which note is selected
- **LED 2**: Shows volume level
- **LED 3**: Moving pattern that shows oscillator speed
- **LED 4**: Flashes when sound is loud enough to hear

---

## Step 8: Complete Tone Generator

### 8.1 Final Version with All Features
Here's your complete first sound generator:

```impala
// Complete Tone Generator - Musical Note Synthesizer
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]

// Oscillator state variables
global int phase = 0        // Current waveform position (0-65535)
global int frequency = 110  // Oscillator frequency
global int volume = 500     // Output volume level

function process()
{
    loop {
        // Musical note selection (change this value to hear different notes)
        int note = 5  // 0-11 for chromatic scale
        
        // Convert note number to oscillator frequency
        if (note == 0) frequency = 65        // C (low C)
        else if (note == 1) frequency = 73   // C# 
        else if (note == 2) frequency = 82   // D
        else if (note == 3) frequency = 87   // D#
        else if (note == 4) frequency = 98   // E
        else if (note == 5) frequency = 110  // F
        else if (note == 6) frequency = 123  // F#
        else if (note == 7) frequency = 131  // G
        else if (note == 8) frequency = 147  // G#
        else if (note == 9) frequency = 165  // A (reference pitch)
        else if (note == 10) frequency = 175 // A#
        else frequency = 196                 // B
        
        // Generate triangle wave oscillator
        int amplitude = 0
        if (phase < 32768) {
            // First half of wave: rising from -16384 to +16384
            amplitude = phase - 16384
        } else {
            // Second half of wave: falling from +16384 to -16384
            amplitude = 49152 - phase
        }
        
        // Apply volume control and scale to audio range
        int output = (amplitude * volume) / 8000
        
        // Output generated sound (replaces any input audio)
        signal[0] = output  // Left channel
        signal[1] = output  // Right channel (mono output)
        
        // LED visual feedback
        displayLEDs[0] = note * 20            // Current note indicator
        displayLEDs[1] = volume / 4           // Volume level display
        displayLEDs[2] = (phase / 8192)       // Oscillator phase (moving pattern)
        
        // Activity indicator (flashes with audio)
        if (output > 100 || output < -100) {
            displayLEDs[3] = 0xFF             // Bright when sound is active
        } else {
            displayLEDs[3] = 0x01             // Dim when quiet
        }
        
        // Update oscillator phase for next sample
        phase = (phase + frequency) % 65536
        
        yield()
    }
}
```

---

## Step 9: What You've Accomplished

### 9.1 Sound Generation Skills
✅ **Created audio from scratch** instead of just processing input  
✅ **Built a digital oscillator** with triangle wave generation  
✅ **Implemented musical frequencies** for recognizable pitches  
✅ **Added volume control** for safe and musical dynamics  
✅ **Created visual feedback** showing oscillator state  

### 9.2 Understanding Gained
**Digital Synthesis Concepts:**
- Phase accumulation and waveform generation
- Frequency-to-pitch relationships
- Audio sample generation at 44.1kHz rate
- Waveform mathematics and audio scaling

**Programming Patterns:**
- State variables for continuous processes
- Mathematical waveform generation
- Real-time parameter control
- Audio range management and clipping prevention

---

## Step 10: Experiments and What's Next

### 10.1 Try These Modifications

**Different Waveforms:**
```impala
// Square wave (buzzy sound)
if (phase < 32768) {
    amplitude = 16384   // High for first half
} else {
    amplitude = -16384  // Low for second half
}

// Sawtooth wave (bright, buzzy)
amplitude = (phase / 2) - 16384  // Linear ramp

// Sine wave approximation (smooth, pure)
// This is more complex - try the triangle first!
```

**Multiple Oscillators:**
```impala
// Add a second oscillator at different frequency
int phase2 = 0  // Add this as global variable
int frequency2 = frequency * 2  // Octave higher
// Generate second wave and mix: output = (wave1 + wave2) / 2
```

**Frequency Sweeps:**
```impala
// Slowly change frequency over time
static int sweepCounter = 0
sweepCounter = (sweepCounter + 1) % 10000
frequency = 100 + (sweepCounter / 50)  // Sweep from 100 to 300
```

### 10.2 Ready for Next Steps
**Build on your sound generation skills:**
- 📖 [Control Something with Knobs](control-something-with-knobs.md) - Use hardware knobs to control your oscillator
- 📖 [Light Up LEDs](light-up-leds.md) - Advanced LED patterns and audio visualization
- 📖 [Simple Delay Explained](simple-delay-explained.md) - Add delay effects to your generated sounds
- 📖 [Build Your First Filter](build-your-first-filter.md) - Shape your generated sounds with filtering

### 10.3 Advanced Sound Generation
**Your oscillator foundation enables:**
- Multi-oscillator synthesizers
- Frequency modulation (FM synthesis)
- Amplitude modulation and ring modulation
- Complex waveform generation
- Chord and harmony generators

**🎉 You're now a digital sound designer!** You've mastered the fundamental skill of creating audio from scratch - the foundation of all synthesizers and electronic music.