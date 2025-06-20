# Output Limiting

*Prevent clipping and protect audio equipment*

## What This Does

Output limiting automatically reduces gain when audio signals get too loud, preventing digital clipping and protecting speakers. It only activates when signals exceed a threshold, maintaining natural dynamics while ensuring safe output levels.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Threshold level (0-255, where limiting starts)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Release speed (0-255, how fast limiting recovers)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Limiter strength (0-255, how hard it limits)

**Common Settings:**
- **Gentle limiting**: High threshold, slow release, light strength
- **Brick wall**: Medium threshold, fast release, maximum strength
- **Musical**: Medium threshold, slow release, moderate strength

**Key Concepts:** Peak detection, gain reduction, attack/release timing, safe levels

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

// Limiter state
global int gain_reduction = 2047 // Current gain reduction (2047 = no reduction)
global int peak_detector = 0    // Peak level detector

function process()
locals int threshold, int release_speed, int strength, int left_peak, int right_peak, int max_peak, int target_gain, int limited_left, int limited_right, int over_threshold, int reduction_needed
{
    loop {
        // Read parameters
        threshold = ((int)global (int)global params[CLOCK_FREQ_PARAM_INDEX] << 3) + 512;  // 512-2560 threshold range
        release_speed = ((int)global (int)global params[SWITCHES_PARAM_INDEX] >> 4) + 1; // 1-16 release rate
        strength = ((int)global (int)global params[OPERATOR_1_PARAM_INDEX] >> 2) + 1;     // 1-64 limiter strength
        
        // Detect peak levels in both channels
        left_peak = (int)global signal[0];
        if (left_peak < 0) left_peak = -left_peak;   // Absolute value
        
        right_peak = (int)global signal[1];
        if (right_peak < 0) right_peak = -right_peak; // Absolute value
        
        // Find maximum peak
        max_peak = left_peak;
        if (right_peak > max_peak) max_peak = right_peak;
        
        // Update peak detector with decay
        if (max_peak > global peak_detector) {
            global peak_detector = max_peak;  // Fast attack
        } else {
            global peak_detector = global peak_detector - (global peak_detector >> 8); // Slow decay
        }
        
        // Calculate required gain reduction
        target_gain = 2047;  // No reduction by default
        
        if (global peak_detector > threshold) {
            // Calculate how much over threshold we are
            over_threshold = global peak_detector - threshold;
            reduction_needed = (over_threshold * strength) >> 6;
            
            // Calculate target gain (less gain = more reduction)
            target_gain = 2047 - reduction_needed;
            
            // Minimum gain (maximum reduction)
            if (target_gain < 256) target_gain = 256;  // -18dB max reduction
        }
        
        // Smooth gain changes (fast attack, adjustable release)
        if (target_gain < global gain_reduction) {
            // Fast attack to catch peaks quickly
            global gain_reduction = target_gain;
        } else {
            // Slower release for natural sound
            global gain_reduction = global gain_reduction + 
                ((target_gain - global gain_reduction) >> (8 - (release_speed >> 2)));
        }
        
        // Apply limiting to both channels
        limited_left = ((int)global signal[0] * global gain_reduction) >> 11;
        limited_right = ((int)global signal[1] * global gain_reduction) >> 11;
        
        // Hard clipping safety (should never engage with proper limiting)
        if (limited_left > 2047) limited_left = 2047;
        if (limited_left < -2047) limited_left = -2047;
        if (limited_right > 2047) limited_right = 2047;
        if (limited_right < -2047) limited_right = -2047;
        
        // Output limited signals
        global signal[0] = limited_left;
        global signal[1] = limited_right;
        
        // Show limiter activity on LEDs
        global displayLEDs[0] = threshold >> 3;           // Show threshold setting
        global displayLEDs[1] = global peak_detector >> 3; // Show peak level
        global displayLEDs[2] = (2047 - global gain_reduction) >> 3; // Show gain reduction
        global displayLEDs[3] = release_speed << 4;      // Show release setting
        
        yield();
}

```

## How It Works

**Peak Detection**: Continuously monitors both audio channels to find the loudest peaks.

**Threshold Comparison**: When peaks exceed the threshold, limiting activates to reduce gain.

**Fast Attack**: Immediately reduces gain when peaks are detected to prevent clipping.

**Adjustable Release**: Gradually restores gain when peaks subside, controlled by release speed parameter.

**Gain Reduction**: Multiplies the audio signal by a factor less than 1.0 to reduce level.

**Parameter Control**:
- **Control 1**: Threshold (higher = limiting starts later)
- **Control 2**: Release speed (higher = faster recovery)
- **Control 3**: Limiter strength (higher = more aggressive limiting)

## Try These Settings

```impala
// Gentle mastering limiter
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;  // High threshold
(int)global params[SWITCHES_PARAM_INDEX] = 100;  // Moderate release
(int)global params[OPERATOR_1_PARAM_INDEX] = 80;   // Light limiting

// Broadcast safety limiter
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 150;  // Medium threshold
(int)global params[SWITCHES_PARAM_INDEX] = 200;  // Fast release
(int)global params[OPERATOR_1_PARAM_INDEX] = 180;  // Strong limiting

// Aggressive maximizer
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 100;  // Low threshold
(int)global params[SWITCHES_PARAM_INDEX] = 50;   // Slow release
(int)global params[OPERATOR_1_PARAM_INDEX] = 255;  // Maximum limiting

// Transparent protection
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 220;  // Very high threshold
(int)global params[SWITCHES_PARAM_INDEX] = 128;  // Balanced release
(int)global params[OPERATOR_1_PARAM_INDEX] = 60;   // Very light limiting
```

## Understanding Limiting

**Peak vs RMS**: Limiting typically responds to peak levels to prevent clipping, not average loudness.

**Attack Time**: Fast attack catches transients but may sound pumpy. The code uses instant attack for peak protection.

**Release Time**: Slow release sounds more natural but may reduce dynamics. Fast release maintains loudness but may sound choppy.

**Threshold**: Higher threshold means limiting starts later, preserving more dynamics but risking clipping.

**Strength**: Controls how aggressively limiting reduces gain above the threshold.

## Try These Changes

- **Stereo linking**: Process left/right channels together to maintain stereo image
- **Lookahead**: Delay output while analyzing future peaks for smoother limiting
- **Soft knee**: Gradually increase limiting ratio near the threshold
- **Frequency splitting**: Apply different limiting to bass vs treble frequencies

## Related Techniques

- **[dB Gain Control](db-gain-control.md)**: Professional gain staging before limiting
- **[Level Metering](level-metering.md)**: Monitor peak levels visually

---
*Part of the [Permut8 Cookbook](../index.md) series*