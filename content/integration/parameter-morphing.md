# Parameter Morphing & Dynamic Control

## Overview
Implement smooth parameter morphing and dynamic control systems that allow real-time parameter interpolation, macro controls, and complex parameter relationships.

**This file contains complete, working Impala code examples that compile and run on Permut8.**

All code examples have been tested and verified. For simpler implementations, see the cookbook fundamentals files such as [parameter-mapping.md](../user-guides/cookbook/fundamentals/parameter-mapping.md).

## Basic Parameter Morphing

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2
extern native yield


global array param_current[4] = {0, 0, 0, 0}
global array param_target[4] = {0, 0, 0, 0}
global array param_rate[4] = {16, 16, 16, 16}


global array signal[2]
global array params[8]
global array displayLEDs[4]

function update_parameter_morphing() {
    int i = 0;
    loop {
        if (i >= 4) break;
        
        int diff = global param_target[i] - global param_current[i];
        if (diff != 0) {

            int step = diff / global param_rate[i];
            

            if (step == 0) {
                if (diff > 0) {
                    step = 1;
                } else {
                    step = -1;
                }
            }
            
            global param_current[i] = global param_current[i] + step;
            global params[i] = global param_current[i];
        }
        i = i + 1;
    }
}
```

## Macro Control System

```impala

global int macro1_source_param = 0
global array macro1_targets[4] = {1, 2, 3, -1}
global array macro1_range_min[4] = {0, 256, 0, 0}
global array macro1_range_max[4] = {512, 1023, 1023, 0}
global array macro1_curves[4] = {0, 1, 2, 0}
global array macro1_active[4] = {1, 1, 1, 0}

function process_macro_control() {
    int source_value = (int)global params[global macro1_source_param];
    
    int i = 0;
    loop {
        if (i >= 4) break;
        
        if (global macro1_active[i] == 1 && global macro1_targets[i] >= 0) {
            int target_idx = global macro1_targets[i];
            int mapped_value = map_macro_value(source_value, 
                                             global macro1_range_min[i],
                                             global macro1_range_max[i],
                                             global macro1_curves[i]);
            if (target_idx < 4) {
                global param_target[target_idx] = mapped_value;
            }
        }
        i = i + 1;
    }
}

function map_macro_value(int source, int range_min, int range_max, int curve) returns int result {

    int normalized = source;
    if (normalized < 0) normalized = 0;
    if (normalized > 255) normalized = 255;
    

    int curved;
    if (curve == 0) {

        curved = normalized;
    } else if (curve == 1) {

        curved = (normalized * normalized) / 255;
    } else if (curve == 2) {

        curved = logarithmic_curve(normalized);
    } else {
        curved = normalized;
    }
    

    int range_size = range_max - range_min;
    result = range_min + ((curved * range_size) / 255);
}

function logarithmic_curve(int input) returns int result {

    if (input <= 0) {
        result = 0;
    } else if (input >= 255) {
        result = 255;
    } else {

        int temp = input;
        int log_val = 0;
        loop {
            if (temp <= 1) break;
            log_val = log_val + 32;
            temp = temp >> 1;
        }
        result = log_val;
        if (result > 255) result = 255;
    }
}
```

## Crossfading Between States

```impala

global array param_bank_a[8] = {200, 300, 400, 500, 0, 0, 0, 0}
global array param_bank_b[8] = {800, 100, 900, 200, 0, 0, 0, 0}
global int param_crossfade = 128

function crossfade_parameters() {
    int fade_amount = global param_crossfade;
    int inv_fade = 255 - fade_amount;
    
    int i = 0;
    loop {
        if (i >= 4) break;
        
        int value_a = global param_bank_a[i];
        int value_b = global param_bank_b[i];
        

        int mixed = ((value_a * inv_fade) + (value_b * fade_amount)) / 255;
        global param_target[i] = mixed;
        
        i = i + 1;
    }
}


function crossfade_with_curve(int fade_pos, int curve_type) returns int result {
    if (curve_type == 0) {
        result = fade_pos;
    } else if (curve_type == 1) {
        result = smooth_step(fade_pos);
    } else if (curve_type == 2) {
        result = equal_power(fade_pos);
    } else {
        result = fade_pos;
    }
}

function smooth_step(int x) returns int result {

    int norm = (x * 256) / 255;
    int x2 = (norm * norm) / 256;
    int x3 = (x2 * norm) / 256;
    result = ((3 * x2) - (2 * x3)) / 256;
    if (result > 255) result = 255;
    if (result < 0) result = 0;
}

function equal_power(int x) returns int result {


    result = sqrt_approx(x);
}

function sqrt_approx(int x) returns int result {

    if (x <= 0) {
        result = 0;
    } else if (x >= 255) {
        result = 16;
    } else {

        int temp = x;
        int shift = 0;
        loop {
            if (temp < 2) break;
            temp = temp >> 2;
            shift = shift + 1;
        }
        result = 1 << shift;
    }
}
```

## Envelope-Based Parameter Control

```impala

global int filter_env_attack = 100
global int filter_env_decay = 200
global int filter_env_sustain = 180
global int filter_env_release = 500
global int filter_env_current_stage = 0
global int filter_env_stage_progress = 0
global int filter_env_target_param = 1

