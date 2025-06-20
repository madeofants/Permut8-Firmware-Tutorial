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

// Level meter state
global int peak_level = 0       // Current peak level
global int avg_level = 0        // Average level
global int peak_hold_value = 0  // Peak hold level
global int peak_hold_timer = 0  // Peak hold countdown

function process()
locals int sensitivity, int meter_mode, int hold_time, int left_level, int right_level, int max_level, int led_level
{
    loop {
        // Read parameters
        sensitivity = ((int)global (int)global params[CLOCK_FREQ_PARAM_INDEX] >> 4) + 1;  // 1-16 sensitivity
        meter_mode = ((int)global (int)global params[SWITCHES_PARAM_INDEX] >> 6);        // 0-3 meter types
        hold_time = ((int)global (int)global params[OPERATOR_1_PARAM_INDEX] << 4);         // 0-4080 hold time
        
        // Get absolute signal levels
        left_level = (int)global signal[0];
        if (left_level < 0) left_level = -left_level;
        
        right_level = (int)global signal[1];
        if (right_level < 0) right_level = -right_level;
        
        // Find maximum level (stereo peak)
        max_level = left_level;
        if (right_level > max_level) max_level = right_level;
        
        // Update peak level (fast attack)
        if (max_level > global peak_level) {
            global peak_level = max_level;
        } else {
            // Slow release based on sensitivity
            global peak_level = global peak_level - (global peak_level >> sensitivity);
        }
        
        // Update average level (slower response)
        global avg_level = global avg_level + ((max_level - global avg_level) >> 8);
        
        // Peak hold logic
        if (global peak_level > global peak_hold_value) {
            global peak_hold_value = global peak_level;
            global peak_hold_timer = hold_time;
        } else if (global peak_hold_timer > 0) {
            global peak_hold_timer = global peak_hold_timer - 1;
        } else {
            global peak_hold_value = global peak_hold_value - (global peak_hold_value >> 6);
        }
        
        // Select display level based on meter mode
        if (meter_mode == 0) {
            led_level = global peak_level;      // Peak meter
        } else if (meter_mode == 1) {
            led_level = global avg_level;       // Average meter
        } else if (meter_mode == 2) {
            led_level = global peak_hold_value; // Peak hold meter
        } else {
            // Combined display
            led_level = (global peak_level + global avg_level) >> 1;
        }
        
        // Map level to LED display (0-2047 → 0-255 per LED)
        global displayLEDs[0] = led_level >> 3;           // LED 1: Full range
        
        // LED 2: Only for higher levels
        if (led_level > 512) {
            global displayLEDs[1] = (led_level - 512) >> 2;
        } else {
            global displayLEDs[1] = 0;
        }
        
        // LED 3: Only for even higher levels  
        if (led_level > 1280) {
            global displayLEDs[2] = (led_level - 1280) >> 1;
        } else {
            global displayLEDs[2] = 0;
        }
        
        // LED 4: Peak warning (red zone)
        if (led_level > 1843) {  // About 90% of full scale
            global displayLEDs[3] = 255;  // Full brightness warning
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
// Standard peak meter
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 128;  // Medium sensitivity
(int)global params[SWITCHES_PARAM_INDEX] = 0;    // Peak mode
(int)global params[OPERATOR_1_PARAM_INDEX] = 100;  // Short peak hold

// Average level meter
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 64;   // Lower sensitivity
(int)global params[SWITCHES_PARAM_INDEX] = 64;   // Average mode
(int)global params[OPERATOR_1_PARAM_INDEX] = 0;    // No peak hold

// Combined display
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;  // High sensitivity
(int)global params[SWITCHES_PARAM_INDEX] = 192;  // Combined mode
(int)global params[OPERATOR_1_PARAM_INDEX] = 200;  // Long peak hold

// Slow monitoring
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 32;   // Very low sensitivity
(int)global params[SWITCHES_PARAM_INDEX] = 128;  // Peak hold mode
(int)global params[OPERATOR_1_PARAM_INDEX] = 255;  // Maximum hold time
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