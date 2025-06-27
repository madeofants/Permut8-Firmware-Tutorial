# MIDI Learn Implementation

## Overview
Enable dynamic MIDI controller assignment, allowing users to assign any MIDI CC to any firmware parameter in real-time without recompiling.

## Core MIDI Learn Structure

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


global array midi_cc_numbers[4]
global array midi_targets[4]
global array midi_active[4]
global int learn_mode = 0
global int learn_target = -1
global int learn_blink = 0

```

## Learn Mode Implementation

```impala

function enter_learn_mode()
locals int target_param
{

    target_param = ((int)global (int)global params[OPERAND_1_LOW_PARAM_INDEX] >> 6);
    
    if (target_param < 4) {
        global learn_mode = 1;
        global learn_target = target_param;
        global learn_blink = 0;
        

        global displayLEDs[0] = 255;
    }
}


function process_midi_learn()
locals int cc_number, int cc_value, int slot
{
    if (global learn_mode == 0 || global learn_target < 0) return;
    

    cc_number = (int)global (int)global params[OPERATOR_2_PARAM_INDEX];
    cc_value = (int)global (int)global params[OPERAND_2_HIGH_PARAM_INDEX];
    

    if (cc_number >= 0 && cc_number <= 127) {

        slot = global learn_target;
        

        global midi_cc_numbers[slot] = cc_number;
        global midi_targets[slot] = global learn_target;
        global midi_active[slot] = 1;
        

        global learn_mode = 0;
        global learn_target = -1;
        

        global displayLEDs[0] = 128;
        global displayLEDs[slot + 1] = 255;
    }
}


function check_learn_triggers()
locals int learn_button
{

    learn_button = (int)global (int)global params[OPERAND_2_LOW_PARAM_INDEX];
    
    if (learn_button > 127 && global learn_mode == 0) {
        enter_learn_mode();
    }
}
```

## MIDI Processing with Learned Mappings

```impala

function handle_midi_cc()
locals int cc_number, int cc_value, int i, int target_param, int scaled_value
{

    cc_number = (int)global (int)global params[OPERATOR_2_PARAM_INDEX];
    cc_value = (int)global (int)global params[OPERAND_2_HIGH_PARAM_INDEX];
    

    if (global learn_mode == 1) {
        process_midi_learn();
        return;
    }
    

    i = 0;
    loop {
        if (i >= 4) break;
        
        if (global midi_active[i] == 1 && global midi_cc_numbers[i] == cc_number) {
            target_param = global midi_targets[i];
            

            scaled_value = cc_value << 1;
            if (scaled_value > 255) scaled_value = 255;
            

            if (target_param >= 0 && target_param < 4) {
                global params[target_param] = scaled_value;
            }
        }
        
        i = i + 1;
    }
}


function clear_midi_mappings()
locals int i
{
    i = 0;
    loop {
        if (i >= 4) break;
        global midi_active[i] = 0;
        global midi_cc_numbers[i] = -1;
        global midi_targets[i] = -1;
        i = i + 1;
    }
    

    global displayLEDs[0] = 64;
}
```

## Advanced Mapping Features

```impala

function apply_parameter_curve()
locals int param_idx, int raw_value, int curved_value
{
    param_idx = 0;
    loop {
        if (param_idx >= 4) break;
        
        raw_value = (int)global params[param_idx];
        


        curved_value = (raw_value * raw_value) >> 8;
        

        global params[param_idx] = curved_value;
        
        param_idx = param_idx + 1;
    }
}


function apply_parameter_inversion()
locals int invert_mask, int param_idx, int value
{

    invert_mask = (int)global (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
    
    param_idx = 0;
    loop {
        if (param_idx >= 4) break;
        

        if ((invert_mask >> param_idx) & 1) {
            value = (int)global params[param_idx];
            global params[param_idx] = 255 - value;
        }
        
        param_idx = param_idx + 1;
    }
}
```

## Complete Audio Processing with MIDI Learn

```impala
function process()
locals int input_sample, int output_sample, int mix_level, int filter_amount, int feedback
{
    loop {

        check_learn_triggers();
        handle_midi_cc();
        

        apply_parameter_curve();
        apply_parameter_inversion();
        

        input_sample = (int)global signal[0];
        mix_level = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];
        filter_amount = (int)global (int)global params[SWITCHES_PARAM_INDEX];
        feedback = (int)global (int)global params[OPERATOR_1_PARAM_INDEX];
        

        output_sample = input_sample;
        

        output_sample = (output_sample * mix_level) >> 8;
        

        if (filter_amount > 0) {
            output_sample = output_sample + ((input_sample - output_sample) >> 3);
        }
        

        if (feedback > 0) {
            output_sample = output_sample + ((output_sample * feedback) >> 10);
        }
        

        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        

        global signal[0] = output_sample;
        global signal[1] = output_sample;
        

        update_learn_display();
        
        yield();
    }
}


function update_learn_display()
locals int i
{
    if (global learn_mode == 1) {

        global learn_blink = global learn_blink + 1;
        if (global learn_blink > 1000) {
            global displayLEDs[0] = (global displayLEDs[0] > 128) ? 64 : 255;
            global learn_blink = 0;
        }
    } else {

        global displayLEDs[0] = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];
        

        i = 0;
        loop {
            if (i >= 3) break;
            if (global midi_active[i] == 1) {
                global displayLEDs[i + 1] = 128;
            } else {
                global displayLEDs[i + 1] = 32;
            }
            i = i + 1;
        }
    }
}
```

## User Interface Guide

### Learning a New Mapping:
1. Set parameter 4 to select which parameter to learn (0-63=param0, 64-127=param1, etc.)
2. Set parameter 7 above 127 to enter learn mode (LED will blink)
3. Send desired MIDI CC via parameters 5 (CC number) and 6 (CC value)
4. Mapping is stored and learn mode exits (LED stops blinking)

### Clearing Mappings:
- Set all parameters to 0 and parameter 7 to 255 to clear all mappings

### Parameter Usage:
- **params[0-3]**: Main audio processing parameters (can be MIDI controlled)
- **(int)global params[OPERAND_1_LOW_PARAM_INDEX]**: Learn target selection (which parameter to learn)
- **(int)global params[OPERATOR_2_PARAM_INDEX]**: Incoming MIDI CC number
- **(int)global params[OPERAND_2_HIGH_PARAM_INDEX]**: Incoming MIDI CC value
- **(int)global params[OPERAND_2_LOW_PARAM_INDEX]**: Learn mode trigger and clear command

## Benefits

**Real-Time Assignment**: Learn MIDI mappings without stopping audio or recompiling firmware.

**Visual Feedback**: LED indicators show learn mode status and active mappings.

**Parameter Curves**: Automatic curve shaping for more musical parameter response.

**Simple Interface**: Uses standard parameter inputs for MIDI data and control.

**Memory Efficient**: Supports 4 simultaneous MIDI mappings with minimal memory usage.

This simplified MIDI learn system provides flexible controller assignment while maintaining Impala language compatibility and real-time performance.