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

// Volume control state
global int smooth_volume = 1024   // Current volume level
global int smooth_balance = 128   // Current balance setting
global int left_gain = 1024       // Left channel gain
global int right_gain = 1024      // Right channel gain

function process()
locals int volume_target, int balance_target, int smoothing_speed, int left_sample, int right_sample, int output_left, int output_right
{
    loop {
        // Read parameters
        volume_target = ((int)global params[CLOCK_FREQ_PARAM_INDEX] << 3);        // 0-255 → 0-2040
        balance_target = (int)global params[SWITCHES_PARAM_INDEX];              // 0-255 balance
        smoothing_speed = ((int)global params[OPERATOR_1_PARAM_INDEX] >> 4) + 1;  // 1-16 smoothing rate
        
        // Smooth volume changes to prevent clicks
        global smooth_volume = global smooth_volume + 
            ((volume_target - global smooth_volume) >> smoothing_speed);
        
        // Smooth balance changes
        global smooth_balance = global smooth_balance + 
            ((balance_target - global smooth_balance) >> smoothing_speed);
        
        // Calculate stereo balance gains
        if (global smooth_balance < 128) {
            // Balance towards left
            global left_gain = global smooth_volume;
            global right_gain = (global smooth_volume * global smooth_balance) >> 7;
        } else {
            // Balance towards right
            global left_gain = (global smooth_volume * (255 - global smooth_balance)) >> 7;
            global right_gain = global smooth_volume;
        }
        
        // Read input samples
        left_sample = (int)global signal[0];
        right_sample = (int)global signal[1];
        
        // Apply gain to each channel
        output_left = (left_sample * global left_gain) >> 11;
        output_right = (right_sample * global right_gain) >> 11;
        
        // Prevent clipping
        if (output_left > 2047) output_left = 2047;
        if (output_left < -2047) output_left = -2047;
        if (output_right > 2047) output_right = 2047;
        if (output_right < -2047) output_right = -2047;
        
        // Output processed signals
        global signal[0] = output_left;
        global signal[1] = output_right;
        
        // Display volume and balance on LEDs
        global displayLEDs[0] = global smooth_volume >> 3;    // Volume level
        global displayLEDs[1] = global smooth_balance;        // Balance position
        global displayLEDs[2] = global left_gain >> 3;       // Left gain
        global displayLEDs[3] = global right_gain >> 3;      // Right gain
        
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
// Unity gain, centered
global params[CLOCK_FREQ_PARAM_INDEX] = 128;  // Half volume
global params[SWITCHES_PARAM_INDEX] = 128;  // Center balance
global params[OPERATOR_1_PARAM_INDEX] = 64;   // Medium smoothing

// Left-heavy mix
global params[CLOCK_FREQ_PARAM_INDEX] = 200;  // Loud volume
global params[SWITCHES_PARAM_INDEX] = 80;   // Left balance
global params[OPERATOR_1_PARAM_INDEX] = 32;   // Slow smoothing

// Quick response
global params[CLOCK_FREQ_PARAM_INDEX] = 100;  // Moderate volume
global params[SWITCHES_PARAM_INDEX] = 150;  // Right balance
global params[OPERATOR_1_PARAM_INDEX] = 200;  // Fast smoothing

// Background level
global params[CLOCK_FREQ_PARAM_INDEX] = 40;   // Quiet volume
global params[SWITCHES_PARAM_INDEX] = 128;  // Center balance
global params[OPERATOR_1_PARAM_INDEX] = 16;   // Very slow smoothing
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