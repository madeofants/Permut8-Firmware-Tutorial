# Switches and Modes

*Essential discrete control patterns for professional audio interfaces*

## What This Does

Switches and modes provide discrete control options that complement continuous parameters. Users can select different processing algorithms, toggle features, and navigate through configurations.

## Quick Reference

**Essential Parameters:**
- `params[CLOCK_FREQ_PARAM_INDEX-OPERAND_2_LOW_PARAM_INDEX]`: Switch inputs (0-127=off, 128-255=on)
- `mode_count`: Number of available states
- `current_mode`: Active processing mode
- `last_switch`: Previous switch state (for edge detection)

**Core Techniques:**
- **Switch reading**: Convert 0-255 parameter to binary state
- **Edge detection**: Trigger on switch press (not hold)
- **Mode cycling**: Advance through multiple states
- **Debouncing**: Prevent false triggers from noisy switches

**Key Concepts:** State machines, edge detection, mode selection, stable switching

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
global array params[PARAM_COUNT] // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Switch and mode state
global int current_mode = 0     // Active processing mode (0-3)
global int last_switch = 0      // Previous switch state
global int debounce_counter = 0 // Stability counter
global int bypass_active = 0    // Effect bypass state

function process()
locals int switch_input, int switch_pressed, int mode_select, int input_sample, int processed_sample, int output_sample, int effect_gain, int switch_state
{
    loop {
        // Read mode switch with debouncing
        switch_input = (int)global params[CLOCK_FREQ_PARAM_INDEX];
        switch_pressed = 0;
        
        // Convert parameter to binary switch state
        if (switch_input > 127) {
            switch_state = 1;
        } else {
            switch_state = 0;
        }
        
        // Debounce switch input for stability
        if (switch_state == global last_switch) {
            global debounce_counter = 0;
        } else {
            global debounce_counter = global debounce_counter + 1;
            if (global debounce_counter >= 5) {  // 5 samples stable
                global last_switch = switch_state;
                global debounce_counter = 0;
                if (switch_state == 1) {
                    switch_pressed = 1;  // Rising edge detected
                }
            }
        }
        
        // Advance mode on switch press
        if (switch_pressed == 1) {
            global current_mode = global current_mode + 1;
            if (global current_mode >= 4) global current_mode = 0;  // Cycle 0-3
        }
        
        // Read bypass switch from second parameter
        if ((int)global params[SWITCHES_PARAM_INDEX] > 127) {
            global bypass_active = 1;
        } else {
            global bypass_active = 0;
        }
        
        // Read mode selection from third parameter (direct select)
        mode_select = ((int)global params[OPERATOR_1_PARAM_INDEX] * 3) >> 8;  // 0-255 → 0-3
        
        // Use direct mode select if different from current mode
        if (mode_select == global current_mode) {
            // Do nothing - same mode
        } else if (switch_pressed == 0) {
            global current_mode = mode_select;
        }
        
        // Read input sample
        input_sample = (int)global signal[0];
        processed_sample = input_sample;
        
        // Process based on current mode
        if (global current_mode == 0) {
            // Mode 0: Clean signal (no processing)
            processed_sample = input_sample;
            
        } else if (global current_mode == 1) {
            // Mode 1: Simple gain boost
            processed_sample = input_sample + (input_sample >> 2);  // +25% gain
            
        } else if (global current_mode == 2) {
            // Mode 2: Soft distortion
            if (input_sample > 1024) {
                processed_sample = 1024 + ((input_sample - 1024) >> 1);
            } else if (input_sample < -1024) {
                processed_sample = -1024 + ((input_sample + 1024) >> 1);
            }
            
        } else {
            // Mode 3: Bit reduction
            processed_sample = (input_sample >> 2) << 2;  // 4-bit quantization
        }
        
        // Apply bypass switching
        if (global bypass_active == 1) {
            output_sample = input_sample;  // Bypass: clean signal
        } else {
            output_sample = processed_sample;  // Effect: processed signal
        }
        
        // Prevent clipping
        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        
        // Output processed signal
        global signal[0] = output_sample;
        global signal[1] = output_sample;
        
        // Display current mode and bypass state on LEDs
        global displayLEDs[0] = global current_mode << 6;     // Mode indicator
        if (global bypass_active == 1) {
            global displayLEDs[1] = 255;  // Bypass on
        } else {
            global displayLEDs[1] = 0;    // Bypass off
        }
        global displayLEDs[2] = switch_input;                 // Switch level
        global displayLEDs[3] = global debounce_counter << 5; // Debounce activity
        
        yield();
    }
}
```

## How It Works

**Switch Reading**: Parameters 0-255 are split at 127. Values 0-127 = switch off, 128-255 = switch on.

**Edge Detection**: Only trigger mode changes on the rising edge (off→on transition), not while held down.

**Debouncing**: Wait for 5 stable samples before accepting switch state change. Prevents noise from triggering false switches.

**Mode Selection**: Two methods - button cycling (advances through modes) or direct parameter selection (knob selects mode).

**Parameter Control**:
- **Control 1**: Mode advance button (press to cycle)
- **Control 2**: Bypass switch (on/off)
- **Control 3**: Direct mode select (0-255 → mode 0-3)

## Try These Settings

```impala
// Mode cycling with button
params[CLOCK_FREQ_PARAM_INDEX] = 200;  // Button pressed
params[SWITCHES_PARAM_INDEX] = 64;   // Bypass off
params[OPERATOR_1_PARAM_INDEX] = 0;    // Direct select off

// Direct mode selection
params[CLOCK_FREQ_PARAM_INDEX] = 64;   // Button not pressed
params[SWITCHES_PARAM_INDEX] = 64;   // Bypass off
params[OPERATOR_1_PARAM_INDEX] = 128;  // Select mode 1

// Bypass active
params[CLOCK_FREQ_PARAM_INDEX] = 64;   // Button not pressed
params[SWITCHES_PARAM_INDEX] = 200;  // Bypass on
params[OPERATOR_1_PARAM_INDEX] = 200;  // Any mode

// Clean signal
params[CLOCK_FREQ_PARAM_INDEX] = 64;   // Button not pressed
params[SWITCHES_PARAM_INDEX] = 64;   // Bypass off
params[OPERATOR_1_PARAM_INDEX] = 0;    // Mode 0 (clean)
```

## Understanding Switch Control

**Binary Switching**: Parameters naturally split into two ranges - low values (off) and high values (on).

**Edge vs Level**: Edge detection triggers once per press. Level detection responds continuously while held.

**Debouncing**: Real switches bounce between states. Software debouncing ensures clean transitions.

**Mode Management**: State machines track current mode and respond to control inputs consistently.

## Try These Changes

- **Multi-switch modes**: Use combinations of switches for more options
- **Long press detection**: Different actions for short vs long button presses
- **Switch combinations**: Hold one switch while pressing another
- **Mode memory**: Remember selected mode across power cycles

## Related Techniques

- **[Parameter Mapping](#parameter-mapping)**: Map switch positions to useful ranges
- **[Level Metering](#level-metering)**: Visual feedback for switch states
- **[Basic Filter](#basic-filter)**: Switch between filter types

---
*Part of the [Permut8 Cookbook](#permut8-cookbook) series*