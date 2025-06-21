# Parameter Mapping

*Convert knob values into useful parameter ranges*

## What This Does

Parameter mapping transforms raw operand values (0-255) into meaningful ranges for your audio algorithms. Good mapping makes controls feel natural and musical instead of awkward or unusable.

## Permut8 Parameter Interface Architecture

### **Understanding the Interface System**

**Original Permut8 Interface:**
- **Instruction 1**: High Operand (`params[OPERAND_1_HIGH_PARAM_INDEX]`) + Low Operand (`params[OPERAND_1_LOW_PARAM_INDEX]`)
- **Instruction 2**: High Operand (`params[OPERAND_2_HIGH_PARAM_INDEX]`) + Low Operand (`params[OPERAND_2_LOW_PARAM_INDEX]`)
- **User Control**: Scrollable LED displays + bit switches (8 switches per operand)
- **Display**: Each operand shows as hex value (00-FF) representing 0-255

**Custom Firmware Override:**
- **Transform**: Convert operand parameters into direct knob controls
- **Interface**: `panelTextRows` replaces hex displays with custom labels
- **Experience**: Same parameter data, intuitive user interface

### **Data Flow Example**
```impala
// User interaction → Parameter storage → Algorithm processing

// 1. User Action (either interface type):
//    Original: User sets switches/drags LED to value PARAM_MID
//    Custom: User turns knob to middle position
//
// 2. Parameter Storage:
//    params[OPERAND_1_HIGH_PARAM_INDEX] = PARAM_MID  (same value, different input method)
//
// 3. Algorithm Processing:
int cutoff_freq = ((int)params[OPERAND_1_HIGH_PARAM_INDEX] * 8000) / 255;  // 0-8000 Hz range
//    Result: PARAM_MID * 8000 / 255 = ~4000 Hz
//
// 4. LED Feedback:
displayLEDs[0] = params[OPERAND_1_HIGH_PARAM_INDEX];  // Show current parameter state
```

### **panelTextRows Layout System**
```impala
readonly array panelTextRows[8] = {
    "",                                // Row 0
    "",                                // Row 1
    "",                                // Row 2
    "FILTER |-- CUTOFF --| |-- RESO --|", // Row 3: params[OPERAND_1_HIGH_PARAM_INDEX] left, params[OPERAND_2_HIGH_PARAM_INDEX] right
    "",                                // Row 4
    "",                                // Row 5
    "",                                // Row 6
    "EFFECT |-- MIX -----| |-- GAIN --|"  // Row 7: params[OPERAND_1_LOW_PARAM_INDEX] left, params[OPERAND_2_LOW_PARAM_INDEX] right
};

// Layout maps to parameter positions:
// Row 3: Instruction High Operands (params[OPERAND_1_HIGH_PARAM_INDEX], params[OPERAND_2_HIGH_PARAM_INDEX])
// Row 7: Instruction Low Operands (params[OPERAND_1_LOW_PARAM_INDEX], params[OPERAND_2_LOW_PARAM_INDEX])
```

## Quick Reference

**Essential Parameters:**
- `params[OPERAND_1_HIGH_PARAM_INDEX,OPERAND_1_LOW_PARAM_INDEX,OPERAND_2_HIGH_PARAM_INDEX,OPERAND_2_LOW_PARAM_INDEX]`: Instruction operand values (0-255)
- `params[CLOCK_FREQ_PARAM_INDEX]`: Clock frequency (system controlled)
- `params[SWITCHES_PARAM_INDEX]`: Switch states (bitmask)
- `target_range`: Your algorithm's useful range (often 0-AUDIO_MAX)
- `smoothing`: Prevents parameter clicks during changes

**Common Mappings:**
- **Mix controls**: Linear scaling (equal steps feel natural)
- **Frequency**: Logarithmic scaling (matches musical perception)
- **Gain**: Square-law or exponential scaling
- **Time**: Linear for short delays, logarithmic for long delays

**Key Concepts:** Range scaling, parameter smoothing, curve shaping, musical response

## Complete Code

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

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global int clock                 // Sample counter for timing
global array signal[2]          // Left/Right audio samples
global array params[PARAM_COUNT] // Parameter values (0-255)
global array displayLEDs[4]     // LED displays
global int clockFreqLimit        // Current clock frequency limit

// Parameter smoothing state
global int smooth_cutoff = 1000 // Current cutoff value
global int smooth_resonance = 512 // Current resonance value
global int smooth_mix = 1024    // Current mix value

