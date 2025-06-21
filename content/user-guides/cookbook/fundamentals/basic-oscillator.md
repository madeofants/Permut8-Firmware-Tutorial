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
- `params[CLOCK_FREQ_PARAM_INDEX]`: Frequency (0-PARAM_MAX, controls pitch)
- `params[SWITCHES_PARAM_INDEX]`: Waveform type (0-PARAM_MAX, selects wave shape)
- `params[OPERATOR_1_PARAM_INDEX]`: Amplitude (0-PARAM_MAX, controls volume)
- `params[OPERAND_1_HIGH_PARAM_INDEX]`: Fine tune (0-PARAM_MAX, pitch adjustment)

**Waveform Types:**
- **Sine**: Pure tone, no harmonics
- **Square**: Hollow, woody character
- **Sawtooth**: Bright, buzzy character
- **Triangle**: Warm, mellow character

**Key Concepts:** Phase accumulator, frequency control, waveform generation, harmonic content

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

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

// Audio Scaling Constants (16-bit ranges for phase accumulators)
const int AUDIO_FULL_RANGE = 65536          // 16-bit full scale range (0-65535)
const int AUDIO_HALF_RANGE = 32768          // 16-bit half scale (bipolar center)
const int AUDIO_QUARTER_RANGE = 16384       // 16-bit quarter scale (triangle wave peaks)

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

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global int clock = 0            // Sample counter for timing
global array signal[2]          // Left/Right audio samples
global array params[PARAM_COUNT] // Parameter values (0-PARAM_MAX)
global array displayLEDs[4]     // LED displays
global int clockFreqLimit = 132300 // Current clock frequency limit

// Simple oscillator state
global int phase = 0            // Current phase position (0-AUDIO_FULL_RANGE-1)

function process()
locals int frequency, int wave_type, int amplitude, int fine_tune, int phase_inc, int wave_output, int output
{
    loop {
        // Read parameters
        frequency = ((int)global params[CLOCK_FREQ_PARAM_INDEX] << 4) + 100;  // 100-4196 range
        wave_type = ((int)global params[SWITCHES_PARAM_INDEX] >> 6);         // 0-3 wave types
        amplitude = ((int)global params[OPERATOR_1_PARAM_INDEX] << 3);         // 0-(PARAM_MAX*8) amplitude
        fine_tune = ((int)global params[OPERAND_1_HIGH_PARAM_INDEX] >> 3) - 16;    // -16 to +15 fine tune
        
        // Calculate phase increment (determines frequency)
        phase_inc = frequency + fine_tune;
        if (phase_inc < 50) phase_inc = 50;  // Minimum frequency
        
        // Update phase accumulator
        global phase = global phase + phase_inc;
        if (global phase >= AUDIO_FULL_RANGE) global phase = global phase - AUDIO_FULL_RANGE;
        
        // Generate waveform based on type
        if (wave_type == 0) {
            // Sine wave (approximation using triangle + smoothing)
            if (global phase < AUDIO_QUARTER_RANGE) {
                wave_output = global phase >> 2;          // Rising 0 to 4095
            } else if (global phase < AUDIO_HALF_RANGE) {
                wave_output = 4095 - ((global phase - AUDIO_QUARTER_RANGE) >> 2);  // Falling 4095 to 0
            } else if (global phase < (AUDIO_HALF_RANGE + AUDIO_QUARTER_RANGE)) {
                wave_output = -((global phase - AUDIO_HALF_RANGE) >> 2);        // Falling 0 to -4095
            } else {
                wave_output = -4095 + ((global phase - (AUDIO_HALF_RANGE + AUDIO_QUARTER_RANGE)) >> 2); // Rising -4095 to 0
            }
            
        } else if (wave_type == 1) {
            // Square wave
            if (global phase < AUDIO_HALF_RANGE) {
                wave_output = AUDIO_MAX;   // High
            } else {
                wave_output = AUDIO_MIN;  // Low
            }
            
        } else if (wave_type == 2) {
            // Sawtooth wave
            wave_output = (global phase >> 4) - AUDIO_MAX;  // -AUDIO_MAX to AUDIO_MAX ramp
            
        } else {
            // Triangle wave
            if (global phase < AUDIO_HALF_RANGE) {
                wave_output = (global phase >> 3) - AUDIO_MAX;     // Rising -AUDIO_MAX to AUDIO_MAX
            } else {
                wave_output = AUDIO_MAX - ((global phase - AUDIO_HALF_RANGE) >> 3); // Falling AUDIO_MAX to -AUDIO_MAX
            }
        }
        
        // Apply amplitude scaling
        output = (wave_output * amplitude) >> 11;  // Scale by amplitude
        
        // Prevent clipping
        if (output > AUDIO_MAX) output = AUDIO_MAX;
        if (output < AUDIO_MIN) output = AUDIO_MIN;
        
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

**Phase Accumulator**: A counter that cycles from 0 to AUDIO_FULL_RANGE-1, representing one complete waveform cycle.

**Phase Increment**: How much the phase advances each sample - larger values = higher frequency.

**Waveform Generation**: Different mathematical functions convert the linear phase into different wave shapes.

**Frequency Control**: The phase increment determines pitch. Doubling the increment doubles the frequency (one octave up).

**Parameter Control**:
- **Control 1**: Frequency (higher = higher pitch)
- **Control 2**: Waveform (0-63=sine, 64-127=square, 128-191=saw, 192-PARAM_MAX=triangle)
- **Control 3**: Amplitude (higher = louder)
- **Control 4**: Fine tune (PARAM_MID = center, adjust for precise tuning)

## Try These Settings

```impala
// Deep bass sine
global params[CLOCK_FREQ_PARAM_INDEX] = 50;   // Low frequency
global params[SWITCHES_PARAM_INDEX] = 32;   // Sine wave
global params[OPERATOR_1_PARAM_INDEX] = 200;  // Medium volume
global params[OPERAND_1_HIGH_PARAM_INDEX] = PARAM_MID;  // Center tune

// Classic square lead
global params[CLOCK_FREQ_PARAM_INDEX] = 150;  // Mid frequency
global params[SWITCHES_PARAM_INDEX] = 100;  // Square wave
global params[OPERATOR_1_PARAM_INDEX] = 180;  // Good volume
global params[OPERAND_1_HIGH_PARAM_INDEX] = PARAM_MID;  // Center tune

// Bright sawtooth
global params[CLOCK_FREQ_PARAM_INDEX] = 200;  // Higher frequency
global params[SWITCHES_PARAM_INDEX] = 160;  // Sawtooth wave
global params[OPERATOR_1_PARAM_INDEX] = 160;  // Moderate volume
global params[OPERAND_1_HIGH_PARAM_INDEX] = PARAM_MID;  // Center tune

// Warm triangle
global params[CLOCK_FREQ_PARAM_INDEX] = 120;  // Low-mid frequency
global params[SWITCHES_PARAM_INDEX] = 220;  // Triangle wave
global params[OPERATOR_1_PARAM_INDEX] = 200;  // Good volume
global params[OPERAND_1_HIGH_PARAM_INDEX] = PARAM_MID;  // Center tune
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