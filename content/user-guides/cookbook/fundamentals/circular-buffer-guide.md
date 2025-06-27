# Circular Buffer Guide

*Essential delay line techniques for audio effects*

## What This Does

Circular buffers enable delay-based audio effects like echo, reverb, and chorus. They use fixed-size memory efficiently by cycling through buffer positions, allowing you to read audio from the past while continuously writing new samples.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Delay time (0-255, controls echo distance)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Feedback amount (0-255, controls echo repetitions)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Wet/dry mix (0-255, dry to wet balance)

**Core Concept:** Write new samples while reading older samples from different positions in the same buffer.

**Key Concepts:** Fixed memory, position wraparound, delay calculation, feedback control

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
global int write_pos = 0

function process()
locals int delay_time, int feedback, int wet_mix, int read_pos, int delayed_sample, int feedback_sample, int dry_signal, int wet_signal, int output
{
    loop {

        delay_time = ((int)global (int)global params[CLOCK_FREQ_PARAM_INDEX] >> 1) + 1;
        feedback = ((int)global (int)global params[SWITCHES_PARAM_INDEX] >> 1);
        wet_mix = ((int)global (int)global params[OPERATOR_1_PARAM_INDEX]);
        

        read_pos = global write_pos - delay_time;
        if (read_pos < 0) read_pos = read_pos + 128;
        

        delayed_sample = (int)global delay_buffer[read_pos];
        

        feedback_sample = (delayed_sample * feedback) >> 7;
        

        if (feedback_sample > 2047) feedback_sample = 2047;
        if (feedback_sample < -2047) feedback_sample = -2047;
        

        global delay_buffer[global write_pos] = (int)global signal[0] + feedback_sample;
        

        global write_pos = global write_pos + 1;
        if (global write_pos >= 128) global write_pos = 0;
        

        dry_signal = ((int)global signal[0] * (255 - wet_mix)) >> 8;
        wet_signal = (delayed_sample * wet_mix) >> 8;
        output = dry_signal + wet_signal;
        

        if (output > 2047) output = 2047;
        if (output < -2047) output = -2047;
        

        global signal[0] = output;
        global signal[1] = output;
        

        global displayLEDs[0] = delay_time << 1;
        global displayLEDs[1] = feedback << 1;
        global displayLEDs[2] = wet_mix;
        global displayLEDs[3] = global write_pos << 1;
        
        yield();
    }
}

```

## How It Works

**Circular Buffer Concept**: A fixed-size array that cycles through positions. When you reach the end, you wrap back to the beginning, creating an infinite loop within limited memory.

**Write Position**: Always advancing forward, marking where new audio gets stored.

**Read Position**: Calculated by looking backward from the write position by the delay amount.

**Wraparound Math**: When positions go negative, add the buffer size to wrap correctly.

**Parameter Control**:
- **Control 1**: Delay time (higher = longer echo)
- **Control 2**: Feedback amount (higher = more repetitions)
- **Control 3**: Wet/dry mix (0 = dry only, 255 = wet only)

## Try These Settings

```impala

(int)global params[CLOCK_FREQ_PARAM_INDEX] = 30;
(int)global params[SWITCHES_PARAM_INDEX] = 80;
(int)global params[OPERATOR_1_PARAM_INDEX] = 100;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;
(int)global params[SWITCHES_PARAM_INDEX] = 120;
(int)global params[OPERATOR_1_PARAM_INDEX] = 150;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 50;
(int)global params[SWITCHES_PARAM_INDEX] = 40;
(int)global params[OPERATOR_1_PARAM_INDEX] = 60;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 100;
(int)global params[SWITCHES_PARAM_INDEX] = 127;
(int)global params[OPERATOR_1_PARAM_INDEX] = 200;
```

## Understanding Delay Effects

**Delay Time**: Controls the gap between original and echoed sound. Shorter delays (1-50ms) create thickness and space. Longer delays (100ms+) create distinct echoes.

**Feedback**: Creates repeating echoes by feeding the delayed signal back into the input. Too much feedback causes runaway oscillation.

**Wet/Dry Mix**: Balances the original (dry) signal with the delayed (wet) signal. Different mixes create different spatial effects.

**Buffer Management**: Fixed memory size limits maximum delay time. Larger buffers = longer possible delays but use more memory.

## Try These Changes

- **Stereo delay**: Use separate buffers for left/right channels with different delay times
- **Filtered feedback**: Add low-pass filtering to the feedback path for warmer repeats
- **Modulated delay**: Vary delay time slowly for chorus/vibrato effects
- **Multi-tap**: Read from multiple positions for complex rhythmic patterns

## Related Techniques

- **[Make a Delay](../audio-effects/make-a-delay.md)**: Complete delay effect implementation
- **[Basic Filter](basic-filter.md)**: Add filtering to feedback paths

---
*Part of the [Permut8 Cookbook](../index.md) series*