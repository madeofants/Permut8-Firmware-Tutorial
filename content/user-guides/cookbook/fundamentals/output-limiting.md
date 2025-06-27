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


global int gain_reduction = 2047
global int peak_detector = 0

function process()
locals int threshold, int release_speed, int strength, int left_peak, int right_peak, int max_peak, int target_gain, int limited_left, int limited_right, int over_threshold, int reduction_needed
{
    loop {

        threshold = ((int)global (int)global params[CLOCK_FREQ_PARAM_INDEX] << 3) + 512;
        release_speed = ((int)global (int)global params[SWITCHES_PARAM_INDEX] >> 4) + 1;
        strength = ((int)global (int)global params[OPERATOR_1_PARAM_INDEX] >> 2) + 1;
        

        left_peak = (int)global signal[0];
        if (left_peak < 0) left_peak = -left_peak;
        
        right_peak = (int)global signal[1];
        if (right_peak < 0) right_peak = -right_peak;
        

        max_peak = left_peak;
        if (right_peak > max_peak) max_peak = right_peak;
        

        if (max_peak > global peak_detector) {
            global peak_detector = max_peak;
        } else {
            global peak_detector = global peak_detector - (global peak_detector >> 8);
        }
        

        target_gain = 2047;
        
        if (global peak_detector > threshold) {

            over_threshold = global peak_detector - threshold;
            reduction_needed = (over_threshold * strength) >> 6;
            

            target_gain = 2047 - reduction_needed;
            

            if (target_gain < 256) target_gain = 256;
        }
        

        if (target_gain < global gain_reduction) {

            global gain_reduction = target_gain;
        } else {

            global gain_reduction = global gain_reduction + 
                ((target_gain - global gain_reduction) >> (8 - (release_speed >> 2)));
        }
        

        limited_left = ((int)global signal[0] * global gain_reduction) >> 11;
        limited_right = ((int)global signal[1] * global gain_reduction) >> 11;
        

        if (limited_left > 2047) limited_left = 2047;
        if (limited_left < -2047) limited_left = -2047;
        if (limited_right > 2047) limited_right = 2047;
        if (limited_right < -2047) limited_right = -2047;
        

        global signal[0] = limited_left;
        global signal[1] = limited_right;
        

        global displayLEDs[0] = threshold >> 3;
        global displayLEDs[1] = global peak_detector >> 3;
        global displayLEDs[2] = (2047 - global gain_reduction) >> 3;
        global displayLEDs[3] = release_speed << 4;
        
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

(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;
(int)global params[SWITCHES_PARAM_INDEX] = 100;
(int)global params[OPERATOR_1_PARAM_INDEX] = 80;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 150;
(int)global params[SWITCHES_PARAM_INDEX] = 200;
(int)global params[OPERATOR_1_PARAM_INDEX] = 180;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 100;
(int)global params[SWITCHES_PARAM_INDEX] = 50;
(int)global params[OPERATOR_1_PARAM_INDEX] = 255;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 220;
(int)global params[SWITCHES_PARAM_INDEX] = 128;
(int)global params[OPERATOR_1_PARAM_INDEX] = 60;
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