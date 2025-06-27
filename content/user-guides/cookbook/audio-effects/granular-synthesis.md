# Granular Synthesis

*Create textural effects by chopping audio into tiny grains and playing them back*

## What This Does

Creates granular synthesis by capturing audio into a buffer and playing back small chunks (grains) with controllable position and size. Produces everything from subtle textures to dramatic time-stretching and glitched effects.

## Quick Reference

**Essential Parameters:**
- `params[CLOCK_FREQ_PARAM_INDEX]`: Grain size (20-100 samples, controls grain duration)
- `params[SWITCHES_PARAM_INDEX]`: Playback position (0-255, where in buffer to read)
- `params[OPERATOR_1_PARAM_INDEX]`: Grain trigger rate (0-255, how often new grains start)
- `params[OPERAND_1_HIGH_PARAM_INDEX]`: Dry/wet mix (0-255, blend control)

**Key Concepts:** Circular buffering, grain windowing, position control, texture creation

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


global int clock = 0
global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clockFreqLimit = 132300


global array temp_buffer[2]
global int write_pos = 0
global int grain_pos = 0
global int grain_counter = 0
global int grain_trigger = 0
const int BUFFER_SIZE = 2048

function process()
locals int grain_size, int position, int trigger_rate, int mix, int grain_sample_l, int grain_sample_r, int output_l, int output_r, int envelope, int half_size, int read_pos, int offset
{
    loop {

        grain_size = ((int)global params[CLOCK_FREQ_PARAM_INDEX] >> 2) + 20;
        position = (int)global params[SWITCHES_PARAM_INDEX];
        trigger_rate = ((int)global params[OPERATOR_1_PARAM_INDEX] >> 3) + 1;
        mix = (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
        

        if (grain_size > 100) grain_size = 100;
        if (grain_size < 20) grain_size = 20;
        

        global temp_buffer[0] = global signal[0];
        write(global write_pos, 1, global temp_buffer);
        

        global temp_buffer[0] = global signal[1];
        write(global write_pos + BUFFER_SIZE, 1, global temp_buffer);
        

        global grain_trigger = global grain_trigger + 1;
        if (global grain_trigger >= trigger_rate) {
            global grain_trigger = 0;
            

            offset = ((position * (BUFFER_SIZE >> 2)) >> 8) + grain_size;
            global grain_pos = (global write_pos - offset + BUFFER_SIZE) % BUFFER_SIZE;
            global grain_counter = 0;
        }
        

        if (global grain_counter < grain_size) {

            read_pos = (global grain_pos + global grain_counter) % BUFFER_SIZE;
            

            read(read_pos, 1, global temp_buffer);
            grain_sample_l = (int)global temp_buffer[0];
            

            read(read_pos + BUFFER_SIZE, 1, global temp_buffer);
            grain_sample_r = (int)global temp_buffer[0];
            

            half_size = grain_size >> 1;
            if (half_size == 0) half_size = 1;
            
            if (global grain_counter < half_size) {

                envelope = (global grain_counter * 255) / half_size;
            } else {

                envelope = ((grain_size - global grain_counter) * 255) / half_size;
            }
            

            grain_sample_l = (grain_sample_l * envelope) >> 8;
            grain_sample_r = (grain_sample_r * envelope) >> 8;
            global grain_counter = global grain_counter + 1;
        } else {
            grain_sample_l = 0;
            grain_sample_r = 0;
        }
        

        output_l = ((int)global signal[0] * (255 - mix) + grain_sample_l * mix) >> 8;
        output_r = ((int)global signal[1] * (255 - mix) + grain_sample_r * mix) >> 8;
        

        if (output_l > 2047) output_l = 2047;
        if (output_l < -2047) output_l = -2047;
        if (output_r > 2047) output_r = 2047;
        if (output_r < -2047) output_r = -2047;
        

        global signal[0] = output_l;
        global signal[1] = output_r;
        

        global displayLEDs[0] = (grain_size - 20) << 2;
        global displayLEDs[1] = (global grain_counter << 8) / grain_size;
        global displayLEDs[2] = position;
        global displayLEDs[3] = (mix >> 2);
        

        global write_pos = (global write_pos + 1) % BUFFER_SIZE;
        
        yield();
    }
}

```

## How It Works

**Buffer Capture**: Continuously writes incoming audio to a circular buffer using safe memory management with proper bounds checking.

**Grain Generation**: Periodically triggers new grains that read from different positions in the captured buffer using circular buffer arithmetic for safety.

**Triangle Envelope**: Uses a triangle window (0-255 range) to smooth grain edges and prevent clicks, with division-by-zero protection.

**Position Control**: Parameter controls where in the buffer grains are read from, creating time-stretch effects with safe memory addressing.

**Stereo Processing**: Independent left and right channel processing maintains stereo image during granular synthesis.

**Parameter Control**:
- **Control 1**: Grain size (larger = smoother, smaller = more granular)
- **Control 2**: Read position (different timing relationships)
- **Control 3**: Trigger rate (faster = denser texture)
- **Control 4**: Dry/wet mix (blend original with granular)

## Try These Settings

```impala

global params[CLOCK_FREQ_PARAM_INDEX] = 200;
global params[SWITCHES_PARAM_INDEX] = 64;
global params[OPERATOR_1_PARAM_INDEX] = 128;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 128;


global params[CLOCK_FREQ_PARAM_INDEX] = 50;
global params[SWITCHES_PARAM_INDEX] = 200;
global params[OPERATOR_1_PARAM_INDEX] = 32;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;
```

## Try These Changes

- **Reverse grains**: Read grains backwards for different textures
- **Multiple grain voices**: Layer 2-3 grains with different positions
- **Pitch shifting**: Change grain playback speed
- **Stereo granular**: Different grain patterns for left/right channels

## Related Techniques

- **[Make a Delay](make-a-delay.md)**: Buffer management fundamentals
- **[Circular Buffer Guide](../fundamentals/circular-buffer-guide.md)**: Buffer techniques

---
*Part of the [Permut8 Cookbook](../index.md) series*