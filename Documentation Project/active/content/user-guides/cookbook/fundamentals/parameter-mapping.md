# Parameter Mapping

*Convert knob values into useful parameter ranges*

## What This Does

Parameter mapping transforms raw operand values (0-255) into meaningful ranges for your audio algorithms. Good mapping makes controls feel natural and musical instead of awkward or unusable.

## Permut8 Parameter Interface Architecture

### **Understanding the Interface System**

**Original Permut8 Interface:**
- **Instruction 1**: High Operand (`params[3]`) + Low Operand (`params[4]`)
- **Instruction 2**: High Operand (`params[6]`) + Low Operand (`params[7]`)
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
//    Original: User sets switches/drags LED to value 128
//    Custom: User turns knob to middle position
//
// 2. Parameter Storage:
//    params[3] = 128  (same value, different input method)
//
// 3. Algorithm Processing:
int cutoff_freq = ((int)params[3] * 8000) / 255;  // 0-8000 Hz range
//    Result: 128 * 8000 / 255 = ~4000 Hz
//
// 4. LED Feedback:
displayLEDs[0] = params[3];  // Show current parameter state
```

### **panelTextRows Layout System**
```impala
readonly array panelTextRows[8] = {
    "",                                // Row 0
    "",                                // Row 1
    "",                                // Row 2
    "FILTER |-- CUTOFF --| |-- RESO --|", // Row 3: params[3] left, params[6] right
    "",                                // Row 4
    "",                                // Row 5
    "",                                // Row 6
    "EFFECT |-- MIX -----| |-- GAIN --|"  // Row 7: params[4] left, params[7] right
};

// Layout maps to parameter positions:
// Row 3: Instruction High Operands (params[3], params[6])
// Row 7: Instruction Low Operands (params[4], params[7])
```

## Quick Reference

**Essential Parameters:**
- `params[3,4,6,7]`: Instruction operand values (0-255)
- `params[0]`: Clock frequency (system controlled)
- `params[1]`: Switch states (bitmask)
- `target_range`: Your algorithm's useful range (often 0-2047)
- `smoothing`: Prevents parameter clicks during changes

**Common Mappings:**
- **Mix controls**: Linear scaling (equal steps feel natural)
- **Frequency**: Logarithmic scaling (matches musical perception)
- **Gain**: Square-law or exponential scaling
- **Time**: Linear for short delays, logarithmic for long delays

**Key Concepts:** Range scaling, parameter smoothing, curve shaping, musical response

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Parameter smoothing state
global int smooth_cutoff = 1000 // Current cutoff value
global int smooth_resonance = 512 // Current resonance value
global int smooth_mix = 1024    // Current mix value

function process()
locals int cutoff_target, int resonance_target, int mix_target, int filtered_signal, int dry_signal, int wet_signal, int output
{
    loop {
        // Linear mapping: Mix control (0-2047 range)
        mix_target = ((int)global params[0] << 3);  // 0-255 → 0-2040
        
        // Exponential mapping: Cutoff frequency (200-2000 range)
        cutoff_target = 200 + (((int)global params[1] * (int)global params[1]) >> 4); // Quadratic curve
        if (cutoff_target > 2000) cutoff_target = 2000;
        
        // Linear with offset: Resonance (256-1792 range for stable filter)
        resonance_target = 256 + (((int)global params[2] * 1536) >> 8);
        
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
        if (filtered_signal > 2047) filtered_signal = 2047;
        if (filtered_signal < -2047) filtered_signal = -2047;
        
        // Mix dry and filtered signals
        wet_signal = (filtered_signal * global smooth_mix) >> 11;
        output = dry_signal + wet_signal;
        
        // Prevent clipping
        if (output > 2047) output = 2047;
        if (output < -2047) output = -2047;
        
        // Output mixed signal
        global signal[0] = output;
        global signal[1] = output;
        
        // Show parameter values on LEDs
        global displayLEDs[0] = global smooth_cutoff >> 3; // Show cutoff
        global displayLEDs[1] = global smooth_resonance >> 3; // Show resonance
        global displayLEDs[2] = global smooth_mix >> 3;   // Show mix level
        global displayLEDs[3] = (int)global params[3];    // Show raw param 4
        
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
params[0] = 128;  // 50% mix
params[1] = 100;  // Low cutoff
params[2] = 80;   // Light resonance

// Bright sound
params[0] = 200;  // Heavy wet signal
params[1] = 200;  // High cutoff
params[2] = 60;   // Low resonance

// Dark sound
params[0] = 80;   // Light wet signal
params[1] = 50;   // Very low cutoff
params[2] = 150;  // High resonance

// Extreme effect
params[0] = 255;  // Full wet
params[1] = 255;  // Maximum cutoff
params[2] = 200;  // Strong resonance
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