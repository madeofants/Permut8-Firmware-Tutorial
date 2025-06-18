# Basic Oscillator

*Generate fundamental audio waveforms*

## What This Does

Generates basic audio waveforms - sine, square, sawtooth, and triangle waves. These are the building blocks of synthesis, providing raw tones that filters and effects can shape into complex sounds.

### **Approach: Custom Firmware (Direct Synthesis)**

This recipe demonstrates **Approach 2: Custom Firmware** - implementing oscillator algorithms with direct waveform generation and phase accumulation.

**Why This Approach?**:
- **Precise waveform control** - exact mathematical generation of different wave shapes
- **Multiple waveform types** - custom algorithm for sine, square, sawtooth, triangle
- **Custom interface** - intuitive frequency/waveform/amplitude controls
- **Audio generation** - creating audio rather than processing existing audio

**How It Works**:
```
No Audio Input → [Custom oscillator algorithm generates samples] → Audio Output
```
- Phase accumulator tracks position in waveform cycle
- Mathematical functions convert phase to different wave shapes
- Direct sample generation without input processing

**Alternative Approaches**:
- **Original operators**: OSC operator provides triangular modulation, but limited to modulation use
- **Operator modification**: Could enhance OSC operator for audio-rate synthesis
- **Hybrid approach**: Use custom firmware oscillator to modulate original operator parameters

## Quick Reference

**Essential Parameters:**
- `params[0]`: Frequency (0-255, controls pitch)
- `params[1]`: Waveform type (0-255, selects wave shape)
- `params[2]`: Amplitude (0-255, controls volume)
- `params[3]`: Fine tune (0-255, pitch adjustment)

**Waveform Types:**
- **Sine**: Pure tone, no harmonics
- **Square**: Hollow, woody character
- **Sawtooth**: Bright, buzzy character
- **Triangle**: Warm, mellow character

**Key Concepts:** Phase accumulator, frequency control, waveform generation, harmonic content

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Simple oscillator state
global int phase = 0            // Current phase position (0-65535)

function process()
locals int frequency, int wave_type, int amplitude, int fine_tune, int phase_inc, int wave_output, int output
{
    loop {
        // Read parameters
        frequency = ((int)global params[0] << 4) + 100;  // 100-4196 range
        wave_type = ((int)global params[1] >> 6);         // 0-3 wave types
        amplitude = ((int)global params[2] << 3);         // 0-2040 amplitude
        fine_tune = ((int)global params[3] >> 3) - 16;    // -16 to +15 fine tune
        
        // Calculate phase increment (determines frequency)
        phase_inc = frequency + fine_tune;
        if (phase_inc < 50) phase_inc = 50;  // Minimum frequency
        
        // Update phase accumulator
        global phase = global phase + phase_inc;
        if (global phase > 65535) global phase = global phase - 65535;
        
        // Generate waveform based on type
        if (wave_type == 0) {
            // Sine wave (approximation using triangle + smoothing)
            if (global phase < 16384) {
                wave_output = global phase >> 2;          // Rising 0 to 4095
            } else if (global phase < 32768) {
                wave_output = 4095 - ((global phase - 16384) >> 2);  // Falling 4095 to 0
            } else if (global phase < 49152) {
                wave_output = -((global phase - 32768) >> 2);        // Falling 0 to -4095
            } else {
                wave_output = -4095 + ((global phase - 49152) >> 2); // Rising -4095 to 0
            }
            
        } else if (wave_type == 1) {
            // Square wave
            if (global phase < 32768) {
                wave_output = 2047;   // High
            } else {
                wave_output = -2047;  // Low
            }
            
        } else if (wave_type == 2) {
            // Sawtooth wave
            wave_output = (global phase >> 4) - 2047;  // -2047 to 2047 ramp
            
        } else {
            // Triangle wave
            if (global phase < 32768) {
                wave_output = (global phase >> 3) - 2047;     // Rising -2047 to 2047
            } else {
                wave_output = 2047 - ((global phase - 32768) >> 3); // Falling 2047 to -2047
            }
        }
        
        // Apply amplitude scaling
        output = (wave_output * amplitude) >> 11;  // Scale by amplitude
        
        // Prevent clipping
        if (output > 2047) output = 2047;
        if (output < -2047) output = -2047;
        
        // Output same signal to both channels
        global signal[0] = output;
        global signal[1] = output;
        
        // Show activity on LEDs
        global displayLEDs[0] = frequency >> 4;
        global displayLEDs[1] = wave_type << 6;
        global displayLEDs[2] = amplitude >> 3;
        global displayLEDs[3] = (global phase >> 8);  // Show phase position
        
        yield();
    }
}
```

## How It Works

**Phase Accumulator**: A counter that cycles from 0 to 65535, representing one complete waveform cycle.

**Phase Increment**: How much the phase advances each sample - larger values = higher frequency.

**Waveform Generation**: Different mathematical functions convert the linear phase into different wave shapes.

**Frequency Control**: The phase increment determines pitch. Doubling the increment doubles the frequency (one octave up).

**Parameter Control**:
- **Control 1**: Frequency (higher = higher pitch)
- **Control 2**: Waveform (0-63=sine, 64-127=square, 128-191=saw, 192-255=triangle)
- **Control 3**: Amplitude (higher = louder)
- **Control 4**: Fine tune (128 = center, adjust for precise tuning)

## Try These Settings

```impala
// Deep bass sine
params[0] = 50;   // Low frequency
params[1] = 32;   // Sine wave
params[2] = 200;  // Medium volume
params[3] = 128;  // Center tune

// Classic square lead
params[0] = 150;  // Mid frequency
params[1] = 100;  // Square wave
params[2] = 180;  // Good volume
params[3] = 128;  // Center tune

// Bright sawtooth
params[0] = 200;  // Higher frequency
params[1] = 160;  // Sawtooth wave
params[2] = 160;  // Moderate volume
params[3] = 128;  // Center tune

// Warm triangle
params[0] = 120;  // Low-mid frequency
params[1] = 220;  // Triangle wave
params[2] = 200;  // Good volume
params[3] = 128;  // Center tune
```

## Understanding Waveforms

**Harmonic Content**: Different waveforms contain different combinations of harmonics (multiples of the fundamental frequency):

- **Sine**: Only fundamental frequency - pure, clean
- **Square**: Odd harmonics (1st, 3rd, 5th...) - hollow sound
- **Sawtooth**: All harmonics - bright, full sound
- **Triangle**: Odd harmonics, weaker than square - smooth, warm

**Frequency and Pitch**: Musical notes correspond to specific frequencies:
- A4 (concert pitch) = 440 Hz
- Each octave doubles the frequency
- 12 semitones per octave

**Phase and Sync**: The phase accumulator ensures continuous, smooth oscillation without clicks or pops.

## Try These Changes

- **Multiple oscillators**: Run several oscillators at different frequencies for chords
- **LFO usage**: Use very low frequencies (0.1-10 Hz) to modulate other parameters
- **Detune**: Slightly offset multiple oscillators for thickness
- **Pulse width**: Modify square wave duty cycle for different tones

## Related Techniques

- **[Basic Filter](basic-filter.md)**: Shape the harmonic content of oscillators
- **[Envelope Basics](envelope-basics.md)**: Control oscillator amplitude over time

---
*Part of the [Permut8 Cookbook](../index.md) series*