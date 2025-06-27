# Waveshaper Distortion

*Create harmonic distortion by reshaping audio waveforms*

## What This Does

Creates distortion by applying mathematical curves to reshape the audio waveform. Generates everything from subtle tube warmth to aggressive clipping effects by pushing audio through different waveshaping functions.

## Quick Reference

**Essential Parameters:**
- `params[CLOCK_FREQ_PARAM_INDEX]`: Input drive (0-255, controls distortion intensity)
- `params[SWITCHES_PARAM_INDEX]`: Distortion type (0-255, selects waveshaping curve)
- `params[OPERATOR_1_PARAM_INDEX]`: Output level (0-255, compensates for volume changes)
- `params[OPERAND_1_HIGH_PARAM_INDEX]`: Dry/wet mix (0-255, blend control)

**Key Concepts:** Waveshaping curves, harmonic generation, clipping algorithms, drive control

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

function process()
locals int drive, int dist_type, int output_level, int mix, int input, int driven, int shaped, int output, int mask
{
    loop {

        drive = ((int)global params[CLOCK_FREQ_PARAM_INDEX] >> 2) + 1;
        dist_type = ((int)global params[SWITCHES_PARAM_INDEX] >> 6);
        output_level = ((int)global params[OPERATOR_1_PARAM_INDEX] >> 1) + 64;
        mix = (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
        
        input = (int)global signal[0];
        

        driven = input * drive;
        

        if (driven > 2047) driven = 2047;
        if (driven < -2047) driven = -2047;
        

        if (dist_type == 0) {

            if (driven > 1365) {
                shaped = 1365 + ((driven - 1365) >> 2);
            } else if (driven < -1365) {
                shaped = -1365 + ((driven + 1365) >> 2);
            } else {
                shaped = driven;
            }
            
        } else if (dist_type == 1) {

            if (driven > 1024) {
                shaped = 1024;
            } else if (driven < -1024) {
                shaped = -1024;
            } else {
                shaped = driven;
            }
            
        } else if (dist_type == 2) {

            mask = 0xFFF0;
            shaped = driven & mask;
            
        } else {

            if (driven > 1024) {
                shaped = 2048 - driven;
            } else if (driven < -1024) {
                shaped = -2048 + driven;
            } else {
                shaped = driven;
            }
        }
        

        shaped = (shaped * output_level) >> 8;
        

        if (shaped > 2047) shaped = 2047;
        if (shaped < -2047) shaped = -2047;
        

        output = ((input * (255 - mix)) + (shaped * mix)) >> 8;
        

        global signal[0] = output;
        global signal[1] = output;
        

        global displayLEDs[0] = (drive - 1) << 2;
        global displayLEDs[1] = dist_type << 6;
        global displayLEDs[2] = (output_level - 64) << 1;
        global displayLEDs[3] = (mix >> 2);
        
        yield();
    }
}

```

## How It Works

**Input Drive**: Amplifies the signal before waveshaping to control distortion intensity.

**Waveshaping Types**:
- **Type 0 (Soft Clip)**: Gentle compression at high levels, preserves dynamics
- **Type 1 (Hard Clip)**: Aggressive limiting, creates square-wave harmonics
- **Type 2 (Bit Crush)**: Digital artifacts by removing bit resolution
- **Type 3 (Fold-back)**: Wraps signal around at limits for unique textures

**Output Compensation**: Adjusts level after distortion to maintain consistent volume.

**Parameter Control**:
- **Control 1**: Drive (higher = more distortion)
- **Control 2**: Type (0-63=soft, 64-127=hard, 128-191=bit, 192-255=fold)
- **Control 3**: Output level (compensate for volume changes)
- **Control 4**: Dry/wet mix (blend clean with distorted)

## Try These Settings

```impala

global params[CLOCK_FREQ_PARAM_INDEX] = 100;
global params[SWITCHES_PARAM_INDEX] = 32;
global params[OPERATOR_1_PARAM_INDEX] = 180;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 150;


global params[CLOCK_FREQ_PARAM_INDEX] = 200;
global params[SWITCHES_PARAM_INDEX] = 100;
global params[OPERATOR_1_PARAM_INDEX] = 140;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 220;


global params[CLOCK_FREQ_PARAM_INDEX] = 150;
global params[SWITCHES_PARAM_INDEX] = 160;
global params[OPERATOR_1_PARAM_INDEX] = 200;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 180;


global params[CLOCK_FREQ_PARAM_INDEX] = 180;
global params[SWITCHES_PARAM_INDEX] = 220;
global params[OPERATOR_1_PARAM_INDEX] = 160;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;
```

## Understanding Waveshaping

**Harmonic Generation**: Waveshaping creates new frequencies (harmonics) not present in the original signal by applying non-linear functions.

**Drive vs. Output**: Drive controls how hard you push into the waveshaper (distortion amount), while output compensates for the resulting volume changes.

**Waveshaping Curves**: Different mathematical functions create different harmonic content:
- **Linear**: No distortion (straight line)
- **Soft curves**: Gentle, musical harmonics
- **Hard edges**: Aggressive, buzzy harmonics
- **Fold-back**: Unique, metallic textures

## Try These Changes

- **Multiple stages**: Apply waveshaping twice for more complex distortion
- **Frequency-dependent**: Apply different amounts to high vs low frequencies
- **Dynamic waveshaping**: Vary the curve based on input level
- **Stereo processing**: Different waveshaping for left/right channels

## Related Techniques

- **[Gain and Volume](../fundamentals/gain-and-volume.md)**: Level control fundamentals
- **[Bitcrusher](bitcrusher.md)**: Related digital distortion effects

---
*Part of the [Permut8 Cookbook](../index.md) series*