# State Recall & External Control

## Overview
Implement state management that allows external systems to save, recall, and synchronize firmware states including parameters, internal variables, and processing modes.

## Core State Structure

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// State management globals
global array saved_params[8]    // Saved parameter values
global int saved_mode = 0       // Saved processing mode
global int current_mode = 0     // Current processing mode
global array param_targets[8]   // Target values for smooth transitions
global array param_steps[8]     // Step sizes for smooth transitions
global int smooth_active = 0    // Smoothing in progress flag
```

## State Capture & Restoration

```impala
// Capture current state
function save_current_state()
locals int i
{
    // Save all parameters
    i = 0;
    loop {
        if (i >= 8) break;
        global saved_params[i] = (int)global params[i];
        i = i + 1;
    }
    
    // Save current mode
    global saved_mode = global current_mode;
    
    // Visual feedback
    global displayLEDs[0] = 255;  // Save confirmation
}

// Restore saved state with smoothing
function restore_saved_state()
locals int i
{
    // Set up smooth parameter transitions
    i = 0;
    loop {
        if (i >= 8) break;
        global param_targets[i] = global saved_params[i];
        global param_steps[i] = (global param_targets[i] - (int)global params[i]) >> 5;  // Smooth over 32 samples
        i = i + 1;
    }
    
    // Restore mode
    global current_mode = global saved_mode;
    global smooth_active = 1;
    
    // Visual feedback
    global displayLEDs[1] = 255;  // Restore confirmation
}

// Update smooth parameter transitions
function update_smooth_transitions()
locals int i, int current, int target, int step
{
    if (global smooth_active == 0) return;
    
    global smooth_active = 0;  // Reset flag, set to 1 if any parameter still smoothing
    
    i = 0;
    loop {
        if (i >= 8) break;
        
        current = (int)global params[i];
        target = global param_targets[i];
        step = global param_steps[i];
        
        if (current != target) {
            // Continue smoothing
            if (step > 0 && current < target) {
                current = current + step;
                if (current > target) current = target;
            } else if (step < 0 && current > target) {
                current = current + step;
                if (current < target) current = target;
            }
            
            global params[i] = current;
            global smooth_active = 1;  // Still smoothing
        }
        
        i = i + 1;
    }
}
```

## External Control Interface

```impala
// Simple state commands via parameter inputs
function handle_state_commands()
locals int save_trigger, int restore_trigger, int param_set_mode
{
    // Read command triggers from higher parameter slots
    save_trigger = (int)global params[6];      // Save state when > 127
    restore_trigger = (int)global params[7];   // Restore state when > 127
    
    // Save state command
    if (save_trigger > 127) {
        save_current_state();
    }
    
    // Restore state command
    if (restore_trigger > 127) {
        restore_saved_state();
    }
    
    // Direct parameter setting mode (params[5] selects which param to set)
    param_set_mode = (int)global params[5];
    if (param_set_mode < 8) {
        // Set specific parameter via external control
        // Value comes from params[4]
        global params[param_set_mode] = (int)global params[4];
    }
}
```

## Multiple State Snapshots

```impala
// Support for 4 state snapshots
global array snapshot_params[32]  // 4 snapshots × 8 parameters
global array snapshot_modes[4]    // Mode for each snapshot
global int current_snapshot = 0   // Currently selected snapshot

function save_to_snapshot()
locals int slot, int base_index, int i
{
    slot = ((int)global params[5] >> 6);  // 0-3 from parameter bits
    if (slot >= 4) return;
    
    base_index = slot * 8;
    
    // Save parameters to snapshot
    i = 0;
    loop {
        if (i >= 8) break;
        global snapshot_params[base_index + i] = (int)global params[i];
        i = i + 1;
    }
    
    // Save mode
    global snapshot_modes[slot] = global current_mode;
    global current_snapshot = slot;
    
    // Visual feedback - show snapshot number
    global displayLEDs[2] = slot << 6;
}

