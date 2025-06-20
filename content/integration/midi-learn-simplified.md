# MIDI Learn Implementation

## Overview
Enable dynamic MIDI controller assignment, allowing users to assign any MIDI CC to any firmware parameter in real-time without recompiling.

## Core MIDI Learn Structure

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

// MIDI Learn mapping storage
global array midi_cc_numbers[4]  // CC numbers for each mapped parameter
global array midi_targets[4]     // Target parameter indices
global array midi_active[4]      // Active mapping flags (0=inactive, 1=active)
global int learn_mode = 0        // Learn mode active flag
global int learn_target = -1     // Parameter being learned (-1 = none)
global int learn_blink = 0       // LED blink counter for learn mode

```

## Learn Mode Implementation

```impala
// Enter learn mode for specific parameter
function enter_learn_mode()
locals int target_param
{
    // Use parameter 4 to select which parameter to learn (0-3)
    target_param = ((int)global (int)global params[OPERAND_1_LOW_PARAM_INDEX] >> 6);  // 0-3 from top 2 bits
    
    if (target_param < 4) {
        global learn_mode = 1;
        global learn_target = target_param;
        global learn_blink = 0;
        
        // Visual feedback - blink LED
        global displayLEDs[0] = 255;
    }
}

// Process MIDI learn when CC received
function process_midi_learn()
locals int cc_number, int cc_value, int slot
{
    if (global learn_mode == 0 || global learn_target < 0) return;
    
    // Read incoming MIDI CC from parameters 5 and 6
    cc_number = (int)global (int)global params[OPERATOR_2_PARAM_INDEX];  // CC number (0-127)
    cc_value = (int)global (int)global params[OPERAND_2_HIGH_PARAM_INDEX];   // CC value (0-127)
    
    // Only process if we have a valid CC
    if (cc_number >= 0 && cc_number <= 127) {
        // Find mapping slot or use the learn target slot
        slot = global learn_target;
        
        // Store mapping
        global midi_cc_numbers[slot] = cc_number;
        global midi_targets[slot] = global learn_target;
        global midi_active[slot] = 1;
        
        // Exit learn mode
        global learn_mode = 0;
        global learn_target = -1;
        
        // Success feedback
        global displayLEDs[0] = 128;
        global displayLEDs[slot + 1] = 255;  // Light up corresponding LED
    }
}

// Check for learn mode triggers
function check_learn_triggers()
locals int learn_button
{
    // Use parameter 7 as learn mode button
    learn_button = (int)global (int)global params[OPERAND_2_LOW_PARAM_INDEX];
    
    if (learn_button > 127 && global learn_mode == 0) {
        enter_learn_mode();
    }
}
```

## MIDI Processing with Learned Mappings

```impala
// Handle incoming MIDI CC messages
function handle_midi_cc()
locals int cc_number, int cc_value, int i, int target_param, int scaled_value
{
    // Read MIDI input from parameters
    cc_number = (int)global (int)global params[OPERATOR_2_PARAM_INDEX];  // CC number
    cc_value = (int)global (int)global params[OPERAND_2_HIGH_PARAM_INDEX];   // CC value (0-127)
    
    // Check if in learn mode first
    if (global learn_mode == 1) {
        process_midi_learn();
        return;
    }
    
    // Process learned mappings
    i = 0;
    loop {
        if (i >= 4) break;
        
        if (global midi_active[i] == 1 && global midi_cc_numbers[i] == cc_number) {
            target_param = global midi_targets[i];
            
            // Scale MIDI value (0-127) to parameter range (0-255)
            scaled_value = cc_value << 1;  // Simple 2x scaling
            if (scaled_value > 255) scaled_value = 255;
            
            // Apply to target parameter
            if (target_param >= 0 && target_param < 4) {
                global params[target_param] = scaled_value;
            }
        }
        
        i = i + 1;
    }
}

// Clear all learned mappings
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
    
    // Clear feedback
    global displayLEDs[0] = 64;  // Clear confirmation
}
```

## Advanced Mapping Features

```impala
// Apply curve shaping to mapped parameters
function apply_parameter_curve()
locals int param_idx, int raw_value, int curved_value
{
    param_idx = 0;
    loop {
        if (param_idx >= 4) break;
        
        raw_value = (int)global params[param_idx];
        
        // Apply exponential curve for more natural feel
        // Using simple square curve: output = input^2 / 255
        curved_value = (raw_value * raw_value) >> 8;  // Square and scale down
        
        // Apply curved value back to parameter
        global params[param_idx] = curved_value;
        
        param_idx = param_idx + 1;
    }
}

// Invert parameter mapping for reverse control
function apply_parameter_inversion()
locals int invert_mask, int param_idx, int value
{
    // Use bits of parameter 3 to control which parameters are inverted
    invert_mask = (int)global (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
    
    param_idx = 0;
    loop {
        if (param_idx >= 4) break;
        
        // Check if this parameter should be inverted
        if ((invert_mask >> param_idx) & 1) {
            value = (int)global params[param_idx];
            global params[param_idx] = 255 - value;  // Invert
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
        // Handle MIDI learn system
        check_learn_triggers();
        handle_midi_cc();
        
        // Apply parameter processing
        apply_parameter_curve();
        apply_parameter_inversion();
        
        // Process audio using learned parameters
        input_sample = (int)global signal[0];
        mix_level = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];      // Can be MIDI controlled
        filter_amount = (int)global (int)global params[SWITCHES_PARAM_INDEX];  // Can be MIDI controlled
        feedback = (int)global (int)global params[OPERATOR_1_PARAM_INDEX];       // Can be MIDI controlled
        
        // Simple effect processing
        output_sample = input_sample;
        
        // Apply mix level
        output_sample = (output_sample * mix_level) >> 8;
        
        // Apply simple filtering
        if (filter_amount > 0) {
            output_sample = output_sample + ((input_sample - output_sample) >> 3);
        }
        
        // Add feedback
        if (feedback > 0) {
            output_sample = output_sample + ((output_sample * feedback) >> 10);
        }
        
        // Prevent clipping
        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        
        // Output processed signal
        global signal[0] = output_sample;
        global signal[1] = output_sample;
        
        // Update LED display
        update_learn_display();
        
        yield();
    }
}

// Visual feedback for learn system
function update_learn_display()
locals int i
{
    if (global learn_mode == 1) {
        // Blink LED during learn mode
        global learn_blink = global learn_blink + 1;
        if (global learn_blink > 1000) {
            global displayLEDs[0] = (global displayLEDs[0] > 128) ? 64 : 255;
            global learn_blink = 0;
        }
    } else {
        // Show mapping status
        global displayLEDs[0] = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];  // Show main parameter
        
        // Show active mappings
        i = 0;
        loop {
            if (i >= 3) break;  // LEDs 1-3
            if (global midi_active[i] == 1) {
                global displayLEDs[i + 1] = 128;  // Dim light for active mapping
            } else {
                global displayLEDs[i + 1] = 32;   // Very dim for inactive
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