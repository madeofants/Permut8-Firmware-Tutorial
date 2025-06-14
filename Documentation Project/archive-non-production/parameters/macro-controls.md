# Macro Controls

*Control multiple parameters simultaneously with single knobs for expressive musical performance*

## What This Does

Allows a single knob to control multiple parameters with custom relationships. Transforms technical parameter adjustments into intuitive musical gestures like "brightness," "drive," and "space."

## Quick Reference

**Essential Parameters:**
- `params[0]`: Brightness macro (filter + tone)
- `params[1]`: Drive macro (distortion + gain)
- `params[2]`: Space macro (reverb + delay)
- `params[3]`: Energy macro (levels + speed)

**Core Techniques:**
- **Multi-parameter mapping**: One knob controls several values
- **Curve shaping**: Linear, exponential, inverted responses
- **Musical gestures**: Intuitive control groupings
- **Parameter relationships**: Complementary parameter changes

**Key Concepts:** Macro mapping, parameter curves, musical intuition, expressive control

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Macro control state
global int brightness_level = 128    // Brightness macro value
global int drive_level = 0           // Drive macro value
global int space_level = 0           // Space macro value
global int energy_level = 128        // Energy macro value

function process()
locals int brightness_macro, int drive_macro, int space_macro, int energy_macro, int filter_cutoff, int filter_resonance, int distortion_gain, int reverb_mix, int energy_level, int input_sample, int filtered_sample, int driven_sample, int spatial_sample, int output_sample
{
    loop {
        // Read macro control knobs
        brightness_macro = (int)global params[0];   // 0-255 brightness
        drive_macro = (int)global params[1];        // 0-255 drive
        space_macro = (int)global params[2];        // 0-255 space
        energy_macro = (int)global params[3];       // 0-255 energy
        
        // === BRIGHTNESS MACRO (Filter + Tone) ===
        // Controls filter cutoff, resonance, and tone shaping
        filter_cutoff = 200 + ((brightness_macro * 1800) >> 8);    // 200-2000 Hz
        filter_resonance = 256 + ((brightness_macro * 1024) >> 8); // 256-1280 range
        
        // === DRIVE MACRO (Distortion + Gain) ===
        // Controls pre-gain, distortion amount, and post-compensation
        // Exponential curve for natural distortion feel
        distortion_gain = (drive_macro * drive_macro) >> 8;         // Quadratic curve
        if (distortion_gain < 128) distortion_gain = 128;          // Minimum unity gain
        
        // === SPACE MACRO (Reverb + Delay) ===
        // Controls wet signal amount and spatial effects
        reverb_mix = (space_macro * 180) >> 8;                      // 0-180 mix level
        
        // === ENERGY MACRO (Levels + Dynamics) ===
        // Controls overall energy and dynamics
        energy_level = 512 + ((energy_macro * 1536) >> 8);         // 512-2048 range
        
        // === AUDIO PROCESSING ===
        
        // Read input sample
        input_sample = (int)global signal[0];
        
        // Apply brightness (simple filter)
        filtered_sample = filter_cutoff + 
            (((input_sample - filter_cutoff) * filter_resonance) >> 11);
        
        // Limit filter output
        if (filtered_sample > 2047) filtered_sample = 2047;
        if (filtered_sample < -2047) filtered_sample = -2047;
        
        // Apply drive (soft saturation)
        driven_sample = (filtered_sample * distortion_gain) >> 8;
        if (driven_sample > 1536) {
            driven_sample = 1536 + ((driven_sample - 1536) >> 2); // Soft limiting
        }
        if (driven_sample < -1536) {
            driven_sample = -1536 + ((driven_sample + 1536) >> 2);
        }
        
        // Apply space (simple reverb simulation)
        spatial_sample = driven_sample + 
            (((driven_sample >> 2) * reverb_mix) >> 8);        // Add delayed/reverb signal
        
        // Apply energy (final level control)
        output_sample = (spatial_sample * energy_level) >> 10;
        
        // Prevent clipping
        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        
        // Output processed signal
        global signal[0] = output_sample;
        global signal[1] = output_sample;
        
        // Display macro levels on LEDs
        global displayLEDs[0] = brightness_macro;       // Brightness level
        global displayLEDs[1] = drive_macro;            // Drive level
        global displayLEDs[2] = space_macro;            // Space level
        global displayLEDs[3] = energy_macro;           // Energy level
        
        yield();
    }
}
```

## How It Works

**Brightness Macro**: Controls filter cutoff and resonance together. Higher values = brighter, more resonant sound.

**Drive Macro**: Uses exponential curve for natural distortion feel. Controls pre-gain and soft limiting together.

**Space Macro**: Controls reverb/delay mix amount. Creates sense of acoustic space and depth.

**Energy Macro**: Final level and dynamics control. Sets overall energy and impact of the sound.

**Parameter Control**:
- **Knob 1**: Brightness (filter cutoff + resonance)
- **Knob 2**: Drive (distortion gain + saturation) 
- **Knob 3**: Space (reverb mix + spatial effects)
- **Knob 4**: Energy (levels + dynamics)

## Try These Settings

```impala
// Clean, bright sound
params[0] = 200;  // High brightness
params[1] = 64;   // Light drive
params[2] = 80;   // Moderate space
params[3] = 150;  // Good energy

// Dark, driven sound
params[0] = 80;   // Low brightness
params[1] = 180;  // Heavy drive
params[2] = 120;  // More space
params[3] = 200;  // High energy

// Ambient, spacious
params[0] = 120;  // Medium brightness
params[1] = 100;  // Medium drive
params[2] = 200;  // Lots of space
params[3] = 100;  // Moderate energy

// Aggressive, punchy
params[0] = 255;  // Maximum brightness
params[1] = 255;  // Maximum drive
params[2] = 50;   // Dry signal
params[3] = 255;  // Maximum energy
```

## Understanding Macro Controls

**Musical Intuition**: Group related parameters so users think musically, not technically.

**Parameter Curves**: Linear curves feel technical. Exponential/logarithmic curves feel more natural.

**Complementary Controls**: Some parameters should increase while others decrease for musical balance.

**Performance Oriented**: Design macros for real-time performance and expression.

## Try These Changes

- **Custom curves**: Add S-curves, inverted responses, or stepped mappings
- **Bipolar controls**: Center position = neutral, extremes = opposite effects
- **Cross-parameter coupling**: One macro affects the response of another
- **Tempo-synced macros**: Sync parameter changes to musical timing

## Related Techniques

- **[Parameter Smoothing](parameter-smoothing.md)**: Add smoothing to macro controls
- **[Read Knobs](read-knobs.md)**: Basic parameter reading for macro inputs
- **[Parameter Mapping](../fundamentals/parameter-mapping.md)**: Advanced parameter scaling

---
*Part of the [Permut8 Cookbook](../index.md) series*