function recall_from_snapshot()
locals int slot, int base_index, int i
{
    slot = ((int)global params[5] >> 6);  // 0-3 from parameter bits
    if (slot >= 4) return;
    
    base_index = slot * 8;
    
    // Set up smooth transitions to snapshot values
    i = 0;
    loop {
        if (i >= 8) break;
        global param_targets[i] = global snapshot_params[base_index + i];
        global param_steps[i] = (global param_targets[i] - (int)global params[i]) >> 5;
        i = i + 1;
    }
    
    // Restore mode
    global current_mode = global snapshot_modes[slot];
    global current_snapshot = slot;
    global smooth_active = 1;
    
    // Visual feedback
    global displayLEDs[3] = slot << 6;
}
```

## Complete Audio Processing with State Management

```impala
function process()
locals int input_sample, int output_sample, int mix_level, int mode_processing
{
    loop {
        // Handle external state commands
        handle_state_commands();
        
        // Update smooth parameter transitions
        update_smooth_transitions();
        
        // Process audio based on current mode
        input_sample = (int)global signal[0];
        mix_level = (int)global params[0];
        
        if (global current_mode == 0) {
            // Mode 0: Clean pass-through
            output_sample = input_sample;
            
        } else if (global current_mode == 1) {
            // Mode 1: Simple gain control
            output_sample = (input_sample * mix_level) >> 8;
            
        } else if (global current_mode == 2) {
            // Mode 2: Basic distortion
            mode_processing = input_sample + (input_sample >> 2);
            output_sample = (mode_processing * mix_level) >> 8;
            
        } else {
            // Mode 3: Bit reduction
            mode_processing = (input_sample >> 2) << 2;
            output_sample = (mode_processing * mix_level) >> 8;
        }
        
        // Prevent clipping
        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        
        // Output processed signal
        global signal[0] = output_sample;
        global signal[1] = output_sample;
        
        // Show state activity on LEDs
        global displayLEDs[0] = mix_level;                    // Main parameter
        global displayLEDs[1] = global current_mode << 6;    // Current mode
        global displayLEDs[2] = global current_snapshot << 6; // Active snapshot
        global displayLEDs[3] = global smooth_active ? 255 : 64; // Smoothing indicator
        
        yield();
    }
}
```

## State Validation & Safety

```impala
// Validate parameter ranges for safety
function validate_and_fix_state()
locals int i, int param_value
{
    i = 0;
    loop {
        if (i >= 8) break;
        
        param_value = (int)global params[i];
        
        // Clamp to valid range
        if (param_value < 0) {
            global params[i] = 0;
        } else if (param_value > 255) {
            global params[i] = 255;
        }
        
        i = i + 1;
    }
    
    // Validate mode
    if (global current_mode < 0) global current_mode = 0;
    if (global current_mode > 3) global current_mode = 0;
}

// Create safe default state
function reset_to_safe_defaults()
locals int i
{
    // Reset all parameters to safe values
    i = 0;
    loop {
        if (i >= 8) break;
        global params[i] = 128;  // Middle values
        i = i + 1;
    }
    
    // Reset mode and state
    global current_mode = 0;
    global current_snapshot = 0;
    global smooth_active = 0;
    
    // Clear all snapshots
    i = 0;
    loop {
        if (i >= 32) break;
        global snapshot_params[i] = 128;
        i = i + 1;
    }
    
    // Visual feedback
    global displayLEDs[0] = 128;  // Default indicator
}
```

## Integration Benefits

**Parameter Smoothing**: Prevents audio clicks during state transitions with gradual parameter changes.

**Multiple Snapshots**: Support for 4 complete state snapshots with instant recall.

**External Control**: Simple parameter-based interface for DAW automation and external controllers.

**Mode Management**: Complete processing mode state included in saved presets.

**Safety Validation**: Automatic parameter range checking and safe default fallbacks.

This simplified state management system provides essential preset functionality while maintaining real-time audio performance and Impala language compatibility.