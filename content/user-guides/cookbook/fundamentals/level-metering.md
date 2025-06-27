# Level Metering

*Visual feedback for monitoring audio signal levels*

## What This Does

Level metering displays audio signal levels using LED indicators. It shows peak levels to prevent clipping and provides visual feedback for gain staging and signal monitoring.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Meter sensitivity (0-255, controls response speed)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Display mode (0-255, selects different meter types)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Peak hold time (0-255, how long peaks are displayed)

**Meter Types:**
- **Peak meter**: Shows instantaneous signal peaks
- **Average meter**: Shows smoothed signal levels
- **Peak hold**: Displays peak levels with hold time

**Key Concepts:** Peak detection, level averaging, LED mapping, visual feedback

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
global int avg_level = 0
global int peak_hold_value = 0
global int peak_hold_timer = 0

function process()
locals int sensitivity, int meter_mode, int hold_time, int left_level, int right_level, int max_level, int led_level
{
    loop {

        sensitivity = ((int)global (int)global params[CLOCK_FREQ_PARAM_INDEX] >> 4) + 1;
        meter_mode = ((int)global (int)global params[SWITCHES_PARAM_INDEX] >> 6);
        hold_time = ((int)global (int)global params[OPERATOR_1_PARAM_INDEX] << 4);
        

        left_level = (int)global signal[0];
        if (left_level < 0) left_level = -left_level;
        
        right_level = (int)global signal[1];
        if (right_level < 0) right_level = -right_level;
        

        max_level = left_level;
        if (right_level > max_level) max_level = right_level;
        

        if (max_level > global peak_level) {
            global peak_level = max_level;
        } else {

            global peak_level = global peak_level - (global peak_level >> sensitivity);
        }
        

        global avg_level = global avg_level + ((max_level - global avg_level) >> 8);
        

        if (global peak_level > global peak_hold_value) {
            global peak_hold_value = global peak_level;
            global peak_hold_timer = hold_time;
        } else if (global peak_hold_timer > 0) {
            global peak_hold_timer = global peak_hold_timer - 1;
        } else {
            global peak_hold_value = global peak_hold_value - (global peak_hold_value >> 6);
        }
        

        if (meter_mode == 0) {
            led_level = global peak_level;
        } else if (meter_mode == 1) {
            led_level = global avg_level;
        } else if (meter_mode == 2) {
            led_level = global peak_hold_value;
        } else {

            led_level = (global peak_level + global avg_level) >> 1;
        }
        

        global displayLEDs[0] = led_level >> 3;
        

        if (led_level > 512) {
            global displayLEDs[1] = (led_level - 512) >> 2;
        } else {
            global displayLEDs[1] = 0;
        }
        

        if (led_level > 1280) {
            global displayLEDs[2] = (led_level - 1280) >> 1;
        } else {
            global displayLEDs[2] = 0;
        }
        

        if (led_level > 1843) {
            global displayLEDs[3] = 255;
        } else {
            global displayLEDs[3] = 0;
        }
        
        yield();

```

## How It Works

**Peak Detection**: Monitors instantaneous signal peaks to detect clipping potential. Uses fast attack (immediate response to peaks) and slower release for visual readability.

**Average Level**: Smooths signal level over time to show perceived loudness. More stable than peak detection but less responsive to transients.

**Peak Hold**: Displays peak levels for a set time so brief peaks remain visible. Essential for catching short transients.

**LED Mapping**: Different LEDs light up at different signal levels:
- LED 1: Always shows signal level
- LED 2: Only lights above moderate levels  
- LED 3: Only lights at high levels
- LED 4: Warning light for near-clipping levels

**Parameter Control**:
- **Control 1**: Meter sensitivity (higher = more responsive)
- **Control 2**: Display mode (peak, average, peak hold, or combined)
- **Control 3**: Peak hold time (how long peaks are displayed)

## Try These Settings

```impala

(int)global params[CLOCK_FREQ_PARAM_INDEX] = 128;
(int)global params[SWITCHES_PARAM_INDEX] = 0;
(int)global params[OPERATOR_1_PARAM_INDEX] = 100;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 64;
(int)global params[SWITCHES_PARAM_INDEX] = 64;
(int)global params[OPERATOR_1_PARAM_INDEX] = 0;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;
(int)global params[SWITCHES_PARAM_INDEX] = 192;
(int)global params[OPERATOR_1_PARAM_INDEX] = 200;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 32;
(int)global params[SWITCHES_PARAM_INDEX] = 128;
(int)global params[OPERATOR_1_PARAM_INDEX] = 255;
```

## Understanding Level Metering

**Peak vs Average**: Peak meters show instantaneous levels and clipping potential. Average meters show perceived loudness and signal presence.

**LED Color Zones**: Green = safe levels, yellow = caution zone, red = danger of clipping.

**Update Rate**: LEDs update fast enough to catch peaks but slow enough to be readable.

**Stereo Monitoring**: Both channels are monitored and the maximum level is displayed.

## Try These Changes

- **Stereo separation**: Show left/right channels on separate LEDs
- **Frequency bands**: Split signal into bass/treble and meter separately  
- **Correlation metering**: Show if left/right channels are in or out of phase
- **Gain reduction display**: Show how much a limiter is reducing gain

## Related Techniques

- **[Output Limiting](output-limiting.md)**: Use meters to monitor limiting activity
- **[dB Gain Control](db-gain-control.md)**: Professional gain staging with metering

---
*Part of the [Permut8 Cookbook](../index.md) series*