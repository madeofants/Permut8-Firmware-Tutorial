# Parameter Smoothing

*Eliminate zipper noise and audio artifacts when parameters change rapidly*

## What This Does

Parameter smoothing prevents zipper noise by gradually transitioning between parameter values instead of jumping instantly. Essential for professional-quality firmware with smooth, musical parameter changes.

## Quick Reference

**Essential Parameters:**
- `params[0-7]`: Input parameters (0-255)
- `smoothing_rate`: How fast parameters change (1-16)
- `current_param`: Smoothed parameter value
- `target_param`: Destination parameter value

**Core Techniques:**
- **Exponential smoothing**: Gradual approach to target values
- **Time constants**: Control how fast parameters respond
- **Snap-to-target**: Prevent endless tiny steps
- **Per-parameter control**: Different smoothing for each knob

**Key Concepts:** Zipper noise elimination, exponential decay, parameter interpolation, smooth transitions

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
global array signal[2]          // Left/Right audio samples
global array params[PARAM_COUNT]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Parameter smoothing state
global int smooth_cutoff = 1000    // Smoothed cutoff frequency
global int smooth_resonance = 512  // Smoothed resonance
global int smooth_volume = 1024    // Smoothed volume level
global int smooth_rate = 4         // Smoothing speed (1-16)

function process()
locals int cutoff_target, int resonance_target, int volume_target, int input_sample, int filtered_sample, int output_sample
{
    loop {
        // Read target parameters from knobs
        cutoff_target = 200 + (((int)global (int)global params[CLOCK_FREQ_PARAM_INDEX] * 1800) >> 8);   // 200-2000 Hz range
        resonance_target = 256 + (((int)global (int)global params[SWITCHES_PARAM_INDEX] * 1280) >> 8); // 256-1536 range
        volume_target = ((int)global (int)global params[OPERATOR_1_PARAM_INDEX] << 3);                   // 0-2040 range
        global smooth_rate = ((int)global (int)global params[OPERAND_1_HIGH_PARAM_INDEX] >> 4) + 1;         // 1-16 rate
        
        // Smooth cutoff frequency to prevent zipper noise
        global smooth_cutoff = global smooth_cutoff + 
            ((cutoff_target - global smooth_cutoff) >> global smooth_rate);
        
        // Smooth resonance parameter
        global smooth_resonance = global smooth_resonance + 
            ((resonance_target - global smooth_resonance) >> global smooth_rate);
        
        // Smooth volume parameter  
        global smooth_volume = global smooth_volume + 
            ((volume_target - global smooth_volume) >> global smooth_rate);
        
        // Snap to target if very close (prevents endless tiny steps)
        if (cutoff_target - global smooth_cutoff < 4 && 
            cutoff_target - global smooth_cutoff > -4) {
            global smooth_cutoff = cutoff_target;
        }
        
        if (resonance_target - global smooth_resonance < 4 && 
            resonance_target - global smooth_resonance > -4) {
            global smooth_resonance = resonance_target;
        }
        
        if (volume_target - global smooth_volume < 4 && 
            volume_target - global smooth_volume > -4) {
            global smooth_volume = volume_target;
        }
        
        // Read input sample
        input_sample = (int)global signal[0];
        
        // Apply simple low-pass filter using smoothed parameters
        filtered_sample = global smooth_cutoff + 
            (((input_sample - global smooth_cutoff) * global smooth_resonance) >> 11);
        
        // Limit filter output
        if (filtered_sample > 2047) filtered_sample = 2047;
        if (filtered_sample < -2047) filtered_sample = -2047;
        
        // Apply smoothed volume
        output_sample = (filtered_sample * global smooth_volume) >> 11;
        
        // Prevent clipping
        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        
        // Output processed signal
        global signal[0] = output_sample;
        global signal[1] = output_sample;
        
        // Display smoothed parameter values on LEDs
        global displayLEDs[0] = global smooth_cutoff >> 3;     // Cutoff level
        global displayLEDs[1] = global smooth_resonance >> 3;  // Resonance level
        global displayLEDs[2] = global smooth_volume >> 3;     // Volume level
        global displayLEDs[3] = global smooth_rate << 4;       // Smoothing rate
        
        yield();
    }
}

```

## How It Works

**Exponential Smoothing**: Uses formula `current = current + ((target - current) >> rate)` for gradual parameter changes.

**Smoothing Rate**: Higher values = faster response, lower values = slower, smoother changes. Rate of 1 = very slow, 16 = very fast.

**Snap-to-Target**: When parameters get very close to target, snap exactly to prevent endless tiny adjustments.

**Parameter Scaling**: Maps 0-255 knob values to useful ranges (frequency, resonance, volume) before smoothing.

**Parameter Control**:
- **Knob 1**: Filter cutoff frequency (200-2000 Hz)
- **Knob 2**: Filter resonance (256-1536 range)
- **Knob 3**: Output volume (0-2040 range)
- **Knob 4**: Smoothing speed (1-16 rate)

## Try These Settings

```impala
// Fast, responsive controls
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 128;  // Medium cutoff
(int)global params[SWITCHES_PARAM_INDEX] = 100;  // Light resonance
(int)global params[OPERATOR_1_PARAM_INDEX] = 150;  // Medium volume
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;  // Fast smoothing

// Slow, ambient changes
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 80;   // Lower cutoff
(int)global params[SWITCHES_PARAM_INDEX] = 150;  // More resonance
(int)global params[OPERATOR_1_PARAM_INDEX] = 120;  // Moderate volume
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 32;   // Very slow smoothing

// Musical transitions
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;  // Higher cutoff
(int)global params[SWITCHES_PARAM_INDEX] = 80;   // Low resonance
(int)global params[OPERATOR_1_PARAM_INDEX] = 180;  // Louder volume
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 100;  // Medium smoothing

// Instant changes (no smoothing)
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 255;  // Maximum cutoff
(int)global params[SWITCHES_PARAM_INDEX] = 200;  // High resonance
(int)global params[OPERATOR_1_PARAM_INDEX] = 255;  // Full volume
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 255;  // Maximum rate (instant)
```

## Understanding Parameter Smoothing

**Exponential Decay**: Each step closes a fraction of the distance to target. Creates natural-feeling parameter motion.

**Time Constants**: Smaller smoothing rates create longer time constants (slower changes). Larger rates = shorter time constants (faster changes).

**Zipper Noise**: Occurs when parameters change too quickly, creating audible stepping artifacts. Smoothing eliminates this.

**Musical Response**: Good smoothing feels natural and musical, not robotic or jerky.

## Try These Changes

- **Per-parameter rates**: Different smoothing speeds for different controls
- **Adaptive smoothing**: Faster smoothing for large changes, slower for small adjustments
- **Curve shaping**: Non-linear parameter mapping before smoothing
- **Tempo sync**: Sync parameter changes to musical timing

## Related Techniques

- **[Parameter Mapping](../fundamentals/parameter-mapping.md)**: Map parameters to useful ranges before smoothing
- **[Read Knobs](read-knobs.md)**: Basic parameter reading techniques
- **[Macro Controls](macro-controls.md)**: Control multiple parameters with smoothing

---
*Part of the [Permut8 Cookbook](../index.md) series*