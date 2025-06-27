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


global int clock
global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clockFreqLimit


global int envelope = 0
global int gain_reduction = 255

function process()
locals int threshold, int ratio, int attack, int release, int input_level, int target_gain, int output, int overage, int gain_reduction_amount, int attack_factor, int release_factor, int output_left, int output_right
{
    loop {

        threshold = ((int)global params[CLOCK_FREQ_PARAM_INDEX] << 2) + 256;
        ratio = ((int)global params[SWITCHES_PARAM_INDEX] >> 4) + 2;
        attack = ((int)global params[OPERATOR_1_PARAM_INDEX] >> 5) + 1;
        release = ((int)global params[OPERAND_1_HIGH_PARAM_INDEX] >> 5) + 1;
        

        attack_factor = attack & 7;
        release_factor = release & 7;
        

        input_level = (int)global signal[0];
        if (input_level < 0) input_level = -input_level;
        

        if (input_level > global envelope) {


            global envelope = global envelope + ((input_level - global envelope) >> attack_factor);
        } else {


            global envelope = global envelope + ((input_level - global envelope) >> release_factor);
        }
        

        if (global envelope > threshold) {

            overage = global envelope - threshold;
            


            gain_reduction_amount = overage - (overage / ratio);
            


            target_gain = 255 - ((gain_reduction_amount << 8) / overage);
            if (target_gain < 64) target_gain = 64;
        } else {
            target_gain = 255;
        }
        

        if (target_gain < global gain_reduction) {

            global gain_reduction = global gain_reduction - ((global gain_reduction - target_gain) >> attack_factor);
        } else {

            global gain_reduction = global gain_reduction + ((target_gain - global gain_reduction) >> release_factor);
        }
        

        output_left = ((int)global signal[0] * global gain_reduction) >> 8;
        output_right = ((int)global signal[1] * global gain_reduction) >> 8;
        

        if (output_left > 2047) output_left = 2047;
        if (output_left < -2047) output_left = -2047;
        if (output_right > 2047) output_right = 2047;
        if (output_right < -2047) output_right = -2047;
        

        global signal[0] = output_left;
        global signal[1] = output_right;
        

        global displayLEDs[0] = 255 - global gain_reduction;
        global displayLEDs[1] = global envelope >> 3;
        global displayLEDs[2] = threshold >> 3;
        global displayLEDs[3] = ratio << 4;
        
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
- **Control 3**: Attack (higher = slower attack response, 1-8 speed range)
- **Control 4**: Release (higher = slower release response, 1-8 speed range)

**LED Feedback**: Shows gain reduction, input level, threshold setting, and compression ratio.

## Try These Settings

```impala

global params[CLOCK_FREQ_PARAM_INDEX] = 180;
global params[SWITCHES_PARAM_INDEX] = 64;
global params[OPERATOR_1_PARAM_INDEX] = 32;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 128;


global params[CLOCK_FREQ_PARAM_INDEX] = 120;
global params[SWITCHES_PARAM_INDEX] = 96;
global params[OPERATOR_1_PARAM_INDEX] = 8;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 64;
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