# Basic Compressor

*Create dynamic range control with automatic level adjustment*

## What This Does

Automatically reduces the volume of loud signals while leaving quieter signals unchanged, creating more consistent levels. Essential for controlling dynamics in vocals, drums, and mix buses.

## Quick Reference

**Essential Parameters:**
- `params[CLOCK_FREQ_PARAM_INDEX]`: Threshold (0-255, level where compression starts)
- `params[SWITCHES_PARAM_INDEX]`: Ratio (0-255, amount of compression)
- `params[OPERATOR_1_PARAM_INDEX]`: Attack (0-255, how fast compression engages)
- `params[OPERAND_1_HIGH_PARAM_INDEX]`: Release (0-255, how fast compression disengages)

**Key Concepts:** Envelope following, threshold detection, gain reduction, attack/release timing

## Complete Code

```impala
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

// Simple compressor state
global int envelope = 0         // Current envelope level
global int gain_reduction = 255 // Current gain reduction (255=no reduction, 0=max reduction)

function process()
locals int threshold, int ratio, int attack, int release, int input_level, int target_gain, int output, int overage, int gain_reduction_amount, int attack_factor, int release_factor, int output_left, int output_right
{
    loop {
        // Read parameters
        threshold = ((int)global params[CLOCK_FREQ_PARAM_INDEX] << 2) + 256;   // 256-1276 range (within audio range)
        ratio = ((int)global params[SWITCHES_PARAM_INDEX] >> 4) + 2;         // 2-17 ratio (reasonable compression range)
        attack = ((int)global params[OPERATOR_1_PARAM_INDEX] >> 5) + 1;        // 1-8 attack speed
        release = ((int)global params[OPERAND_1_HIGH_PARAM_INDEX] >> 5) + 1;       // 1-8 release speed
        
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
        output_left = ((int)global signal[0] * global gain_reduction) >> 8;
        output_right = ((int)global signal[1] * global gain_reduction) >> 8;
        
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
- **Control 1**: Threshold (higher = less compression)
- **Control 2**: Ratio (higher = more compression, 2:1 to 17:1 range)  
- **Control 3**: Attack (higher = slower attack, 1-8 speed range)
- **Control 4**: Release (higher = slower release, 1-8 speed range)

**LED Feedback**: Shows gain reduction, input level, threshold setting, and compression ratio.

## Try These Settings

```impala
// Gentle vocal compression
global params[CLOCK_FREQ_PARAM_INDEX] = 180;  // High threshold
global params[SWITCHES_PARAM_INDEX] = 64;   // 8:1 ratio
global params[OPERATOR_1_PARAM_INDEX] = 32;   // Medium attack
global params[OPERAND_1_HIGH_PARAM_INDEX] = 128;  // Slow release

// Drum compression
global params[CLOCK_FREQ_PARAM_INDEX] = 120;  // Lower threshold
global params[SWITCHES_PARAM_INDEX] = 96;   // 12:1 ratio  
global params[OPERATOR_1_PARAM_INDEX] = 8;    // Fast attack
global params[OPERAND_1_HIGH_PARAM_INDEX] = 64;   // Medium release
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