function process()
locals int cutoff_target, int resonance_target, int mix_target, int filtered_signal, int dry_signal, int wet_signal, int output
{
    loop {
        // Linear mapping: Mix control (0-AUDIO_MAX range)
        mix_target = ((int)global params[CLOCK_FREQ_PARAM_INDEX] << 3);  // 0-255 → 0-2040
        
        // Exponential mapping: Cutoff frequency (200-2000 range)
        cutoff_target = 200 + (((int)global params[SWITCHES_PARAM_INDEX] * (int)global params[SWITCHES_PARAM_INDEX]) >> 4); // Quadratic curve
        if (cutoff_target > 2000) cutoff_target = 2000;
        
        // Linear with offset: Resonance (256-1792 range for stable filter)
        resonance_target = 256 + (((int)global params[OPERATOR_1_PARAM_INDEX] * 1536) >> 8);
        
        // Smooth parameter changes to prevent clicks
        global smooth_cutoff = global smooth_cutoff + ((cutoff_target - global smooth_cutoff) >> 4);
        global smooth_resonance = global smooth_resonance + ((resonance_target - global smooth_resonance) >> 4);
        global smooth_mix = global smooth_mix + ((mix_target - global smooth_mix) >> 4);
        
        // Simple one-pole filter example using mapped parameters
        dry_signal = (int)global signal[0];
        
        // Basic low-pass filter calculation
        filtered_signal = global smooth_cutoff + 
            (((dry_signal - global smooth_cutoff) * global smooth_resonance) >> 11);
        
        // Limit filter output
        if (filtered_signal > AUDIO_MAX) filtered_signal = AUDIO_MAX;
        if (filtered_signal < AUDIO_MIN) filtered_signal = AUDIO_MIN;
        
        // Mix dry and filtered signals
        wet_signal = (filtered_signal * global smooth_mix) >> 11;
        output = dry_signal + wet_signal;
        
        // Prevent clipping
        if (output > AUDIO_MAX) output = AUDIO_MAX;
        if (output < AUDIO_MIN) output = AUDIO_MIN;
        
        // Output mixed signal
        global signal[0] = output;
        global signal[1] = output;
        
        // Show parameter values on LEDs
        global displayLEDs[0] = global smooth_cutoff >> 3; // Show cutoff
        global displayLEDs[1] = global smooth_resonance >> 3; // Show resonance
        global displayLEDs[2] = global smooth_mix >> 3;   // Show mix level
        global displayLEDs[3] = (int)global params[OPERAND_1_HIGH_PARAM_INDEX];    // Show raw param 4
        
        yield();
    }
}
```

## How It Works

**Linear Mapping**: Simplest scaling where equal knob movements create equal parameter changes. Good for mix controls and balance.

**Exponential Mapping**: Using squared values creates more natural feeling controls for frequency and gain parameters.

**Parameter Smoothing**: Prevents clicks and zipper noise by gradually changing values instead of jumping immediately.

**Range Mapping**: Converting 0-255 knob values into useful ranges like 200-2000 for filter cutoff frequencies.

**Parameter Control**:
- **Control 1**: Mix level (0-255 → 0-2040 linear mapping)
- **Control 2**: Cutoff frequency (0-255 → 200-2000 exponential mapping)  
- **Control 3**: Resonance (0-255 → 256-1792 linear with offset)

## Try These Settings

```impala
// Smooth mixing
global params[CLOCK_FREQ_PARAM_INDEX] = PARAM_MID;  // 50% mix
global params[SWITCHES_PARAM_INDEX] = 100;  // Low cutoff
global params[OPERATOR_1_PARAM_INDEX] = 80;   // Light resonance

// Bright sound
global params[CLOCK_FREQ_PARAM_INDEX] = 200;  // Heavy wet signal
global params[SWITCHES_PARAM_INDEX] = 200;  // High cutoff
global params[OPERATOR_1_PARAM_INDEX] = 60;   // Low resonance

// Dark sound
global params[CLOCK_FREQ_PARAM_INDEX] = 80;   // Light wet signal
global params[SWITCHES_PARAM_INDEX] = 50;   // Very low cutoff
global params[OPERATOR_1_PARAM_INDEX] = 150;  // High resonance

// Extreme effect
global params[CLOCK_FREQ_PARAM_INDEX] = 255;  // Full wet
global params[SWITCHES_PARAM_INDEX] = 255;  // Maximum cutoff
global params[OPERATOR_1_PARAM_INDEX] = 200;  // Strong resonance
```

## Understanding Parameter Curves

**Linear Response**: Equal knob steps = equal parameter steps. Good for mix controls and panning.

**Exponential Response**: Using squared values gives more control at low values, faster changes at high values. Good for frequencies and gain.

**Smoothing**: Gradual parameter changes prevent audio clicks. Faster smoothing for quick response, slower for smooth changes.

**Range Mapping**: Converting knob ranges (0-255) to useful parameter ranges (like 200-2000 Hz) with proper scaling.

## Try These Changes

- **Custom curves**: Create lookup tables for specific parameter responses
- **Multi-parameter control**: Control several parameters with one knob
- **Quantized mapping**: Snap parameters to musical steps (notes, rhythms)
- **Linked parameters**: Make parameters automatically adjust based on others

## Related Techniques

- **[Basic Filter](basic-filter.md)**: Apply parameter mapping to filter controls
- **[Envelope Basics](envelope-basics.md)**: Map time parameters naturally

---
*Part of the [Permut8 Cookbook](../index.md) series*