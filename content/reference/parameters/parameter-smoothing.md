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


const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT



extern native yield


global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]


global int smooth_cutoff = 1000
global int smooth_resonance = 512
global int smooth_volume = 1024
global int smooth_rate = 4

function process()
locals int cutoff_target, int resonance_target, int volume_target, int input_sample, int filtered_sample, int output_sample
{
    loop {

        cutoff_target = 200 + (((int)global (int)global params[CLOCK_FREQ_PARAM_INDEX] * 1800) >> 8);
        resonance_target = 256 + (((int)global (int)global params[SWITCHES_PARAM_INDEX] * 1280) >> 8);
        volume_target = ((int)global (int)global params[OPERATOR_1_PARAM_INDEX] << 3);
        global smooth_rate = ((int)global (int)global params[OPERAND_1_HIGH_PARAM_INDEX] >> 4) + 1;
        

        global smooth_cutoff = global smooth_cutoff + 
            ((cutoff_target - global smooth_cutoff) >> global smooth_rate);
        

        global smooth_resonance = global smooth_resonance + 
            ((resonance_target - global smooth_resonance) >> global smooth_rate);
        

        global smooth_volume = global smooth_volume + 
            ((volume_target - global smooth_volume) >> global smooth_rate);
        

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
        

        input_sample = (int)global signal[0];
        

        filtered_sample = global smooth_cutoff + 
            (((input_sample - global smooth_cutoff) * global smooth_resonance) >> 11);
        

        if (filtered_sample > 2047) filtered_sample = 2047;
        if (filtered_sample < -2047) filtered_sample = -2047;
        

        output_sample = (filtered_sample * global smooth_volume) >> 11;
        

        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        

        global signal[0] = output_sample;
        global signal[1] = output_sample;
        

        global displayLEDs[0] = global smooth_cutoff >> 3;
        global displayLEDs[1] = global smooth_resonance >> 3;
        global displayLEDs[2] = global smooth_volume >> 3;
        global displayLEDs[3] = global smooth_rate << 4;
        
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

(int)global params[CLOCK_FREQ_PARAM_INDEX] = 128;
(int)global params[SWITCHES_PARAM_INDEX] = 100;
(int)global params[OPERATOR_1_PARAM_INDEX] = 150;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 80;
(int)global params[SWITCHES_PARAM_INDEX] = 150;
(int)global params[OPERATOR_1_PARAM_INDEX] = 120;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 32;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;
(int)global params[SWITCHES_PARAM_INDEX] = 80;
(int)global params[OPERATOR_1_PARAM_INDEX] = 180;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 100;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 255;
(int)global params[SWITCHES_PARAM_INDEX] = 200;
(int)global params[OPERATOR_1_PARAM_INDEX] = 255;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 255;
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