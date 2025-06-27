# Automation Sequencing

*Create automated parameter sequences for dynamic, evolving effects*

## What This Does

Provides step-based automation sequencing for parameters, enabling complex evolving effects and rhythmic parameter modulation. Create sequences of parameter values that play back automatically with internal timing.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Sequence speed (0-255)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Step length (1-16 steps)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Pattern type (0-255)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Sequence enable (>128 = on)

**Core Techniques:**
- **Step sequencing**: Preset parameter values advance over time
- **Pattern programming**: Create rhythmic parameter changes
- **Tempo control**: Adjust sequence playback speed
- **Multi-parameter automation**: Different sequences for different parameters

**Key Concepts:** Step sequencing, automation patterns, rhythmic control, evolving textures

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


global array step_pattern[8]
global int current_step = 0
global int step_counter = 0
global int step_interval = 4410
global int sequence_active = 0

function process()
locals int sequence_speed, int pattern_length, int pattern_type, int sequence_enable, int step_length, int pattern_value, int cutoff_freq, int resonance, int input_sample, int filtered_sample, int output_sample
{
    loop {

        sequence_speed = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];
        pattern_length = ((int)global (int)global params[SWITCHES_PARAM_INDEX] >> 5) + 1;
        pattern_type = (int)global (int)global params[OPERATOR_1_PARAM_INDEX] >> 6;
        sequence_enable = (int)global (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
        

        step_length = 11025 - ((sequence_speed * 10800) >> 8);
        if (step_length < 225) step_length = 225;
        

        if (sequence_enable > 127) {
            global sequence_active = 1;
        } else {
            global sequence_active = 0;
            global current_step = 0;
            global step_counter = 0;
        }
        

        if (pattern_type == 0) {

            global step_pattern[0] = 32;   global step_pattern[1] = 64;
            global step_pattern[2] = 96;   global step_pattern[3] = 128;
            global step_pattern[4] = 160;  global step_pattern[5] = 192;
            global step_pattern[6] = 224;  global step_pattern[7] = 255;
            
        } else if (pattern_type == 1) {

            global step_pattern[0] = 255;  global step_pattern[1] = 64;
            global step_pattern[2] = 255;  global step_pattern[3] = 64;
            global step_pattern[4] = 255;  global step_pattern[5] = 64;
            global step_pattern[6] = 255;  global step_pattern[7] = 64;
            
        } else if (pattern_type == 2) {

            global step_pattern[0] = 128;  global step_pattern[1] = 200;
            global step_pattern[2] = 80;   global step_pattern[3] = 255;
            global step_pattern[4] = 32;   global step_pattern[5] = 180;
            global step_pattern[6] = 150;  global step_pattern[7] = 100;
            
        } else {

            global step_pattern[0] = 255;  global step_pattern[1] = 224;
            global step_pattern[2] = 192;  global step_pattern[3] = 160;
            global step_pattern[4] = 128;  global step_pattern[5] = 96;
            global step_pattern[6] = 64;   global step_pattern[7] = 32;
        }
        

        if (global sequence_active == 1) {
            global step_counter = global step_counter + 1;
            if (global step_counter >= step_length) {
                global step_counter = 0;
                global current_step = global current_step + 1;
                if (global current_step >= pattern_length) {
                    global current_step = 0;
                }
            }
        }
        

        pattern_value = (int)global step_pattern[global current_step];
        

        cutoff_freq = 200 + ((pattern_value * 1800) >> 8);
        resonance = 256 + ((pattern_value * 1280) >> 8);
        

        input_sample = (int)global signal[0];
        

        filtered_sample = cutoff_freq + 
            (((input_sample - cutoff_freq) * resonance) >> 11);
        

        if (filtered_sample > 2047) filtered_sample = 2047;
        if (filtered_sample < -2047) filtered_sample = -2047;
        

        output_sample = filtered_sample;
        if (pattern_value > 200) {

            if (output_sample > 1536) {
                output_sample = 1536 + ((output_sample - 1536) >> 2);
            }
            if (output_sample < -1536) {
                output_sample = -1536 + ((output_sample + 1536) >> 2);
            }
        }
        

        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        

        global signal[0] = output_sample;
        global signal[1] = output_sample;
        

        global displayLEDs[0] = global current_step << 5;
        global displayLEDs[1] = pattern_value;
        global displayLEDs[2] = pattern_type << 6;
        if (global sequence_active == 1) {
            global displayLEDs[3] = 255;
        } else {
            global displayLEDs[3] = 0;
        }
        
        yield();
    }
}

```

## How It Works

**Step Sequencing**: Pre-programmed parameter values advance automatically over time, creating rhythmic parameter changes.

**Pattern Types**: Different mathematical patterns create different musical effects:
- Rising: Gradual build-up
- Alternating: Rhythmic on/off effect
- Random: Unpredictable variation
- Falling: Gradual wind-down

**Timing Control**: Sequence speed parameter controls how fast steps advance. Faster = more rapid changes.

**Pattern Length**: Adjustable from 1-8 steps for different phrase lengths.

**Parameter Control**:
- **Knob 1**: Sequence speed (0-255, fast to slow)
- **Knob 2**: Pattern length (1-8 steps)
- **Knob 3**: Pattern type (0-3 types)
- **Knob 4**: Sequence enable (on/off)

## Try These Settings

```impala

(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;
(int)global params[SWITCHES_PARAM_INDEX] = 64;
(int)global params[OPERATOR_1_PARAM_INDEX] = 64;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 50;
(int)global params[SWITCHES_PARAM_INDEX] = 255;
(int)global params[OPERATOR_1_PARAM_INDEX] = 0;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 128;
(int)global params[SWITCHES_PARAM_INDEX] = 160;
(int)global params[OPERATOR_1_PARAM_INDEX] = 128;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 100;
(int)global params[SWITCHES_PARAM_INDEX] = 100;
(int)global params[OPERATOR_1_PARAM_INDEX] = 100;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 64;
```

## Understanding Automation Sequencing

**Musical Timing**: Sequences create musical phrases and rhythmic interest beyond static parameter settings.

**Pattern Design**: Good patterns have musical logic - rises, falls, repetition, and variation.

**Tempo Relationship**: Sequence timing should relate to musical tempo for best results.

**Parameter Choice**: Different parameters create different musical effects when sequenced.

## Try These Changes

- **Multiple sequences**: Run different patterns on different parameters simultaneously
- **Swing timing**: Add rhythmic swing by varying step lengths
- **Pattern chains**: Link multiple patterns together for longer sequences
- **External sync**: Sync sequence timing to external clock or tempo

## Related Techniques

- **[Parameter Smoothing](parameter-smoothing.md)**: Smooth sequence step transitions
- **[Macro Controls](macro-controls.md)**: Sequence macro parameters for complex changes
- **[MIDI CC Mapping](midi-cc-mapping.md)**: External control of sequence parameters

---
*Part of the [Permut8 Cookbook](../index.md) series*