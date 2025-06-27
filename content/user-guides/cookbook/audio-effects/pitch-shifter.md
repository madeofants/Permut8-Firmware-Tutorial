# Pitch Shifter

*Simple pitch shifting using variable delay*

## What This Does

Creates basic pitch shifting by using a variable delay line with modulated read speed. This creates pitch changes by reading the delay buffer faster (higher pitch) or slower (lower pitch), similar to changing tape speed.

## Quick Reference

**Essential Parameters:**
- `params[CLOCK_FREQ_PARAM_INDEX]`: Pitch shift (0-255, where 128 = no shift)
- `params[SWITCHES_PARAM_INDEX]`: Buffer size (0-255, affects quality vs latency)
- `params[OPERATOR_1_PARAM_INDEX]`: Smoothing (0-255, reduces glitches)
- `params[OPERAND_1_HIGH_PARAM_INDEX]`: Dry/wet mix (0-255, blend control)

**Key Concepts:** Variable delay, read speed modulation, simple time-stretch, pitch-time relationship

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
extern native read
extern native write


global int clock
global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clockFreqLimit


global array temp_buffer[2]
global int write_pos = 0
global int read_pos_frac = 0
global int last_sample_l = 0
global int last_sample_r = 0
const int MAX_BUFFER_SIZE = 4096

function process()
locals int pitch_shift, int buffer_size, int smoothing, int mix, int pitch_speed, int new_read_pos, int current_sample_l, int current_sample_r, int smoothed_sample_l, int smoothed_sample_r, int output_l, int output_r, int smooth_factor, int position_diff
{
    loop {

        pitch_shift = (int)global params[CLOCK_FREQ_PARAM_INDEX];
        buffer_size = ((int)global params[SWITCHES_PARAM_INDEX] >> 2) + 32;
        smoothing = ((int)global params[OPERATOR_1_PARAM_INDEX] >> 3) + 1;
        mix = (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
        

        if (buffer_size > 1000) buffer_size = 1000;
        

        global temp_buffer[0] = global signal[0];
        write(global write_pos, 1, global temp_buffer);
        

        global temp_buffer[0] = global signal[1];
        write(global write_pos + MAX_BUFFER_SIZE, 1, global temp_buffer);
        


        if (pitch_shift < 128) {
            pitch_speed = 128 + (pitch_shift >> 1);
        } else {
            pitch_speed = 128 + ((pitch_shift - 128) << 1);
        }
        

        global read_pos_frac = (global read_pos_frac + pitch_speed) & 65535;
        

        new_read_pos = global write_pos - (global read_pos_frac >> 8) - buffer_size;
        

        while (new_read_pos < 0) {
            new_read_pos = new_read_pos + MAX_BUFFER_SIZE;
        }
        

        read(new_read_pos, 1, global temp_buffer);
        current_sample_l = (int)global temp_buffer[0];
        

        read(new_read_pos + MAX_BUFFER_SIZE, 1, global temp_buffer);
        current_sample_r = (int)global temp_buffer[0];
        

        smooth_factor = smoothing & 7;
        

        smoothed_sample_l = global last_sample_l + ((current_sample_l - global last_sample_l) >> smooth_factor);
        global last_sample_l = smoothed_sample_l;
        

        smoothed_sample_r = global last_sample_r + ((current_sample_r - global last_sample_r) >> smooth_factor);
        global last_sample_r = smoothed_sample_r;
        

        position_diff = global write_pos - new_read_pos;
        if (position_diff > (buffer_size + 100)) {

            global read_pos_frac = global read_pos_frac - 256;
        }
        

        output_l = (((int)global signal[0] * (255 - mix)) + (smoothed_sample_l * mix)) >> 8;
        

        output_r = (((int)global signal[1] * (255 - mix)) + (smoothed_sample_r * mix)) >> 8;
        

        if (output_l > 2047) output_l = 2047;
        if (output_l < -2047) output_l = -2047;
        

        if (output_r > 2047) output_r = 2047;
        if (output_r < -2047) output_r = -2047;
        

        global signal[0] = output_l;
        global signal[1] = output_r;
        

        global displayLEDs[0] = pitch_shift;
        global displayLEDs[1] = (global read_pos_frac >> 8);
        global displayLEDs[2] = (buffer_size - 32) << 2;
        global displayLEDs[3] = (mix >> 2);
        

        global write_pos = (global write_pos + 1) % MAX_BUFFER_SIZE;
        
        yield();
    }
}

```

## How It Works

**Variable Delay**: Uses a delay buffer with a variable read position that moves at different speeds.

**Pitch Speed Control**: Reading faster creates higher pitch, reading slower creates lower pitch.

**Fractional Positioning**: Uses fixed-point arithmetic for smooth read position changes.

**Simple Smoothing**: Reduces glitches by interpolating between samples.

**Parameter Control**:
- **Control 1**: Pitch shift (128 = normal, <128 = lower, >128 = higher)
- **Control 2**: Buffer size (larger = better quality, more latency)  
- **Control 3**: Smoothing (higher = smoother but less responsive, limited to reasonable range)
- **Control 4**: Dry/wet mix (blend original with pitch-shifted)

**Stereo Processing**: Left and right channels processed independently for true stereo pitch shifting.

## Try These Settings

```impala

global params[CLOCK_FREQ_PARAM_INDEX] = 200;
global params[SWITCHES_PARAM_INDEX] = 128;
global params[OPERATOR_1_PARAM_INDEX] = 64;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;


global params[CLOCK_FREQ_PARAM_INDEX] = 64;
global params[SWITCHES_PARAM_INDEX] = 180;
global params[OPERATOR_1_PARAM_INDEX] = 128;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 180;


global params[CLOCK_FREQ_PARAM_INDEX] = 140;
global params[SWITCHES_PARAM_INDEX] = 64;
global params[OPERATOR_1_PARAM_INDEX] = 32;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 128;
```

## Limitations & Improvements

**Current Limitations**:
- Time stretching (pitch affects duration)
- Periodic glitches at buffer boundaries
- Limited pitch range before artifacts

**Possible Improvements**:
- **Windowing**: Add crossfading between buffer regions
- **Interpolation**: Better sample interpolation for smoother results
- **Multiple voices**: Overlap multiple delay lines for artifact reduction

## Try These Changes

- **Stereo pitch**: Different pitch amounts for left/right channels
- **LFO modulation**: Slowly vary pitch for vibrato effects
- **Harmonic pitch**: Add multiple pitch-shifted voices for chord effects
- **Feedback**: Add some output back to input for resonance

## Related Techniques

- **[Make a Delay](make-a-delay.md)**: Delay buffer fundamentals
- **[Chorus Effect](chorus-effect.md)**: Similar modulated delay concepts

---
*Part of the [Permut8 Cookbook](../index.md) series*