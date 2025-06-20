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

// Circular buffer for delay
global array delay_buffer[128]  // Fixed delay buffer
global int write_pos = 0        // Current write position

function process()
locals int delay_time, int feedback, int wet_mix, int read_pos, int delayed_sample, int feedback_sample, int dry_signal, int wet_signal, int output
{
    loop {
        // Read parameters
        delay_time = ((int)global (int)global params[CLOCK_FREQ_PARAM_INDEX] >> 1) + 1;  // 1-128 delay samples
        feedback = ((int)global (int)global params[SWITCHES_PARAM_INDEX] >> 1);        // 0-127 feedback amount
        wet_mix = ((int)global (int)global params[OPERATOR_1_PARAM_INDEX]);              // 0-255 wet/dry balance
        
        // Calculate read position (look back in time)
        read_pos = global write_pos - delay_time;
        if (read_pos < 0) read_pos = read_pos + 128;    // Wrap negative positions
        
        // Read delayed sample from buffer
        delayed_sample = (int)global delay_buffer[read_pos];
        
        // Create feedback signal (delayed signal fed back into input)
        feedback_sample = (delayed_sample * feedback) >> 7;  // Scale feedback
        
        // Prevent feedback explosion
        if (feedback_sample > 2047) feedback_sample = 2047;
        if (feedback_sample < -2047) feedback_sample = -2047;
        
        // Mix input with feedback and write to buffer
        global delay_buffer[global write_pos] = (int)global signal[0] + feedback_sample;
        
        // Advance write position with wraparound
        global write_pos = global write_pos + 1;
        if (global write_pos >= 128) global write_pos = 0;
        
        // Mix dry and wet signals
        dry_signal = ((int)global signal[0] * (255 - wet_mix)) >> 8;
        wet_signal = (delayed_sample * wet_mix) >> 8;
        output = dry_signal + wet_signal;
        
        // Prevent clipping
        if (output > 2047) output = 2047;
        if (output < -2047) output = -2047;
        
        // Output result
        global signal[0] = output;
        global signal[1] = output;
        
        // Show activity on LEDs
        global displayLEDs[0] = delay_time << 1;      // Show delay time
        global displayLEDs[1] = feedback << 1;       // Show feedback amount
        global displayLEDs[2] = wet_mix;             // Show wet/dry mix
        global displayLEDs[3] = global write_pos << 1; // Show buffer position
        
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
// Short slap-back delay
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 30;   // Short delay
(int)global params[SWITCHES_PARAM_INDEX] = 80;   // Medium feedback
(int)global params[OPERATOR_1_PARAM_INDEX] = 100;  // Mix with dry signal

// Long echo
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;  // Long delay
(int)global params[SWITCHES_PARAM_INDEX] = 120;  // Strong feedback
(int)global params[OPERATOR_1_PARAM_INDEX] = 150;  // More wet signal

// Subtle ambience
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 50;   // Medium delay
(int)global params[SWITCHES_PARAM_INDEX] = 40;   // Light feedback
(int)global params[OPERATOR_1_PARAM_INDEX] = 60;   // Mostly dry

// Self-oscillation (careful!)
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 100;  // Medium delay
(int)global params[SWITCHES_PARAM_INDEX] = 127;  // Maximum feedback
(int)global params[OPERATOR_1_PARAM_INDEX] = 200;  // Heavy wet mix
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