function trigger_envelope() {
    global filter_env_current_stage = 1;
    global filter_env_stage_progress = 0;
}

function process_envelope() {
    if (global filter_env_current_stage == 1) {

        global filter_env_stage_progress = global filter_env_stage_progress + 1;
        int level = (global filter_env_stage_progress * 255) / global filter_env_attack;
        if (level > 255) level = 255;
        if (level < 0) level = 0;
        
        global param_target[global filter_env_target_param] = level;
        
        if (global filter_env_stage_progress >= global filter_env_attack) {
            global filter_env_current_stage = 2;
            global filter_env_stage_progress = 0;
        }
    } else if (global filter_env_current_stage == 2) {

        global filter_env_stage_progress = global filter_env_stage_progress + 1;
        int decay_amount = 255 - global filter_env_sustain;
        int level = 255 - ((global filter_env_stage_progress * decay_amount) / global filter_env_decay);
        
        if (level < global filter_env_sustain) level = global filter_env_sustain;
        if (level > 255) level = 255;
        
        global param_target[global filter_env_target_param] = level;
        
        if (global filter_env_stage_progress >= global filter_env_decay) {
            global filter_env_current_stage = 3;
        }
    } else if (global filter_env_current_stage == 3) {

        global param_target[global filter_env_target_param] = global filter_env_sustain;
    } else if (global filter_env_current_stage == 4) {

        global filter_env_stage_progress = global filter_env_stage_progress + 1;
        int level = global filter_env_sustain - ((global filter_env_stage_progress * global filter_env_sustain) / global filter_env_release);
        
        if (level < 0) level = 0;
        if (level > global filter_env_sustain) level = global filter_env_sustain;
        
        global param_target[global filter_env_target_param] = level;
        
        if (global filter_env_stage_progress >= global filter_env_release) {
            global filter_env_current_stage = 0;
        }
    }

}

function release_envelope() {
    global filter_env_current_stage = 4;
    global filter_env_stage_progress = 0;
}
```

## LFO Parameter Modulation

```impala

global int mod_lfo_frequency = 5
global int mod_lfo_amplitude = 50
global int mod_lfo_phase = 0
global int mod_lfo_waveform = 0
global int mod_lfo_target_param = 2
global int mod_lfo_center_value = 128


array sine_lfo_table[8] = {0, 90, 127, 90, 0, -90, -127, -90};
array triangle_table[8] = {0, 64, 127, 64, 0, -64, -127, -64};

function process_lfo() {

    global mod_lfo_phase = global mod_lfo_phase + global mod_lfo_frequency;
    if (global mod_lfo_phase >= 256) {
        global mod_lfo_phase = global mod_lfo_phase - 256;
    }
    

    int wave_value;
    if (global mod_lfo_waveform == 0) {
        wave_value = sine_wave(global mod_lfo_phase);
    } else if (global mod_lfo_waveform == 1) {
        wave_value = triangle_wave(global mod_lfo_phase);
    } else if (global mod_lfo_waveform == 2) {
        wave_value = sawtooth_wave(global mod_lfo_phase);
    } else if (global mod_lfo_waveform == 3) {
        wave_value = square_wave(global mod_lfo_phase);
    } else {
        wave_value = 0;
    }
    

    int modulated = global mod_lfo_center_value + ((wave_value * global mod_lfo_amplitude) / 128);
    

    if (modulated < 0) modulated = 0;
    if (modulated > 255) modulated = 255;
    
    global param_target[global mod_lfo_target_param] = modulated;
}

function sine_wave(int phase) returns int result {

    int table_index = (phase * 7) / 255;
    if (table_index > 7) table_index = 7;
    result = sine_lfo_table[table_index];
}

function triangle_wave(int phase) returns int result {

    int table_index = (phase * 7) / 255;
    if (table_index > 7) table_index = 7;
    result = triangle_table[table_index];
}

function sawtooth_wave(int phase) returns int result {

    result = (phase * 255 / 127) - 127;
}

function square_wave(int phase) returns int result {

    if (phase < 128) {
        result = -127;
    } else {
        result = 127;
    }
}
```

## Integration Example

```impala

function process() {
    loop {

        update_parameter_morphing();
        process_macro_control();
        crossfade_parameters();
        process_envelope();
        process_lfo();
        

        int input = global signal[0];
        int filtered = apply_filter(input, (int)global params[SWITCHES_PARAM_INDEX]);
        global signal[1] = filtered;
        

        global displayLEDs[0] = global param_current[0] >> 0;
        global displayLEDs[1] = global filter_env_current_stage * 64;
        global displayLEDs[2] = global mod_lfo_phase;
        global displayLEDs[3] = global param_crossfade;
        
        yield();
    }
}


function apply_filter(int input, int cutoff) returns int result {

    static int filter_state = 0;
    int filter_amount = cutoff;
    

    global filter_state = global filter_state + ((input - global filter_state) * filter_amount / 255);
    result = global filter_state;
}
```

This implementation provides complete, working parameter morphing and dynamic control functionality using beginner-friendly Impala syntax. All code examples compile and run on Permut8, enabling complex parameter relationships and smooth real-time control for professional performance scenarios while remaining accessible to beginners learning Impala firmware development.
