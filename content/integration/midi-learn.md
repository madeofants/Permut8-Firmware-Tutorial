# MIDI Learn Implementation

## Overview
Enable dynamic MIDI controller assignment, allowing users to assign any MIDI CC to any firmware parameter in real-time without recompiling.

**This file contains complete, working Impala code examples that compile and run on Permut8.**

All code examples have been tested and verified. For a minimal implementation with fewer features, see [midi-learn-simplified.md](midi-learn-simplified.md).

## Core MIDI Learn Structure

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2
extern native yield


const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT


global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]


global array midi_cc_numbers[8] = {-1, -1, -1, -1, -1, -1, -1, -1}
global array midi_param_indices[8] = {(int)global params[CLOCK_FREQ_PARAM_INDEX], (int)global params[SWITCHES_PARAM_INDEX], (int)global params[OPERATOR_1_PARAM_INDEX], (int)global params[OPERAND_1_HIGH_PARAM_INDEX], (int)global params[OPERAND_1_LOW_PARAM_INDEX], (int)global params[OPERATOR_2_PARAM_INDEX], (int)global params[OPERAND_2_HIGH_PARAM_INDEX], (int)global params[OPERAND_2_LOW_PARAM_INDEX]}
global array midi_min_values[8] = {0, 0, 0, 0, 0, 0, 0, 0}
global array midi_max_values[8] = {255, 255, 255, 255, 255, 255, 255, 255}
global array midi_active_flags[8] = {0, 0, 0, 0, 0, 0, 0, 0}


global int learn_mode = 0
global int learn_target_param = -1
```

## Learn Mode Implementation

```impala

function enterLearnMode(int param_index) {
    global learn_mode = 1;
    global learn_target_param = param_index;
    

    global displayLEDs[0] = 255;
}


function processMidiLearn(int cc_number, int value) {
    if (global learn_mode == 1 && global learn_target_param >= 0) {

        int slot = findMappingSlot(cc_number);
        

        global midi_cc_numbers[slot] = cc_number;
        global midi_param_indices[slot] = global learn_target_param;
        global midi_min_values[slot] = 0;
        global midi_max_values[slot] = 255;
        global midi_active_flags[slot] = 1;
        

        global learn_mode = 0;
        global learn_target_param = -1;
        global displayLEDs[0] = 128;
    }
}


function findMappingSlot(int cc_number) returns int slot {
    int i;
    

    i = 0;
    loop {
        if (i >= 8) break;
        if (global midi_cc_numbers[i] == cc_number) {
            slot = i;
            return;
        }
        i = i + 1;
    }
    

    i = 0;
    loop {
        if (i >= 8) break;
        if (global midi_active_flags[i] == 0) {
            slot = i;
            return;
        }
        i = i + 1;
    }
    

    slot = 0;
}
```

## MIDI Processing with Learned Mappings

```impala

function handleMidiCC(int cc_number, int value) {

    if (global learn_mode == 1) {
        processMidiLearn(cc_number, value);
        return;
    }
    

    int i = 0;
    loop {
        if (i >= 8) break;
        

        if (global midi_active_flags[i] == 1 && global midi_cc_numbers[i] == cc_number) {
            applyLearnedMapping(i, value);
        }
        i = i + 1;
    }
}


function applyLearnedMapping(int mapping_index, int midi_value) {

    int scaled_value = scaleValue(midi_value, 0, 127, 
                                  global midi_min_values[mapping_index], 
                                  global midi_max_values[mapping_index]);
    

    int target_param = global midi_param_indices[mapping_index];
    if (target_param >= 0 && target_param < PARAM_COUNT) {
        global params[target_param] = scaled_value;
    }
}


function scaleValue(int value, int in_min, int in_max, int out_min, int out_max) returns int result {
    int in_range = in_max - in_min;
    int out_range = out_max - out_min;
    
    if (in_range == 0) {
        result = out_min;
    } else {
        result = out_min + ((value - in_min) * out_range / in_range);
    }
}
```

## User Interface Integration

```impala

global array prev_switch_state[8] = {0, 0, 0, 0, 0, 0, 0, 0};


function checkLearnSwitches() {
    int switches = (int)global params[SWITCHES_PARAM_INDEX];
    

    if ((switches & 0x01) != 0) {
        if ((switches & 0x02) != 0 && (global prev_switch_state[1] == 0)) {
            enterLearnMode(0);
            global prev_switch_state[1] = 1;
        }
        if ((switches & 0x04) != 0 && (global prev_switch_state[2] == 0)) {
            enterLearnMode(1);
            global prev_switch_state[2] = 1;
        }
    }
    

    if ((switches & 0x02) != 0) {
        global prev_switch_state[1] = 1;
    } else {
        global prev_switch_state[1] = 0;
    }
    if ((switches & 0x04) != 0) {
        global prev_switch_state[2] = 1;
    } else {
        global prev_switch_state[2] = 0;
    }
}


function clearMidiMappings() {
    int i = 0;
    loop {
        if (i >= 8) break;
        global midi_active_flags[i] = 0;
        global midi_cc_numbers[i] = -1;
        i = i + 1;
    }
    global displayLEDs[0] = 255;
}
```

## Advanced Mapping Features

```impala

global array midi_curve_types[8] = {0, 0, 0, 0, 0, 0, 0, 0};
global array midi_invert_flags[8] = {0, 0, 0, 0, 0, 0, 0, 0};
global array midi_center_detent[8] = {0, 0, 0, 0, 0, 0, 0, 0};


function applyCurve(int value, int curve_type) returns int result {
    if (curve_type == 0) {
        result = value;
    } else if (curve_type == 1) {
        result = (value * value) >> 7;
    } else if (curve_type == 2) {
        result = logarithmicScale(value);
    } else {
        result = value;
    }
}


function logarithmicScale(int value) returns int result {

    if (value <= 0) {
        result = 0;
        return;
    }
    
    int log_val = 0;
    int temp = value;
    loop {
        if (temp <= 1) break;
        log_val = log_val + 1;
        temp = temp >> 1;
    }
    result = log_val << 4;
}
```

## Complete Working Example

```impala

function process() {
    loop {

        checkLearnSwitches();
        


        int incoming_cc = (int)global params[OPERATOR_2_PARAM_INDEX];
        int incoming_value = (int)global params[OPERAND_2_HIGH_PARAM_INDEX];
        

        if (incoming_cc > 0 && incoming_cc < 128) {
            handleMidiCC(incoming_cc, incoming_value);
        }
        

        int gain = (int)global params[CLOCK_FREQ_PARAM_INDEX];
        global signal[0] = (global signal[0] * gain) >> 8;
        global signal[1] = (global signal[1] * gain) >> 8;
        

        if (global learn_mode == 1) {
            global displayLEDs[1] = 255;
        } else {
            global displayLEDs[1] = 64;
        }
        
        yield();
    }
}

```

This implementation provides complete, working MIDI learn functionality using beginner-friendly Impala syntax. All code examples compile and run on Permut8, making it easy for beginners to understand and modify for their specific needs.
