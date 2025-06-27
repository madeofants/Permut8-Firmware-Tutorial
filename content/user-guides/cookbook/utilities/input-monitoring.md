# Input Monitoring

*Detect signal levels, peaks, and presence for responsive patch behavior*

## What This Does

Provides real-time monitoring of input signals for level detection, peak measurement, and signal presence detection. Essential for creating responsive patches that adapt to incoming signals, visual feedback, and triggering events based on audio thresholds.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Presence threshold (0-255)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Release time (0-255)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Peak hold time (0-255)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Monitoring mode (0-255)

**Core Techniques:**
- **Peak detection**: Track maximum instantaneous levels
- **RMS measurement**: Average signal energy over time
- **Threshold detection**: Binary signal presence decisions
- **Envelope following**: Smooth level tracking

**Key Concepts:** Peak vs RMS, threshold hysteresis, signal presence, visual feedback

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


global int peak_level = 0
global int rms_accumulator = 0
global int rms_level = 0
global int peak_hold_counter = 0
global int signal_present = 0
global int previous_sample = 0

function process()
locals input_sample, abs_input, presence_threshold, release_time, peak_hold_time, monitor_mode, sample_squared, peak_hold_samples, release_amount, rms_smooth
{
    loop {

        input_sample = signal[0];
        

        presence_threshold = params[CLOCK_FREQ_PARAM_INDEX];
        release_time = (params[SWITCHES_PARAM_INDEX] >> 4) + 1;
        peak_hold_time = (params[OPERATOR_1_PARAM_INDEX] << 4) + 512;
        monitor_mode = params[OPERAND_1_HIGH_PARAM_INDEX];
        

        if (input_sample < 0) {
            abs_input = -input_sample;
        } else {
            abs_input = input_sample;
        }
        

        if (abs_input > global peak_level) {

            global peak_level = abs_input;
            global peak_hold_counter = peak_hold_time;
        } else {

            if (global peak_hold_counter > 0) {
                global peak_hold_counter = global peak_hold_counter - 1;
            } else {

                release_amount = global peak_level >> release_time;
                if (release_amount < 1) release_amount = 1;
                global peak_level = global peak_level - release_amount;
                if (global peak_level < 0) global peak_level = 0;
            }
        }
        

        sample_squared = (input_sample >> 3) * (input_sample >> 3);
        global rms_accumulator = global rms_accumulator - (global rms_accumulator >> 8);
        global rms_accumulator = global rms_accumulator + sample_squared;
        

        rms_smooth = global rms_accumulator >> 4;
        if (rms_smooth > 1024) {
            global rms_level = 32 + (rms_smooth >> 5);
        } else if (rms_smooth > 256) {
            global rms_level = 16 + (rms_smooth >> 4);
        } else if (rms_smooth > 64) {
            global rms_level = 8 + (rms_smooth >> 3);
        } else {
            global rms_level = rms_smooth >> 2;
        }
        

        if (monitor_mode < 128) {

            if (global peak_level > presence_threshold) {
                global signal_present = 1;
            } else {
                global signal_present = 0;
            }
        } else {

            if (global rms_level > (presence_threshold >> 2)) {
                global signal_present = 1;
            } else {
                global signal_present = 0;
            }
        }
        

        global signal[0] = input_sample;
        global signal[1] = input_sample;
        

        global displayLEDs[0] = global peak_level >> 3;
        global displayLEDs[1] = global rms_level << 2;
        if (global signal_present == 1) {
            global displayLEDs[2] = 255;
        } else {
            global displayLEDs[2] = 32;
        }
        global displayLEDs[3] = presence_threshold;
        
        yield();
    }
}

```

## How It Works

**Peak Detection**: Tracks maximum instantaneous levels with fast attack and controlled release. Peak hold maintains the maximum for visual feedback.

**RMS Approximation**: Estimates average signal energy using a sliding window approach. More stable than peak detection and correlates better with perceived loudness.

**Signal Presence**: Binary detection using either peak or RMS levels compared to threshold. Prevents false triggering from noise.

**Parameter Control**:
- **Knob 1**: Presence threshold (sensitivity)
- **Knob 2**: Release time (how fast peaks decay)
- **Knob 3**: Peak hold time (how long peaks are held)
- **Knob 4**: Monitor mode (peak vs RMS presence detection)

## Try These Settings

```impala

params[CLOCK_FREQ_PARAM_INDEX] = 64;
params[SWITCHES_PARAM_INDEX] = 32;
params[OPERATOR_1_PARAM_INDEX] = 200;
params[OPERAND_1_HIGH_PARAM_INDEX] = 64;


params[CLOCK_FREQ_PARAM_INDEX] = 128;
params[SWITCHES_PARAM_INDEX] = 80;
params[OPERATOR_1_PARAM_INDEX] = 100;
params[OPERAND_1_HIGH_PARAM_INDEX] = 200;


params[CLOCK_FREQ_PARAM_INDEX] = 100;
params[SWITCHES_PARAM_INDEX] = 200;
params[OPERATOR_1_PARAM_INDEX] = 50;
params[OPERAND_1_HIGH_PARAM_INDEX] = 80;


params[CLOCK_FREQ_PARAM_INDEX] = 180;
params[SWITCHES_PARAM_INDEX] = 64;
params[OPERATOR_1_PARAM_INDEX] = 150;
params[OPERAND_1_HIGH_PARAM_INDEX] = 180;
```

## Understanding Peak vs RMS

**Peak Detection**: Tracks maximum instantaneous levels. Fast response to transients, good for preventing clipping, but can be misleading for continuous signals.

**RMS Detection**: Measures average power over time. Correlates better with perceived loudness, slower response but more stable, better for musical applications.

**Envelope Following**: Digital implementation uses exponential decay where release speed is controlled by bit-shifting the current level.

**Signal Presence**: Binary decision based on comparison to threshold. Different modes use peak or RMS levels for more appropriate detection.

## Try These Changes

- **Hysteresis thresholds**: Use different on/off thresholds to prevent chattering
- **Multi-band monitoring**: Split signal into frequency bands for selective monitoring
- **Gate/trigger detection**: Add onset detection for musical events
- **Auto-ducking**: Reduce other signals when input is detected

## Related Techniques

- **[Crossfade](crossfade.md)**: Blend signals based on input monitoring
- **[Mix Multiple Signals](mix-multiple-signals.md)**: Combine signals with level control
- **[Control LEDs](../visual-feedback/control-leds.md)**: Visual feedback for monitoring

---
*Part of the [Permut8 Cookbook](../index.md) series*
