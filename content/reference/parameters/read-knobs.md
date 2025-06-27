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

function process()
locals int knob1, int knob2, int knob3, int knob4, int gain_level, int cutoff_freq, int steps, int mix_amount, int input_sample, int processed_sample, int output_sample
{
    loop {

        knob1 = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];
        knob2 = (int)global (int)global params[SWITCHES_PARAM_INDEX];
        knob3 = (int)global (int)global params[OPERATOR_1_PARAM_INDEX];
        knob4 = (int)global (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
        

        

        gain_level = (knob1 << 3);
        

        cutoff_freq = 200 + ((knob2 * 1800) >> 8);
        

        steps = knob3 >> 5;
        

        mix_amount = (knob4 * 100) >> 8;
        

        

        input_sample = (int)global signal[0];
        

        processed_sample = (input_sample * gain_level) >> 11;
        

        if (cutoff_freq > 1000) {

            processed_sample = processed_sample + (processed_sample >> 3);
        } else {

            processed_sample = processed_sample - (processed_sample >> 3);
        }
        

        if (steps > 4) {

            if (processed_sample > 1024) processed_sample = 1024;
            if (processed_sample < -1024) processed_sample = -1024;
        }
        

        output_sample = ((input_sample * (100 - mix_amount)) + 
                        (processed_sample * mix_amount)) / 100;
        

        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        

        global signal[0] = output_sample;
        global signal[1] = output_sample;
        

        

        global displayLEDs[0] = knob1;
        

        global displayLEDs[1] = cutoff_freq >> 3;
        

        global displayLEDs[2] = 1 << steps;
        

        global displayLEDs[3] = (mix_amount << 2) + 50;
        
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

(int)global params[CLOCK_FREQ_PARAM_INDEX] = 128;
(int)global params[SWITCHES_PARAM_INDEX] = 200;
(int)global params[OPERATOR_1_PARAM_INDEX] = 0;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 50;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;
(int)global params[SWITCHES_PARAM_INDEX] = 80;
(int)global params[OPERATOR_1_PARAM_INDEX] = 200;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 180;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 100;
(int)global params[SWITCHES_PARAM_INDEX] = 150;
(int)global params[OPERATOR_1_PARAM_INDEX] = 100;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 80;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 255;
(int)global params[SWITCHES_PARAM_INDEX] = 255;
(int)global params[OPERATOR_1_PARAM_INDEX] = 255;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 255;
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