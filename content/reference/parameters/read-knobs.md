# Read Knobs

*Basic parameter reading and scaling techniques*

## What This Does

Shows how to read knob values from parameters and convert them to useful ranges for audio processing. Covers linear scaling, stepped values, and visual feedback techniques.

## Quick Reference

**Essential Parameters:**
- `params[0-7]`: Knob values (0-255 range)
- Parameter scaling formulas for common ranges
- LED feedback for parameter visualization

**Core Techniques:**
- **Linear scaling**: Map 0-255 to any range
- **Stepped values**: Create discrete parameter steps  
- **Range mapping**: Convert to frequency, gain, time values
- **Visual feedback**: Display parameter values on LEDs

**Key Concepts:** Parameter scaling, range mapping, visual feedback, bit manipulation

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

function process()
locals int knob1, int knob2, int knob3, int knob4, int gain_level, int cutoff_freq, int steps, int mix_amount, int input_sample, int processed_sample, int output_sample
{
    loop {
        // Read all knob values (always 0-255 from hardware)
        knob1 = (int)global params[0];    // First knob
        knob2 = (int)global params[1];    // Second knob
        knob3 = (int)global params[2];    // Third knob
        knob4 = (int)global params[3];    // Fourth knob
        
        // === PARAMETER SCALING EXAMPLES ===
        
        // Linear scaling: knob1 to gain (0-2047 range)
        gain_level = (knob1 << 3);        // 0-255 → 0-2040
        
        // Frequency range: knob2 to cutoff (200-2000 Hz)
        cutoff_freq = 200 + ((knob2 * 1800) >> 8);  // 200-2000 range
        
        // Stepped values: knob3 to 8 discrete steps
        steps = knob3 >> 5;               // Divide by 32 → 0-7 steps
        
        // Percentage: knob4 to mix amount (0-100%)
        mix_amount = (knob4 * 100) >> 8;  // 0-100 percentage
        
        // === AUDIO PROCESSING USING SCALED PARAMETERS ===
        
        // Read input sample
        input_sample = (int)global signal[0];
        
        // Apply gain from knob1
        processed_sample = (input_sample * gain_level) >> 11;
        
        // Simple tone control based on knob2 cutoff frequency
        if (cutoff_freq > 1000) {
            // High cutoff: brighten signal
            processed_sample = processed_sample + (processed_sample >> 3);
        } else {
            // Low cutoff: darken signal  
            processed_sample = processed_sample - (processed_sample >> 3);
        }
        
        // Apply stepped processing based on knob3
        if (steps > 4) {
            // High steps: add distortion
            if (processed_sample > 1024) processed_sample = 1024;
            if (processed_sample < -1024) processed_sample = -1024;
        }
        
        // Mix dry/wet based on knob4
        output_sample = ((input_sample * (100 - mix_amount)) + 
                        (processed_sample * mix_amount)) / 100;
        
        // Prevent clipping
        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        
        // Output to both channels
        global signal[0] = output_sample;
        global signal[1] = output_sample;
        
        // === VISUAL FEEDBACK ON LEDS ===
        
        // Show knob1 level (0-255 directly)
        global displayLEDs[0] = knob1;
        
        // Show knob2 as frequency indicator (scaled for LED)
        global displayLEDs[1] = cutoff_freq >> 3;    // Scale down for LED
        
        // Show knob3 steps as binary pattern
        global displayLEDs[2] = 1 << steps;          // Light up LED position
        
        // Show knob4 mix percentage
        global displayLEDs[3] = (mix_amount << 2) + 50;  // Scale for visibility
        
        yield();
    }
}
```

## How It Works

**Linear Scaling**: Multiply parameter by target range and divide by 255. Formula: `result = (param * range) / 255`

**Bit Shifting**: Fast way to scale parameters. Left shift multiplies by 2^n, right shift divides by 2^n.

**Range Mapping**: Convert 0-255 to any range using: `min + ((param * (max - min)) / 255)`

**Stepped Values**: Use right shift to create discrete parameter steps. `param >> 5` creates 8 steps.

**Parameter Control**:
- **Knob 1**: Gain level (0-2040 range)
- **Knob 2**: Cutoff frequency (200-2000 Hz)
- **Knob 3**: Processing steps (0-7 discrete levels)
- **Knob 4**: Dry/wet mix (0-100%)

## Try These Settings

```impala
// Clean signal
params[0] = 128;  // Medium gain
params[1] = 200;  // High cutoff (bright)
params[2] = 0;    // Minimum steps (clean)
params[3] = 50;   // Light mix

// Distorted sound
params[0] = 200;  // High gain
params[1] = 80;   // Low cutoff (dark)
params[2] = 200;  // High steps (distortion)
params[3] = 180;  // Heavy mix

// Subtle processing
params[0] = 100;  // Low gain
params[1] = 150;  // Medium cutoff
params[2] = 100;  // Medium steps
params[3] = 80;   // Moderate mix

// Extreme effect
params[0] = 255;  // Maximum gain
params[1] = 255;  // Maximum cutoff
params[2] = 255;  // Maximum steps
params[3] = 255;  // Full wet
```

## Understanding Parameter Reading

**Raw Values**: All knobs provide 0-255 values regardless of their physical position or labeling.

**Scaling Math**: Use multiplication and division to map 0-255 to any useful range for your algorithm.

**Bit Operations**: Right shift (>>) divides by powers of 2. Left shift (<<) multiplies by powers of 2.

**LED Feedback**: Show parameter values visually so users understand current settings.

## Try These Changes

- **Exponential scaling**: Use `(param * param) >> 8` for curves that feel more natural
- **Inverted parameters**: Use `255 - param` to reverse parameter direction
- **Quantized steps**: Create exact note frequencies or rhythm divisions
- **Parameter combinations**: Combine multiple knobs for complex control

## Related Techniques

- **[Parameter Smoothing](parameter-smoothing.md)**: Add smoothing to prevent zipper noise
- **[Parameter Mapping](../fundamentals/parameter-mapping.md)**: Advanced scaling techniques
- **[Macro Controls](macro-controls.md)**: Control multiple parameters with one knob

---
*Part of the [Permut8 Cookbook](../index.md) series*