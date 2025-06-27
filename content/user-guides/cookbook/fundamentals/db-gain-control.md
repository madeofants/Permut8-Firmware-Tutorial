# dB Gain Control

*Professional logarithmic volume control*

## What This Does

Implements studio-style dB (decibel) gain control with logarithmic response that matches human hearing and professional audio equipment. Unlike linear volume knobs, dB control provides perceptually uniform volume changes where each step sounds like a consistent loudness difference.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Gain level (0-255, mapped to dB range)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Response curve (0-255, controls logarithmic shape)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Smoothing speed (0-255, controls gain change rate)

**Common dB Levels:**
- **Unity Gain**: 0dB (no level change)
- **Mixing Level**: -6dB (headroom for mixing)
- **Background**: -20dB (quiet background)
- **Very Quiet**: -40dB (whisper level)
- **Mute**: -∞dB (silence)

**Key Concepts:** Logarithmic scaling, perceptual uniformity, gain staging, professional response

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


global int current_gain = 2047
global int target_gain = 2047

function process()
locals int gain_param, int curve_param, int smooth_speed, int gain_step, int output_left, int output_right
{
    loop {

        gain_param = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];
        curve_param = (int)global (int)global params[SWITCHES_PARAM_INDEX];
        smooth_speed = ((int)global (int)global params[OPERATOR_1_PARAM_INDEX] >> 4) + 1;
        

        if (gain_param == 0) {

            global target_gain = 0;
        } else if (gain_param < 64) {

            global target_gain = (gain_param * gain_param) >> 4;
        } else if (gain_param < 192) {

            global target_gain = 256 + ((gain_param - 64) * 14);
        } else {

            global target_gain = 2047 + ((gain_param - 192) << 5);
        }
        

        if (curve_param < 128) {

            global target_gain = (global target_gain * curve_param) >> 7;
        } else {

            global target_gain = (global target_gain * global target_gain) >> 11;
        }
        

        if (global target_gain > 4095) global target_gain = 4095;
        

        if (global current_gain < global target_gain) {
            global current_gain = global current_gain + smooth_speed;
            if (global current_gain > global target_gain) global current_gain = global target_gain;
        } else if (global current_gain > global target_gain) {
            global current_gain = global current_gain - smooth_speed;
            if (global current_gain < global target_gain) global current_gain = global target_gain;
        }
        

        output_left = ((int)global signal[0] * global current_gain) >> 11;
        output_right = ((int)global signal[1] * global current_gain) >> 11;
        

        if (output_left > 2047) output_left = 2047;
        if (output_left < -2047) output_left = -2047;
        if (output_right > 2047) output_right = 2047;
        if (output_right < -2047) output_right = -2047;
        

        global signal[0] = output_left;
        global signal[1] = output_right;
        

        global displayLEDs[0] = gain_param;
        global displayLEDs[1] = global current_gain >> 4;
        global displayLEDs[2] = curve_param;
        global displayLEDs[3] = smooth_speed << 4;
        
        yield();
    }
}

```

## How It Works

**Logarithmic Response**: The gain calculation uses different curves for different ranges - quadratic for quiet sounds, linear for normal levels, and gentle boost for loud levels.

**Gain Smoothing**: Changes in gain level are smoothed over time to prevent zipper noise when adjusting the gain knob.

**Range Mapping**: The 0-255 parameter range maps to practical dB levels from silence (-∞dB) through unity gain (0dB) to moderate boost (+6dB).

**Curve Shaping**: The curve parameter adjusts the response from more linear (professional) to more exponential (musical).

**Parameter Control**:
- **Control 1**: Gain level (0 = mute, 128 = moderate, 255 = boost)
- **Control 2**: Response curve (0 = linear, 255 = exponential)
- **Control 3**: Smoothing speed (higher = faster changes)

## Try These Settings

```impala

(int)global params[CLOCK_FREQ_PARAM_INDEX] = 192;
(int)global params[SWITCHES_PARAM_INDEX] = 128;
(int)global params[OPERATOR_1_PARAM_INDEX] = 64;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 80;
(int)global params[SWITCHES_PARAM_INDEX] = 64;
(int)global params[OPERATOR_1_PARAM_INDEX] = 32;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 160;
(int)global params[SWITCHES_PARAM_INDEX] = 200;
(int)global params[OPERATOR_1_PARAM_INDEX] = 128;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;
(int)global params[SWITCHES_PARAM_INDEX] = 100;
(int)global params[OPERATOR_1_PARAM_INDEX] = 200;
```

## Understanding dB Control

**Logarithmic Nature**: dB scales match human hearing where equal dB steps sound like equal loudness changes.

**Professional Standards**: Studio equipment uses dB markings because they provide intuitive, musical control over levels.

**Gain Staging**: Multiple gain stages allow precise control over signal levels throughout the processing chain.

**Smooth Response**: Gain smoothing prevents zipper noise when adjusting levels during audio playback.

## Try These Changes

- **Multi-band gain**: Apply different gain curves to different frequency ranges
- **Stereo gain**: Independent left/right channel gain control
- **Automation**: Program gain changes that follow musical phrases
- **Limiting integration**: Combine with limiting for broadcast-safe levels

## Related Techniques

- **[Gain and Volume](gain-and-volume.md)**: Basic linear volume control
- **[Output Limiting](output-limiting.md)**: Prevent clipping with limiting

---
*Part of the [Permut8 Cookbook](../index.md) series*