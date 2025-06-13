# MIDI Learn Implementation

## Overview
Enable dynamic MIDI controller assignment, allowing users to assign any MIDI CC to any firmware parameter in real-time without recompiling.

> **Note**: This file contains advanced implementation concepts. For a practical working version, see [midi-learn-simplified.md](midi-learn-simplified.md) which provides the same core functionality using proper Impala syntax.

## Core MIDI Learn Structure

```impala
// MIDI Learn mapping table
struct MidiMapping {
    cc_number: i32,
    param_index: i32,
    min_value: i32,
    max_value: i32,
    is_active: bool
}

let midi_map: [MidiMapping; 8] = [
    MidiMapping { cc_number: -1, param_index: 0, min_value: 0, max_value: 1023, is_active: false },
    // ... initialize 8 slots
];

let learn_mode = false;
let learn_target_param = -1;
```

## Learn Mode Implementation

```impala
fn enter_learn_mode(param_index: i32) {
    learn_mode = true;
    learn_target_param = param_index;
    
    // Visual feedback - blink LED for target parameter
    displayLEDs[0] = 0x0F0F;  // Blink pattern
}

fn process_midi_learn(cc_number: i32, value: i32) {
    if learn_mode && learn_target_param >= 0 {
        // Find empty mapping slot or update existing
        let slot = find_mapping_slot(cc_number);
        
        midi_map[slot].cc_number = cc_number;
        midi_map[slot].param_index = learn_target_param;
        midi_map[slot].min_value = 0;
        midi_map[slot].max_value = 1023;
        midi_map[slot].is_active = true;
        
        // Exit learn mode
        learn_mode = false;
        learn_target_param = -1;
        displayLEDs[0] = 0x00FF;  // Success indicator
    }
}

fn find_mapping_slot(cc_number: i32) -> i32 {
    // First, check if CC already mapped
    for i in 0..8 {
        if midi_map[i].cc_number == cc_number {
            return i;
        }
    }
    
    // Find empty slot
    for i in 0..8 {
        if !midi_map[i].is_active {
            return i;
        }
    }
    
    return 0;  // Use first slot if all full
}
```

## MIDI Processing with Learned Mappings

```impala
fn handle_midi_cc(cc_number: i32, value: i32) {
    // Check if in learn mode first
    if learn_mode {
        process_midi_learn(cc_number, value);
        return;
    }
    
    // Process learned mappings
    for i in 0..8 {
        let mapping = midi_map[i];
        if mapping.is_active && mapping.cc_number == cc_number {
            apply_learned_mapping(mapping, value);
        }
    }
}

fn apply_learned_mapping(mapping: MidiMapping, midi_value: i32) {
    // Scale MIDI value (0-127) to parameter range
    let scaled_value = scale_value(midi_value, 0, 127, 
                                  mapping.min_value, mapping.max_value);
    
    params[mapping.param_index] = scaled_value;
}

fn scale_value(value: i32, in_min: i32, in_max: i32, 
               out_min: i32, out_max: i32) -> i32 {
    let in_range = in_max - in_min;
    let out_range = out_max - out_min;
    return out_min + ((value - in_min) * out_range / in_range);
}
```

## User Interface Integration

```impala
// Switch-based learn mode activation
fn check_learn_switches() {
    // Hold switch 1 + press parameter switch to enter learn
    if signal[0] > 1000 {  // Switch 1 held
        if signal[1] > 1000 && !prev_switch[1] {  // Switch 2 pressed
            enter_learn_mode(0);  // Learn for parameter 0
        }
        if signal[2] > 1000 && !prev_switch[2] {  // Switch 3 pressed
            enter_learn_mode(1);  // Learn for parameter 1
        }
    }
}

// Clear learned mappings
fn clear_midi_mappings() {
    for i in 0..8 {
        midi_map[i].is_active = false;
        midi_map[i].cc_number = -1;
    }
    displayLEDs[0] = 0xFF00;  // Clear confirmation
}
```

## Advanced Mapping Features

```impala
// Bidirectional mapping with custom scaling
struct AdvancedMapping {
    cc_number: i32,
    param_index: i32,
    curve_type: i32,  // 0=linear, 1=exponential, 2=logarithmic
    invert: bool,
    center_detent: bool
}

fn apply_curve(value: i32, curve_type: i32) -> i32 {
    match curve_type {
        0 => value,  // Linear
        1 => (value * value) >> 10,  // Exponential
        2 => logarithmic_scale(value),  // Logarithmic
        _ => value
    }
}

fn logarithmic_scale(value: i32) -> i32 {
    // Simple log approximation for parameter curves
    if value <= 0 { return 0; }
    let log_val = 0;
    let temp = value;
    while temp > 1 {
        log_val += 1;
        temp >>= 1;
    }
    return log_val << 7;  // Scale to parameter range
}
```

## Memory Management

```impala
// Persistent storage simulation
let eeprom_mappings: [u8; 64] = [0; 64];  // 8 mappings * 8 bytes each

fn save_mappings_to_eeprom() {
    for i in 0..8 {
        let offset = i * 8;
        eeprom_mappings[offset] = midi_map[i].cc_number as u8;
        eeprom_mappings[offset + 1] = midi_map[i].param_index as u8;
        eeprom_mappings[offset + 2] = midi_map[i].is_active as u8;
        // Store min/max values as 16-bit values
    }
}

fn load_mappings_from_eeprom() {
    for i in 0..8 {
        let offset = i * 8;
        midi_map[i].cc_number = eeprom_mappings[offset] as i32;
        midi_map[i].param_index = eeprom_mappings[offset + 1] as i32;
        midi_map[i].is_active = eeprom_mappings[offset + 2] != 0;
    }
}
```

This implementation provides flexible MIDI learn functionality that works with any controller and can be customized for different parameter behaviors.
