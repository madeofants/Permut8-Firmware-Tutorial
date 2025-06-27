# State Recall & External Control

## Overview
Implement state management that allows external systems to save, recall, and synchronize firmware states including parameters, internal variables, and processing modes.

## Core State Structure

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


global array saved_params[PARAM_COUNT]
global int saved_mode = 0
global int current_mode = 0
global array param_targets[8]
global array param_steps[8]
global int smooth_active = 0

```

## State Capture & Restoration

```impala

function save_current_state()
locals int i
{

    i = 0;
    loop {
        if (i >= 8) break;
        global saved_params[i] = (int)global params[i];
        i = i + 1;
    }
    

    global saved_mode = global current_mode;
    

    global displayLEDs[0] = 255;
}


function restore_saved_state()
locals int i
{

    i = 0;
    loop {
        if (i >= 8) break;
        global param_targets[i] = global saved_params[i];
        global param_steps[i] = (global param_targets[i] - (int)global params[i]) >> 5;
        i = i + 1;
    }
    

    global current_mode = global saved_mode;
    global smooth_active = 1;
    

    global displayLEDs[1] = 255;
}


function update_smooth_transitions()
locals int i, int current, int target, int step
{
    if (global smooth_active == 0) return;
    
    global smooth_active = 0;
    
    i = 0;
    loop {
        if (i >= 8) break;
        
        current = (int)global params[i];
        target = global param_targets[i];
        step = global param_steps[i];
        
        if (current != target) {

            if (step > 0 && current < target) {
                current = current + step;
                if (current > target) current = target;
            } else if (step < 0 && current > target) {
                current = current + step;
                if (current < target) current = target;
            }
            
            global params[i] = current;
            global smooth_active = 1;
        }
        
        i = i + 1;
    }
}
```

## External Control Interface

```impala

function handle_state_commands()
locals int save_trigger, int restore_trigger, int param_set_mode
{

    save_trigger = (int)global (int)global params[OPERAND_2_HIGH_PARAM_INDEX];
    restore_trigger = (int)global (int)global params[OPERAND_2_LOW_PARAM_INDEX];
    

    if (save_trigger > 127) {
        save_current_state();
    }
    

    if (restore_trigger > 127) {
        restore_saved_state();
    }
    

    param_set_mode = (int)global (int)global params[OPERATOR_2_PARAM_INDEX];
    if (param_set_mode < 8) {


        global params[param_set_mode] = (int)global (int)global params[OPERAND_1_LOW_PARAM_INDEX];
    }
}
```

## Multiple State Snapshots

```impala

global array snapshot_params[32]
global array snapshot_modes[4]
global int current_snapshot = 0

function save_to_snapshot()
locals int slot, int base_index, int i
{
    slot = ((int)global (int)global params[OPERATOR_2_PARAM_INDEX] >> 6);
    if (slot >= 4) return;
    
    base_index = slot * 8;
    

    i = 0;
    loop {
        if (i >= 8) break;
        global snapshot_params[base_index + i] = (int)global params[i];
        i = i + 1;
    }
    

    global snapshot_modes[slot] = global current_mode;
    global current_snapshot = slot;
    

    global displayLEDs[2] = slot << 6;
}

function recall_from_snapshot()
locals int slot, int base_index, int i
{
    slot = ((int)global (int)global params[OPERATOR_2_PARAM_INDEX] >> 6);
    if (slot >= 4) return;
    
    base_index = slot * 8;
    

    i = 0;
    loop {
        if (i >= 8) break;
        global param_targets[i] = global snapshot_params[base_index + i];
        global param_steps[i] = (global param_targets[i] - (int)global params[i]) >> 5;
        i = i + 1;
    }
    

    global current_mode = global snapshot_modes[slot];
    global current_snapshot = slot;
    global smooth_active = 1;
    

    global displayLEDs[3] = slot << 6;
}
```

## Complete Audio Processing with State Management

```impala
function process()
locals int input_sample, int output_sample, int mix_level, int mode_processing
{
    loop {

        handle_state_commands();
        

        update_smooth_transitions();
        

        input_sample = (int)global signal[0];
        mix_level = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];
        
        if (global current_mode == 0) {

            output_sample = input_sample;
            
        } else if (global current_mode == 1) {

            output_sample = (input_sample * mix_level) >> 8;
            
        } else if (global current_mode == 2) {

            mode_processing = input_sample + (input_sample >> 2);
            output_sample = (mode_processing * mix_level) >> 8;
            
        } else {

            mode_processing = (input_sample >> 2) << 2;
            output_sample = (mode_processing * mix_level) >> 8;
        }
        

        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        

        global signal[0] = output_sample;
        global signal[1] = output_sample;
        

        global displayLEDs[0] = mix_level;
        global displayLEDs[1] = global current_mode << 6;
        global displayLEDs[2] = global current_snapshot << 6;

        if (global smooth_active) {
            global displayLEDs[3] = 255;
        } else {
            global displayLEDs[3] = 64;
        }
        
        yield();
    }
}
```

## State Validation & Safety

```impala

function validate_and_fix_state()
locals int i, int param_value
{
    i = 0;
    loop {
        if (i >= 8) break;
        
        param_value = (int)global params[i];
        

        if (param_value < 0) {
            global params[i] = 0;
        } else if (param_value > 255) {
            global params[i] = 255;
        }
        
        i = i + 1;
    }
    

    if (global current_mode < 0) global current_mode = 0;
    if (global current_mode > 3) global current_mode = 0;
}


function reset_to_safe_defaults()
locals int i
{

    i = 0;
    loop {
        if (i >= 8) break;
        global params[i] = 128;
        i = i + 1;
    }
    

    global current_mode = 0;
    global current_snapshot = 0;
    global smooth_active = 0;
    

    i = 0;
    loop {
        if (i >= 32) break;
        global snapshot_params[i] = 128;
        i = i + 1;
    }
    

    global displayLEDs[0] = 128;
}
```

## Integration Benefits

**Parameter Smoothing**: Prevents audio clicks during state transitions with gradual parameter changes.

**Multiple Snapshots**: Support for 4 complete state snapshots with instant recall.

**External Control**: Simple parameter-based interface for DAW automation and external controllers.

**Mode Management**: Complete processing mode state included in saved presets.

**Safety Validation**: Automatic parameter range checking and safe default fallbacks.

This simplified state management system provides essential preset functionality while maintaining real-time audio performance and Impala language compatibility.