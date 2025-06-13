# Basic Compressor

*Create dynamic range control with automatic level adjustment*

## What This Does

Automatically reduces the volume of loud signals while leaving quieter signals unchanged, creating more consistent levels. Essential for controlling dynamics in vocals, drums, and mix buses.

## Quick Reference

**Essential Parameters:**
- `params[0]`: Threshold (0-255, level where compression starts)
- `params[1]`: Ratio (0-255, amount of compression)
- `params[2]`: Attack (0-255, how fast compression engages)
- `params[3]`: Release (0-255, how fast compression disengages)

**Key Concepts:** Envelope following, threshold detection, gain reduction, attack/release timing

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Simple compressor state
global int envelope = 0         // Current envelope level
global int gain_reduction = 255 // Current gain reduction (255=no reduction, 0=max reduction)

function process()
locals int threshold
locals int ratio
locals int attack
locals int release
locals int input_level
locals int target_gain
locals int output
locals int overage
locals int gain_reduction_amount
locals int attack_factor
locals int release_factor
{
    loop {
        // Read parameters
        threshold = ((int)global params[0] << 2) + 256;   // 256-1276 range (within audio range)
        ratio = ((int)global params[1] >> 4) + 2;         // 2-17 ratio (reasonable compression range)
        attack = ((int)global params[2] >> 5) + 1;        // 1-8 attack speed
        release = ((int)global params[3] >> 5) + 1;       // 1-8 release speed
        
        // Convert to proper envelope factors
        attack_factor = attack & 7;                       // Limit to 0-7 for reasonable response
        release_factor = release & 7;                     // Limit to 0-7 for reasonable response
        
        // Get input level (absolute value of left channel)
        input_level = (int)global signal[0];
        if (input_level < 0) input_level = -input_level;
        
        // Simple envelope follower with corrected attack/release behavior
        if (input_level > global envelope) {
            // Attack phase - follow rising signals (lower values = faster attack)
            global envelope = global envelope + ((input_level - global envelope) >> attack_factor);
        } else {
            // Release phase - follow falling signals (lower values = faster release)
            global envelope = global envelope + ((input_level - global envelope) >> release_factor);
        }
        
        // Calculate gain reduction if above threshold
        if (global envelope > threshold) {
            // Calculate how much signal exceeds threshold
            overage = global envelope - threshold;
            
            // Apply compression ratio using proper division approximation
            // For ratio N:1, reduce overage by factor of N
            gain_reduction_amount = overage - (overage / ratio);
            
            // Calculate target gain (255=no reduction, lower=more reduction)
            // Scale gain_reduction_amount to 0-255 range
            target_gain = 255 - ((gain_reduction_amount << 8) / overage);
            if (target_gain < 64) target_gain = 64;  // Limit maximum compression (75% max reduction)
        } else {
            target_gain = 255;  // No compression below threshold
        }
        
        // Smooth gain changes with corrected attack/release logic
        if (target_gain < global gain_reduction) {
            // Increasing compression (gain reduction) - use attack time
            global gain_reduction = global gain_reduction - ((global gain_reduction - target_gain) >> attack_factor);
        } else {
            // Decreasing compression (gain recovery) - use release time  
            global gain_reduction = global gain_reduction + ((target_gain - global gain_reduction) >> release_factor);
        }
        
        // Apply compression to both channels
        int output_left = ((int)global signal[0] * global gain_reduction) >> 8;
        int output_right = ((int)global signal[1] * global gain_reduction) >> 8;
        
        // Prevent clipping
        if (output_left > 2047) output_left = 2047;
        if (output_left < -2047) output_left = -2047;
        if (output_right > 2047) output_right = 2047;
        if (output_right < -2047) output_right = -2047;
        
        // Output compressed audio (stereo processing)
        global signal[0] = output_left;
        global signal[1] = output_right;
        
        // Show compression activity on LEDs
        global displayLEDs[0] = 255 - global gain_reduction;  // Gain reduction meter
        global displayLEDs[1] = global envelope >> 3;         // Input level meter
        global displayLEDs[2] = threshold >> 3;               // Threshold level
        global displayLEDs[3] = ratio << 4;                   // Compression ratio
        
        yield();
    }
}
```

## How It Works

**Envelope Following**: Tracks the input signal level using separate attack and release times.

**Threshold Detection**: When the envelope exceeds the threshold, compression is applied.

**Ratio Control**: Determines how much compression is applied to signals above the threshold.

**Parameter Control**:
- **Knob 1**: Threshold (higher = less compression)
- **Knob 2**: Ratio (higher = more compression, 2:1 to 17:1 range)  
- **Knob 3**: Attack (higher = slower attack, 1-8 speed range)
- **Knob 4**: Release (higher = slower release, 1-8 speed range)

**LED Feedback**: Shows gain reduction, input level, threshold setting, and compression ratio.

## Try These Settings

```impala
// Gentle vocal compression
params[0] = 180;  // High threshold
params[1] = 64;   // 8:1 ratio
params[2] = 32;   // Medium attack
params[3] = 128;  // Slow release

// Drum compression
params[0] = 120;  // Lower threshold
params[1] = 96;   // 12:1 ratio  
params[2] = 8;    // Fast attack
params[3] = 64;   // Medium release
```

## Try These Changes

- **Stereo compression**: Process left and right channels separately
- **Makeup gain**: Add parameter to boost output level after compression
- **Soft knee**: Gradually apply compression around the threshold
- **Limiter mode**: Set very high ratio for peak limiting

## Related Techniques

- **[Gain and Volume](../fundamentals/gain-and-volume.md)**: Basic level control
- **[Envelope Basics](../fundamentals/envelope-basics.md)**: Envelope following fundamentals

---
*Part of the [Permut8 Cookbook](../index.md) series*