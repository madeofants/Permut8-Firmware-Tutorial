# Level Meters

*Create professional audio level meters using LED displays for visual feedback*

## What This Does

Visualize audio levels using peak detection and LED bar graphs. Shows input levels, output levels, and other audio parameters with responsive meters that follow audio dynamics.

## Quick Reference

**Essential Parameters:**
- `params[0]`: Meter sensitivity (0-255)
- `params[1]`: Meter type (0-255, peak/RMS mode)
- `params[2]`: Decay rate (0-255, how fast meter falls)
- `params[3]`: Peak hold time (0-255)

**Core Techniques:**
- **Peak detection**: Track maximum signal levels
- **RMS approximation**: Average signal energy
- **Bar graph display**: Visual level representation
- **Multiple meter types**: Different ballistics

**Key Concepts:** Peak detection, level scaling, LED mapping, meter ballistics

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Level meter state
global int peak_level_left = 0      // Left channel peak
global int peak_level_right = 0     // Right channel peak
global int rms_accumulator_left = 0 // Left RMS calculation
global int rms_accumulator_right = 0// Right RMS calculation
global int rms_level_left = 0       // Left RMS value
global int rms_level_right = 0      // Right RMS value
global int sample_counter = 0       // RMS sample counter

function process()
locals int sensitivity, int meter_type, int decay_rate, int peak_hold, int input_left, int input_right, int abs_left, int abs_right, int led_count_left, int led_count_right, int level_pattern_left, int level_pattern_right, int sample_squared
{
    loop {
        // Read control parameters
        sensitivity = ((int)global params[0] >> 1) + 64;  // 64-191 range
        meter_type = (int)global params[1] >> 6;           // 0-3 range
        decay_rate = ((int)global params[2] >> 5) + 1;    // 1-8 range
        peak_hold = (int)global params[3];                // 0-255
        
        // Read audio inputs
        input_left = (int)global signal[0];
        input_right = (int)global signal[1];
        
        // Calculate absolute values
        if (input_left < 0) {
            abs_left = -input_left;
        } else {
            abs_left = input_left;
        }
        
        if (input_right < 0) {
            abs_right = -input_right;
        } else {
            abs_right = input_right;
        }
        
        // Scale by sensitivity
        abs_left = (abs_left * sensitivity) >> 7;   // Divide by 128
        abs_right = (abs_right * sensitivity) >> 7; // Divide by 128
        
        // === LEFT CHANNEL METER ===
        if (meter_type < 2) {
            // Peak meter mode
            if (abs_left > global peak_level_left) {
                global peak_level_left = abs_left;  // Fast attack
            } else {
                // Decay
                global peak_level_left = global peak_level_left - decay_rate;
                if (global peak_level_left < 0) global peak_level_left = 0;
            }
            
            // Convert peak to LED count (0-8)
            led_count_left = global peak_level_left >> 8;  // Scale to 0-8 range
            if (led_count_left > 8) led_count_left = 8;
            
        } else {
            // RMS meter mode
            sample_squared = (abs_left >> 4) * (abs_left >> 4); // Scale to prevent overflow
            global rms_accumulator_left = global rms_accumulator_left - (global rms_accumulator_left >> 6); // Decay
            global rms_accumulator_left = global rms_accumulator_left + sample_squared;
            
            // Approximate square root for RMS
            if (global rms_accumulator_left > 1024) {
                global rms_level_left = 32 + (global rms_accumulator_left >> 6);
            } else if (global rms_accumulator_left > 256) {
                global rms_level_left = 16 + (global rms_accumulator_left >> 5);
            } else {
                global rms_level_left = global rms_accumulator_left >> 4;
            }
            
            led_count_left = global rms_level_left >> 6;  // Scale to 0-8 range
            if (led_count_left > 8) led_count_left = 8;
        }
        
        // Create LED pattern for left channel
        level_pattern_left = 0;
        if (led_count_left >= 1) level_pattern_left = 1;
        if (led_count_left >= 2) level_pattern_left = level_pattern_left | 2;
        if (led_count_left >= 3) level_pattern_left = level_pattern_left | 4;
        if (led_count_left >= 4) level_pattern_left = level_pattern_left | 8;
        if (led_count_left >= 5) level_pattern_left = level_pattern_left | 16;
        if (led_count_left >= 6) level_pattern_left = level_pattern_left | 32;
        if (led_count_left >= 7) level_pattern_left = level_pattern_left | 64;
        if (led_count_left >= 8) level_pattern_left = level_pattern_left | 128;
        global displayLEDs[0] = level_pattern_left;
        
        // === RIGHT CHANNEL METER (same logic as left) ===
        if (meter_type < 2) {
            // Peak meter mode
            if (abs_right > global peak_level_right) {
                global peak_level_right = abs_right;
            } else {
                global peak_level_right = global peak_level_right - decay_rate;
                if (global peak_level_right < 0) global peak_level_right = 0;
            }
            
            led_count_right = global peak_level_right >> 8;
            if (led_count_right > 8) led_count_right = 8;
            
        } else {
            // RMS meter mode
            sample_squared = (abs_right >> 4) * (abs_right >> 4);
            global rms_accumulator_right = global rms_accumulator_right - (global rms_accumulator_right >> 6);
            global rms_accumulator_right = global rms_accumulator_right + sample_squared;
            
            if (global rms_accumulator_right > 1024) {
                global rms_level_right = 32 + (global rms_accumulator_right >> 6);
            } else if (global rms_accumulator_right > 256) {
                global rms_level_right = 16 + (global rms_accumulator_right >> 5);
            } else {
                global rms_level_right = global rms_accumulator_right >> 4;
            }
            
            led_count_right = global rms_level_right >> 6;
            if (led_count_right > 8) led_count_right = 8;
        }
        
        // Create LED pattern for right channel
        level_pattern_right = 0;
        if (led_count_right >= 1) level_pattern_right = 1;
        if (led_count_right >= 2) level_pattern_right = level_pattern_right | 2;
        if (led_count_right >= 3) level_pattern_right = level_pattern_right | 4;
        if (led_count_right >= 4) level_pattern_right = level_pattern_right | 8;
        if (led_count_right >= 5) level_pattern_right = level_pattern_right | 16;
        if (led_count_right >= 6) level_pattern_right = level_pattern_right | 32;
        if (led_count_right >= 7) level_pattern_right = level_pattern_right | 64;
        if (led_count_right >= 8) level_pattern_right = level_pattern_right | 128;
        global displayLEDs[1] = level_pattern_right;
        
        // Status displays
        global displayLEDs[2] = meter_type << 6;  // Show meter type
        global displayLEDs[3] = sensitivity;      // Show sensitivity
        
        // Pass audio through unchanged
        global signal[0] = input_left;
        global signal[1] = input_right;
        
        yield();
    }
}
```

## How It Works

**Peak Detection**: Tracks maximum signal levels with fast attack and controlled decay. Higher sensitivity makes meter more responsive to quiet signals.

**RMS Approximation**: Estimates average signal energy using a sliding window approach. Shows average power rather than peak levels.

**Meter Types**: Peak mode responds quickly to transients, RMS mode shows sustained energy levels.

**LED Mapping**: Audio levels are scaled and converted to LED bar patterns, creating visual meters.

**Parameter Control**:
- **Knob 1**: Meter sensitivity (higher = more sensitive)
- **Knob 2**: Meter type (0-64=peak, 65-128=peak slow, 129-192=RMS, 193-255=RMS smooth)
- **Knob 3**: Decay rate (how fast peaks fall)
- **Knob 4**: Peak hold time (future enhancement)

## Try These Settings

```impala
// Sensitive peak meters
params[0] = 200;  // High sensitivity
params[1] = 32;   // Fast peak mode
params[2] = 64;   // Medium decay
params[3] = 100;  // Peak hold setting

