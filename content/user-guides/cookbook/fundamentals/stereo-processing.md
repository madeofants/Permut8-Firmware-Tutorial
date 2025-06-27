# Stereo Processing

*Control stereo field width and channel relationships*

## What This Does

Stereo processing manipulates the relationship between left and right audio channels to create spatial effects, control stereo width, and position sounds in the stereo field.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Panning position (0-255, left to right)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Stereo width (0-255, mono to wide)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Channel routing (0-255, normal to swapped)

**Core Techniques:**
- **Panning**: Position mono signals in stereo field
- **Width control**: Adjust stereo image from mono to wide
- **Mid-side processing**: Separate center from sides
- **Channel routing**: Swap or mix left/right channels

**Key Concepts:** Spatial positioning, stereo field, mid-side encoding, channel relationships

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

function process()
locals int pan_position, int stereo_width, int channel_mode, int left_input, int right_input, int mid_signal, int side_signal, int left_gain, int right_gain, int mono_input, int output_left, int output_right, int panned_left, int panned_right, int width_left, int width_right
{
    loop {

        pan_position = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];
        stereo_width = (int)global (int)global params[SWITCHES_PARAM_INDEX];
        channel_mode = (int)global (int)global params[OPERATOR_1_PARAM_INDEX];
        

        left_input = (int)global signal[0];
        right_input = (int)global signal[1];
        

        mono_input = (left_input + right_input) >> 1;
        

        mid_signal = (left_input + right_input) >> 1;
        side_signal = (left_input - right_input) >> 1;
        

        side_signal = (side_signal * stereo_width) >> 8;
        

        left_gain = 255 - pan_position;
        right_gain = pan_position;
        

        panned_left = (mono_input * left_gain) >> 8;
        panned_right = (mono_input * right_gain) >> 8;
        

        width_left = mid_signal + side_signal;
        width_right = mid_signal - side_signal;
        

        if (channel_mode < 64) {

            output_left = panned_left;
            output_right = panned_right;
            
        } else if (channel_mode < 128) {

            output_left = width_left;
            output_right = width_right;
            
        } else if (channel_mode < 192) {

            output_left = right_input;
            output_right = left_input;
            
        } else {

            output_left = mid_signal;
            output_right = side_signal;
        }
        

        if (output_left > 2047) output_left = 2047;
        if (output_left < -2047) output_left = -2047;
        if (output_right > 2047) output_right = 2047;
        if (output_right < -2047) output_right = -2047;
        

        global signal[0] = output_left;
        global signal[1] = output_right;
        

        global displayLEDs[0] = pan_position;
        global displayLEDs[1] = stereo_width;
        global displayLEDs[2] = channel_mode >> 2;
        

        if (side_signal >= 0) {
            global displayLEDs[3] = side_signal >> 3;
        } else {
            global displayLEDs[3] = (-side_signal) >> 3;
        }
        
        yield();
    }
}

```

## How It Works

**Mid-Side Processing**: Separating audio into Mid (center) and Side (stereo) components allows independent control. Mid = (L+R)/2 contains vocals and center-panned elements. Side = (L-R)/2 contains stereo width and spatial information.

**Panning Laws**: Linear panning simply adjusts left/right levels, but can create a "hole in the middle" effect. Equal-power panning maintains constant loudness as sounds move across the stereo field.

**Width Control**: Adjusting the Side signal controls stereo width. Width=0 creates mono, Width=1 preserves original stereo, Width>1 creates enhanced stereo.

**Channel Routing**: Different processing modes handle various stereo tasks - panning mono signals, adjusting width of stereo signals, swapping channels, or monitoring mid/side content.

**Parameter Control**:
- **Control 1**: Pan position or processing parameter
- **Control 2**: Stereo width or processing mode
- **Control 3**: Processing mode or channel routing

## Try These Settings

```impala

(int)global params[CLOCK_FREQ_PARAM_INDEX] = 128;
(int)global params[SWITCHES_PARAM_INDEX] = 128;
(int)global params[OPERATOR_1_PARAM_INDEX] = 32;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 64;
(int)global params[SWITCHES_PARAM_INDEX] = 200;
(int)global params[OPERATOR_1_PARAM_INDEX] = 96;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 128;
(int)global params[SWITCHES_PARAM_INDEX] = 128;
(int)global params[OPERATOR_1_PARAM_INDEX] = 160;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 128;
(int)global params[SWITCHES_PARAM_INDEX] = 128;
(int)global params[OPERATOR_1_PARAM_INDEX] = 224;
```

## Understanding Stereo Processing

**Mid-Side Encoding**: Mid signal contains center-panned content (vocals, bass, kick drum). Side signal contains stereo spread content (reverb, wide instruments, ambience).

**Width vs Pan**: Panning positions mono signals in the stereo field. Width control adjusts how wide existing stereo content appears.

**Phase Relationship**: Left and right channels can be in-phase (mono-like) or out-of-phase (wide stereo). Extreme width settings can cause phase cancellation on mono systems.

**Processing Modes**: Different modes handle different stereo tasks efficiently within a single processor.

## Try These Changes

- **Auto-width**: Automatically adjust width based on signal correlation
- **Frequency-dependent width**: Make bass more centered, highs wider
- **Stereo enhancement**: Add subtle width to mono sources
- **Phase correlation monitoring**: Prevent mono compatibility issues

## Related Techniques

- **[Parameter Mapping](parameter-mapping.md)**: Control stereo parameters smoothly
- **[Basic Filter](basic-filter.md)**: Frequency-dependent stereo processing

---
*Part of the [Permut8 Cookbook](../index.md) series*