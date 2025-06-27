# Gain and Volume Control

*Essential volume control for clean, professional audio output*

## What This Does

Gain and volume control scales audio levels with smooth parameter changes to prevent clicks. This is fundamental for all audio processing - controlling output levels and ensuring clean signal flow.

## Quick Reference

**Essential Parameters:**
- `params[CLOCK_FREQ_PARAM_INDEX]`: Master volume (0-255)
- `params[SWITCHES_PARAM_INDEX]`: Stereo balance (0-255, 128=center)
- `params[OPERATOR_1_PARAM_INDEX]`: Smoothing speed (0-255)

**Core Techniques:**
- **Volume scaling**: Multiply samples by gain factor
- **Parameter smoothing**: Gradual changes prevent clicks
- **Stereo balance**: Independent left/right control
- **LED feedback**: Visual level indication

**Key Concepts:** Linear gain, parameter smoothing, stereo balance, level indication

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


global int smooth_volume = 1024
global int smooth_balance = 128
global int left_gain = 1024
global int right_gain = 1024

function process()
locals int volume_target, int balance_target, int smoothing_speed, int left_sample, int right_sample, int output_left, int output_right
{
    loop {

        volume_target = ((int)global params[CLOCK_FREQ_PARAM_INDEX] << 3);
        balance_target = (int)global params[SWITCHES_PARAM_INDEX];
        smoothing_speed = ((int)global params[OPERATOR_1_PARAM_INDEX] >> 4) + 1;
        

        global smooth_volume = global smooth_volume + 
            ((volume_target - global smooth_volume) >> smoothing_speed);
        

        global smooth_balance = global smooth_balance + 
            ((balance_target - global smooth_balance) >> smoothing_speed);
        

        if (global smooth_balance < 128) {

            global left_gain = global smooth_volume;
            global right_gain = (global smooth_volume * global smooth_balance) >> 7;
        } else {

            global left_gain = (global smooth_volume * (255 - global smooth_balance)) >> 7;
            global right_gain = global smooth_volume;
        }
        

        left_sample = (int)global signal[0];
        right_sample = (int)global signal[1];
        

        output_left = (left_sample * global left_gain) >> 11;
        output_right = (right_sample * global right_gain) >> 11;
        

        if (output_left > 2047) output_left = 2047;
        if (output_left < -2047) output_left = -2047;
        if (output_right > 2047) output_right = 2047;
        if (output_right < -2047) output_right = -2047;
        

        global signal[0] = output_left;
        global signal[1] = output_right;
        

        global displayLEDs[0] = global smooth_volume >> 3;
        global displayLEDs[1] = global smooth_balance;
        global displayLEDs[2] = global left_gain >> 3;
        global displayLEDs[3] = global right_gain >> 3;
        
        yield();
    }
}
```

## How It Works

**Volume Scaling**: Multiplies audio samples by gain factor. Using right-shift (>>11) instead of division for efficiency.

**Parameter Smoothing**: Gradual changes prevent clicks when adjusting controls. Higher smoothing values = faster response.

**Stereo Balance**: Left/right channels get independent gain levels based on balance position. Center (128) = equal levels.

**LED Display**: Shows current volume, balance position, and individual channel gains for visual feedback.

**Parameter Control**:
- **Control 1**: Master volume (0-255 → 0-2040 range)
- **Control 2**: Stereo balance (0-255, 128=center)
- **Control 3**: Smoothing speed (0-255 → 1-16 rate)

## Try These Settings

```impala

global params[CLOCK_FREQ_PARAM_INDEX] = 128;
global params[SWITCHES_PARAM_INDEX] = 128;
global params[OPERATOR_1_PARAM_INDEX] = 64;


global params[CLOCK_FREQ_PARAM_INDEX] = 200;
global params[SWITCHES_PARAM_INDEX] = 80;
global params[OPERATOR_1_PARAM_INDEX] = 32;


global params[CLOCK_FREQ_PARAM_INDEX] = 100;
global params[SWITCHES_PARAM_INDEX] = 150;
global params[OPERATOR_1_PARAM_INDEX] = 200;


global params[CLOCK_FREQ_PARAM_INDEX] = 40;
global params[SWITCHES_PARAM_INDEX] = 128;
global params[OPERATOR_1_PARAM_INDEX] = 16;
```

## Understanding Volume Control

**Linear vs Exponential**: Linear gain feels technical and precise. For musical response, try squaring the parameter value.

**Smoothing Trade-offs**: Fast smoothing responds quickly but may sound rough. Slow smoothing is smooth but sluggish.

**Balance Laws**: Simple balance reduces one channel as you move away from center. Equal-power balance maintains constant loudness.

**Gain Staging**: Keep levels reasonable to prevent clipping. Use limiting or compression for louder signals.

## Try These Changes

- **Exponential volume**: Square parameter values for more natural response
- **Mute function**: Add instant mute with dedicated parameter
- **Mono sum**: Add mono output mode for compatibility
- **Gain reduction display**: Show how much gain is being applied

## Related Techniques

- **[Parameter Mapping](#parameter-mapping)**: Advanced parameter curve shaping
- **[dB Gain Control](#db-gain-control)**: Professional decibel-based volume
- **[Output Limiting](#output-limiting)**: Prevent clipping with limiting

---
*Part of the [Permut8 Cookbook](#permut8-cookbook) series*