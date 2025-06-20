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

// Input monitoring state
global int peak_level = 0           // Current peak level
global int rms_accumulator = 0      // RMS calculation buffer
global int rms_level = 0            // Current RMS level
global int peak_hold_counter = 0    // Peak hold countdown
global int signal_present = 0       // Signal presence flag
global int previous_sample = 0      // For derivative calculation

function process()
locals int input_sample, int abs_input, int presence_threshold, int release_time, int peak_hold_time, int monitor_mode, int sample_squared, int peak_hold_samples, int release_amount, int rms_smooth
{
    loop {
        // Read input sample
        input_sample = (int)global signal[0];
        
        // Read control parameters
        presence_threshold = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];        // 0-255 threshold
        release_time = ((int)global (int)global params[SWITCHES_PARAM_INDEX] >> 4) + 1;   // 1-16 release speed
        peak_hold_time = ((int)global (int)global params[OPERATOR_1_PARAM_INDEX] << 4) + 512; // 512-4608 samples
        monitor_mode = (int)global (int)global params[OPERAND_1_HIGH_PARAM_INDEX];              // 0-255 mode select
        
        // Calculate absolute value
        if (input_sample < 0) {
            abs_input = -input_sample;
        } else {
            abs_input = input_sample;
        }
        
        // Peak detection with attack/release
        if (abs_input > global peak_level) {
            // Fast attack: immediate response to higher peaks
            global peak_level = abs_input;
            global peak_hold_counter = peak_hold_time;
        } else {
            // Peak decay with hold time
            if (global peak_hold_counter > 0) {
                global peak_hold_counter = global peak_hold_counter - 1;
            } else {
                // Apply release curve
                release_amount = global peak_level >> release_time;
                if (release_amount < 1) release_amount = 1;
                global peak_level = global peak_level - release_amount;
                if (global peak_level < 0) global peak_level = 0;
            }
        }
        
        // RMS calculation (sliding window approximation)
        sample_squared = (input_sample >> 3) * (input_sample >> 3);  // Scale to prevent overflow
        global rms_accumulator = global rms_accumulator - (global rms_accumulator >> 8); // Decay
        global rms_accumulator = global rms_accumulator + sample_squared; // Add new
        
        // Approximate square root for RMS
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
        
        // Signal presence detection
        if (monitor_mode < 128) {
            // Use peak level for presence
            if (global peak_level > presence_threshold) {
                global signal_present = 1;
            } else {
                global signal_present = 0;
            }
        } else {
            // Use RMS level for presence
            if (global rms_level > (presence_threshold >> 2)) {
                global signal_present = 1;
            } else {
                global signal_present = 0;
            }
        }
        
        // Pass input through (monitoring is non-invasive)
        global signal[0] = input_sample;
        global signal[1] = input_sample;
        
        // Display monitoring results on LEDs
        global displayLEDs[0] = global peak_level >> 3;      // Peak level (scaled to 0-255)
        global displayLEDs[1] = global rms_level << 2;       // RMS level (scaled to 0-255)
        if (global signal_present == 1) {
            global displayLEDs[2] = 255;  // Signal present
        } else {
            global displayLEDs[2] = 32;   // Signal absent
        }
        global displayLEDs[3] = presence_threshold;          // Threshold setting
        
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
// Sensitive peak monitoring
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 64;   // Low threshold - sensitive
(int)global params[SWITCHES_PARAM_INDEX] = 32;   // Slow release
(int)global params[OPERATOR_1_PARAM_INDEX] = 200;  // Long peak hold
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 64;   // Peak-based presence

// RMS-based monitoring
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 128;  // Medium threshold
(int)global params[SWITCHES_PARAM_INDEX] = 80;   // Medium release
(int)global params[OPERATOR_1_PARAM_INDEX] = 100;  // Medium peak hold
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;  // RMS-based presence

// Fast response monitoring
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 100;  // Medium threshold
(int)global params[SWITCHES_PARAM_INDEX] = 200;  // Fast release
(int)global params[OPERATOR_1_PARAM_INDEX] = 50;   // Short peak hold
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 80;   // Peak-based

// Noise-resistant monitoring
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 180;  // High threshold
(int)global params[SWITCHES_PARAM_INDEX] = 64;   // Slow release
(int)global params[OPERATOR_1_PARAM_INDEX] = 150;  // Medium hold
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 180;  // RMS-based
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
