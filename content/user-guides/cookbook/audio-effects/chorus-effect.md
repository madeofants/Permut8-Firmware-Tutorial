# Chorus Effect

## What This Does
Creates a lush, thickening effect by adding multiple modulated delay lines that simulate the natural variations when multiple musicians play the same part. Produces everything from subtle doubling to swirling chorus textures.

## Quick Reference
**Parameters**:
- **Control 1 (params[OPERAND_1_HIGH_PARAM_INDEX])**: LFO rate (0.1Hz to 5Hz, controls sweep speed)
- **Control 2 (params[OPERAND_1_LOW_PARAM_INDEX])**: Modulation depth (0-255, controls pitch variation amount)
- **Control 3 (params[OPERATOR_2_PARAM_INDEX])**: Dry/wet mix (0% = dry signal, 100% = full chorus)
- **Control 4 (params[OPERAND_2_HIGH_PARAM_INDEX])**: Stereo spread (0 = mono, 255 = maximum width)

**Key Concepts**: Multiple delay lines, LFO modulation, stereo imaging, interpolation

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
global int lfo_phase = 0
global int lfo_phase_r = 64
const int MAX_DELAY_BUFFER = 200

function process()
locals int rate, int depth, int mix, int spread, int delay_time_l, int delay_time_r, int lfo_val_l, int lfo_val_r, int delayed_sample_l, int delayed_sample_r, int output_l, int output_r, int read_pos_l, int read_pos_r
{
    loop {

        rate = ((int)global params[OPERAND_1_HIGH_PARAM_INDEX] >> 4) + 1;
        depth = ((int)global params[OPERAND_1_LOW_PARAM_INDEX] >> 3) + 1;
        mix = (int)global params[OPERATOR_2_PARAM_INDEX];
        spread = (int)global params[OPERAND_2_HIGH_PARAM_INDEX];
        

        global lfo_phase = (global lfo_phase + rate) & 255;
        if (global lfo_phase < 128) {
            lfo_val_l = global lfo_phase;
        } else {
            lfo_val_l = 255 - global lfo_phase;
        }
        

        global lfo_phase_r = (global lfo_phase_r + rate) & 255;
        if (global lfo_phase_r < 128) {
            lfo_val_r = global lfo_phase_r;
        } else {
            lfo_val_r = 255 - global lfo_phase_r;
        }
        

        lfo_val_r = lfo_val_l + ((lfo_val_r - lfo_val_l) * spread >> 8);
        

        delay_time_l = 25 + ((lfo_val_l * depth) >> 7);
        delay_time_r = 25 + ((lfo_val_r * depth) >> 7);
        if (delay_time_l > 100) delay_time_l = 100;
        if (delay_time_r > 100) delay_time_r = 100;
        

        global temp_buffer[0] = global signal[0];
        write(global write_pos, 1, global temp_buffer);
        global temp_buffer[0] = global signal[1];
        write(global write_pos + MAX_DELAY_BUFFER, 1, global temp_buffer);
        

        read_pos_l = (global write_pos - delay_time_l + MAX_DELAY_BUFFER) % MAX_DELAY_BUFFER;
        read_pos_r = (global write_pos - delay_time_r + MAX_DELAY_BUFFER) % MAX_DELAY_BUFFER;
        
        read(read_pos_l, 1, global temp_buffer);
        delayed_sample_l = (int)global temp_buffer[0];
        
        read(read_pos_r + MAX_DELAY_BUFFER, 1, global temp_buffer);
        delayed_sample_r = (int)global temp_buffer[0];
        

        output_l = ((int)global signal[0] * (255 - mix) + delayed_sample_l * mix) >> 8;
        output_r = ((int)global signal[1] * (255 - mix) + delayed_sample_r * mix) >> 8;
        

        if (output_l > 2047) output_l = 2047;
        if (output_l < -2047) output_l = -2047;
        if (output_r > 2047) output_r = 2047;
        if (output_r < -2047) output_r = -2047;
        

        global signal[0] = output_l;
        global signal[1] = output_r;
        

        global displayLEDs[0] = lfo_val_l;
        global displayLEDs[1] = lfo_val_r;
        

        global write_pos = (global write_pos + 1) % MAX_DELAY_BUFFER;
        
        yield();
    }
}

```

## Try These Changes
- **More voices**: Add additional delay lines (4-6 voices) for thicker, more complex chorus
- **Vintage chorus**: Reduce LFO rate and increase depth for classic 80s ensemble sounds
- **Ensemble mode**: Use very short delays (5-15 samples) with subtle modulation for string ensemble
- **Tremolo chorus**: Modulate amplitude as well as delay time for animated effects
- **Custom LFO shapes**: Replace triangle wave with sawtooth for different movement character

## How It Works
Chorus creates the illusion of multiple performers by using short delay lines (8-40ms) with delay times modulated by Low Frequency Oscillators (LFOs) at different phases for left and right channels. This simulates the natural pitch and timing variations that occur when multiple musicians play together.

The key elements are: modulated delay times that create subtle pitch variations through Doppler-like effects, stereo spread control that offsets the LFO phases between channels for width, and proper circular buffer management for stable operation. The triangle wave LFO provides smooth, musical modulation that avoids harsh artifacts.

The stereo implementation uses separate LFO phases for each channel, with the stereo spread parameter controlling how much the right channel differs from the left, creating natural chorus width and movement.

## Related Techniques
- **[Make a Delay](make-a-delay.md)**: Basic delay implementation fundamentals
- **[Phaser Effect](#phaser-effect)**: Related modulation-based effect
- **[Stereo Processing](#stereo-processing)**: Stereo width and panning

---
*Part of the [Permut8 Cookbook](#permut8-cookbook) series*