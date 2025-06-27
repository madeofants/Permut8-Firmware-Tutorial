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


global int clock
global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clockFreqLimit


global int current_mode = 0
global int last_switch = 0
global int debounce_counter = 0
global int bypass_active = 0

function process()
locals int switch_input, int switch_pressed, int mode_select, int input_sample, int processed_sample, int output_sample, int effect_gain, int switch_state
{
    loop {

        switch_input = (int)global params[CLOCK_FREQ_PARAM_INDEX];
        switch_pressed = 0;
        

        if (switch_input > 127) {
            switch_state = 1;
        } else {
            switch_state = 0;
        }
        

        if (switch_state == global last_switch) {
            global debounce_counter = 0;
        } else {
            global debounce_counter = global debounce_counter + 1;
            if (global debounce_counter >= 5) {
                global last_switch = switch_state;
                global debounce_counter = 0;
                if (switch_state == 1) {
                    switch_pressed = 1;
                }
            }
        }
        

        if (switch_pressed == 1) {
            global current_mode = global current_mode + 1;
            if (global current_mode >= 4) global current_mode = 0;
        }
        

        if ((int)global params[SWITCHES_PARAM_INDEX] > 127) {
            global bypass_active = 1;
        } else {
            global bypass_active = 0;
        }
        

        mode_select = ((int)global params[OPERATOR_1_PARAM_INDEX] * 3) >> 8;
        

        if (mode_select == global current_mode) {

        } else if (switch_pressed == 0) {
            global current_mode = mode_select;
        }
        

        input_sample = (int)global signal[0];
        processed_sample = input_sample;
        

        if (global current_mode == 0) {

            processed_sample = input_sample;
            
        } else if (global current_mode == 1) {

            processed_sample = input_sample + (input_sample >> 2);
            
        } else if (global current_mode == 2) {

            if (input_sample > 1024) {
                processed_sample = 1024 + ((input_sample - 1024) >> 1);
            } else if (input_sample < -1024) {
                processed_sample = -1024 + ((input_sample + 1024) >> 1);
            }
            
        } else {

            processed_sample = (input_sample >> 2) << 2;
        }
        

        if (global bypass_active == 1) {
            output_sample = input_sample;
        } else {
            output_sample = processed_sample;
        }
        

        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        

        global signal[0] = output_sample;
        global signal[1] = output_sample;
        

        global displayLEDs[0] = global current_mode << 6;
        if (global bypass_active == 1) {
            global displayLEDs[1] = 255;
        } else {
            global displayLEDs[1] = 0;
        }
        global displayLEDs[2] = switch_input;
        global displayLEDs[3] = global debounce_counter << 5;
        
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

global params[CLOCK_FREQ_PARAM_INDEX] = 200;
global params[SWITCHES_PARAM_INDEX] = 64;
global params[OPERATOR_1_PARAM_INDEX] = 0;


global params[CLOCK_FREQ_PARAM_INDEX] = 64;
global params[SWITCHES_PARAM_INDEX] = 64;
global params[OPERATOR_1_PARAM_INDEX] = 128;


global params[CLOCK_FREQ_PARAM_INDEX] = 64;
global params[SWITCHES_PARAM_INDEX] = 200;
global params[OPERATOR_1_PARAM_INDEX] = 200;


global params[CLOCK_FREQ_PARAM_INDEX] = 64;
global params[SWITCHES_PARAM_INDEX] = 64;
global params[OPERATOR_1_PARAM_INDEX] = 0;
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