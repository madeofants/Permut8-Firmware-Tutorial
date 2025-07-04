# Memory Basics

*Essential memory management techniques for Permut8 firmware development*

## What This Does

Memory management is fundamental for reliable firmware development. This covers efficient data organization, circular buffers for delays, lookup tables for fast math, and safe array access patterns.

## Quick Reference

**Essential Memory Areas:**
- `params[]`: Real-time controls (0-255, 8 parameters)
- `signal[]`: Audio I/O (-2047 to 2047, stereo)
- `global arrays`: Custom data storage
- `displayLEDs[]`: Visual feedback (0-255, 4 LEDs)

**Core Techniques:**
- **Circular buffers**: Wrap-around indexing for delays
- **Lookup tables**: Pre-calculated values for fast math
- **Bounds checking**: Prevent crashes from array overruns
- **State management**: Track processing state over time

**Key Concepts:** Static allocation, circular indexing, bounds safety, memory efficiency

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


global array delay_buffer[128]
global array sine_table[64]
global int write_pos = 0
global int state_counter = 0

function process()
locals int delay_time, int read_pos, int feedback, int input_sample, int delayed_sample, int output_sample, int oscillator_phase, int sine_value, int wet_amount, int dry_amount, int feedback_signal
{
    loop {

        delay_time = ((int)global (int)global params[CLOCK_FREQ_PARAM_INDEX] >> 1) + 1;
        feedback = (int)global (int)global params[SWITCHES_PARAM_INDEX];
        wet_amount = (int)global (int)global params[OPERATOR_1_PARAM_INDEX];
        

        input_sample = (int)global signal[0];
        

        read_pos = global write_pos - delay_time;
        if (read_pos < 0) read_pos = read_pos + 128;
        

        delayed_sample = (int)global delay_buffer[read_pos];
        

        delayed_sample = (delayed_sample * feedback) >> 8;
        

        feedback_signal = input_sample + delayed_sample;
        

        if (feedback_signal > 2047) feedback_signal = 2047;
        if (feedback_signal < -2047) feedback_signal = -2047;
        

        global delay_buffer[global write_pos] = feedback_signal;
        

        global write_pos = global write_pos + 1;
        if (global write_pos >= 128) global write_pos = 0;
        

        oscillator_phase = (global state_counter >> 4) & 63;
        sine_value = (int)global sine_table[oscillator_phase];
        

        dry_amount = 255 - wet_amount;
        output_sample = ((input_sample * dry_amount) + (delayed_sample * wet_amount)) >> 8;
        

        output_sample = output_sample + ((sine_value * 200) >> 11);
        

        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        

        global signal[0] = output_sample;
        global signal[1] = output_sample;
        

        global state_counter = global state_counter + 1;
        if (global state_counter >= 4096) global state_counter = 0;
        

        global displayLEDs[0] = global write_pos << 1;
        global displayLEDs[1] = delay_time << 1;
        global displayLEDs[2] = feedback;
        global displayLEDs[3] = oscillator_phase << 2;
        
        yield();
    }
}


function init_sine_table()
locals int i, int angle, int sine_sample
{
    i = 0;
    loop {
        if (i >= 64) break;
        


        if (i < 16) {
            sine_sample = i << 7;
        } else if (i < 32) {
            sine_sample = 2047 - ((i - 16) << 7);
        } else if (i < 48) {
            sine_sample = -((i - 32) << 7);
        } else {
            sine_sample = -2047 + ((i - 48) << 7);
        }
        

        global sine_table[i] = sine_sample;
        i = i + 1;
    }
}

```

## How It Works

**Circular Buffers**: Use modulo arithmetic or manual wraparound to create endless loops. Essential for delays and oscillators.

**Lookup Tables**: Pre-calculate expensive math (sine, logarithms) and store in arrays for fast access during audio processing.

**Bounds Checking**: Always validate array indices before access. Use clamping or modulo to stay within safe ranges.

**State Management**: Track processing state over time using counters and flags. Essential for oscillators and sequencers.

**Parameter Control**:
- **Control 1**: Delay time (1-128 samples)
- **Control 2**: Feedback amount (0-255)
- **Control 3**: Wet/dry mix (0-255)

## Try These Settings

```impala

(int)global params[CLOCK_FREQ_PARAM_INDEX] = 32;
(int)global params[SWITCHES_PARAM_INDEX] = 128;
(int)global params[OPERATOR_1_PARAM_INDEX] = 100;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;
(int)global params[SWITCHES_PARAM_INDEX] = 64;
(int)global params[OPERATOR_1_PARAM_INDEX] = 150;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 8;
(int)global params[SWITCHES_PARAM_INDEX] = 200;
(int)global params[OPERATOR_1_PARAM_INDEX] = 80;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 255;
(int)global params[SWITCHES_PARAM_INDEX] = 180;
(int)global params[OPERATOR_1_PARAM_INDEX] = 120;
```

## Understanding Memory Management

**Static Allocation**: All arrays declared at compile time. No malloc/free - everything is pre-allocated.

**Circular Indexing**: Essential pattern for audio processing. Write position advances continuously, read position follows at a distance.

**Table Lookup**: Trade memory for speed. Store pre-calculated values instead of computing during audio processing.

**Memory Safety**: Always check bounds before array access. Use clamping or modulo arithmetic to stay safe.

## Try These Changes

- **Variable delay**: Smoothly change delay time without clicks
- **Stereo delays**: Independent left/right delay times
- **Multi-tap delays**: Multiple read positions from same buffer
- **Wavetable oscillator**: Store multiple waveforms in lookup tables

## Related Techniques

- **[Circular Buffer Guide](#circular-buffer-guide)**: Advanced circular buffer techniques
- **[Basic Oscillator](#basic-oscillator)**: Wavetable synthesis with lookup tables
- **[Parameter Mapping](#parameter-mapping)**: Efficient parameter scaling

---
*Part of the [Permut8 Cookbook](#permut8-cookbook) series*