// RMS average meters
params[0] = 128;  // Normal sensitivity
params[1] = 150;  // RMS mode
params[2] = 32;   // Slow decay
params[3] = 150;  // Hold setting

// Conservative metering
params[0] = 100;  // Lower sensitivity
params[1] = 64;   // Medium peak
params[2] = 128;  // Fast decay
params[3] = 50;   // Short hold

// Professional monitoring
params[0] = 150;  // Good sensitivity
params[1] = 180;  // Smooth RMS
params[2] = 100;  // Balanced decay
params[3] = 200;  // Long hold
```
## How It Works

### **Peak Detection Theory**
Peak detection tracks the maximum signal amplitude over time with exponential decay. Fast attack preserves transients while adjustable decay provides visual response control.

### **RMS Calculation**
RMS (Root Mean Square) provides better representation of perceived loudness by calculating the average power over a time window.

### **VU Meter Ballistics**
VU meters have specific attack and release characteristics (~300ms) that match human perception of audio dynamics.

### **LED Mapping**
Linear-to-LED conversion maps audio levels to visual representation, with optional logarithmic scaling for professional dB-style meters.

## Memory Usage

The level meter system uses minimal memory:
- State variables: 9 integers
- RMS calculation: 2 integers
- Total: ~45 bytes

## Related Techniques

- **control-leds.md** - Basic LED control and patterns
- **parameter-display.md** - Visual parameter feedback
- **gain-and-volume.md** - Audio level concepts and processing
- **basic-filter.md** - Frequency-dependent level measurement

---

*This level meter system provides professional-quality visual feedback for audio levels, dynamics, and processing. Perfect for monitoring input levels, compression activity, and frequency content with real-time LED visualization.*

## Understanding Meter Types

**Peak Meters**: Track maximum signal levels with fast attack and controlled decay. Best for preventing clipping and monitoring transients.

**RMS Meters**: Estimate average signal energy over time. Better representation of perceived loudness, good for monitoring program material.

**Ballistics**: Different attack and release characteristics affect how meters respond to audio dynamics.

**Level Scaling**: Audio levels are mapped to LED counts for visual representation. Sensitivity control adjusts this mapping.

## Try These Changes

- **Multi-band metering**: Use simple filters to separate frequency bands
- **Stereo correlation**: Show sum and difference between left/right channels
- **Gain reduction**: Display difference between input and processed output
- **Peak hold**: Add peak hold functionality that maintains maximum levels

## Related Techniques

- **[Control LEDs](control-leds.md)**: Basic LED patterns and control
- **[Parameter Display](parameter-display.md)**: Show parameter values on LEDs
- **[Input Monitoring](../utilities/input-monitoring.md)**: Advanced signal detection

---
*Part of the [Permut8 Cookbook](../index.md) series*
