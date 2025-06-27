# MIDI Synchronization Techniques

## Overview
Implement MIDI clock synchronization for tempo-locked effects, ensuring sample-accurate timing with external sequencers, DAWs, and hardware devices.

## MIDI Clock Fundamentals

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


global int midi_running = 0
global int clock_counter = 0
global int samples_per_clock = 1024
global int sample_counter = 0
global int current_tempo = 120
global int clock_received = 0
```

### MIDI Clock Processing

```impala

function process_midi_clock()
locals int midi_message, int start_message, int stop_message, int clock_tick
{

    midi_message = (int)global params[OPERAND_1_LOW_PARAM_INDEX];
    start_message = (int)global params[OPERATOR_2_PARAM_INDEX];
    clock_tick = (int)global params[OPERAND_2_HIGH_PARAM_INDEX];
    

    if (start_message == 250) {
        global midi_running = 1;
        global clock_counter = 0;
        global sample_counter = 0;
        reset_synced_effects();
    }
    

    if (start_message == 252) {
        global midi_running = 0;
    }
    

    if (clock_tick == 248) {
        global clock_received = 1;
        global clock_counter = global clock_counter + 1;
        global sample_counter = 0;
        update_tempo_estimation();
    }
}


function reset_synced_effects()
{

    global clock_counter = 0;
    global sample_counter = 0;
    

    global displayLEDs[0] = 255;
}


function update_tempo_estimation()
{




    global samples_per_clock = 44100 / ((global current_tempo * 24) / 60);
}
```

## Clock Prediction and Timing

```impala

function update_clock_prediction()
locals int clock_phase_256
{
    if (global midi_running == 0) return;
    

    global sample_counter = global sample_counter + 1;
    

    if (global samples_per_clock > 0) {
        clock_phase_256 = (global sample_counter * 256) / global samples_per_clock;
        if (clock_phase_256 > 255) clock_phase_256 = 255;
    } else {
        clock_phase_256 = 0;
    }
    

    if (global sample_counter >= global samples_per_clock) {
        if (global clock_received == 0) {

            global samples_per_clock = global samples_per_clock + 1;
        }
        global sample_counter = 0;
        global clock_received = 0;
    }
    

    global displayLEDs[3] = clock_phase_256;
}
```

## Synchronized Effects

### Beat-Locked Delay

```impala

global int delay_buffer[4096]
global int delay_write_pos = 0
global int delay_time = 1024

function synced_delay()
locals int division, int clocks_per_note, int samples_per_note, int target_delay
locals int input, int delayed, int feedback, int output
{

    division = (int)global params[SWITCHES_PARAM_INDEX] >> 6;
    

    if (division == 0) {
        clocks_per_note = 24;
    } else if (division == 1) {
        clocks_per_note = 12;
    } else if (division == 2) {
        clocks_per_note = 6;
    } else {
        clocks_per_note = 3;
    }
    

    samples_per_note = global samples_per_clock * clocks_per_note;
    if (samples_per_note > 4000) samples_per_note = 4000;
    

    target_delay = samples_per_note;
    if (global delay_time < target_delay) {
        global delay_time = global delay_time + 1;
    } else if (global delay_time > target_delay) {
        global delay_time = global delay_time - 1;
    }
    

    input = (int)global signal[0];
    feedback = (int)global params[OPERATOR_1_PARAM_INDEX];
    

    delayed = global delay_buffer[global delay_write_pos];
    

    global delay_buffer[global delay_write_pos] = input + ((delayed * feedback) >> 8);
    

    global delay_write_pos = global delay_write_pos + 1;
    if (global delay_write_pos >= global delay_time) {
        global delay_write_pos = 0;
    }
    

    output = input + ((delayed * (int)global params[OPERAND_1_HIGH_PARAM_INDEX]) >> 8);
    
    return output;
}
```

### Tempo-Locked LFO

```impala

global int lfo_phase = 0
global int lfo_rate_division = 24

function generate_synced_lfo()
locals int lfo_division, int clocks_per_cycle, int phase_increment, int lfo_output
{

    lfo_division = (int)global params[OPERAND_2_LOW_PARAM_INDEX] >> 5;
    

    if (lfo_division == 0) {
        clocks_per_cycle = 96;
    } else if (lfo_division == 1) {
        clocks_per_cycle = 48;
    } else if (lfo_division == 2) {
        clocks_per_cycle = 24;
    } else if (lfo_division == 3) {
        clocks_per_cycle = 12;
    } else {
        clocks_per_cycle = 6;
    }
    
    if (global midi_running == 1) {

        global lfo_phase = ((global clock_counter % clocks_per_cycle) * 256) / clocks_per_cycle;
        

        phase_increment = (global sample_counter * 256) / (global samples_per_clock * clocks_per_cycle);
        global lfo_phase = global lfo_phase + phase_increment;
        if (global lfo_phase > 255) global lfo_phase = global lfo_phase - 256;
    } else {

        phase_increment = 256 / 1000;
        global lfo_phase = global lfo_phase + phase_increment;
        if (global lfo_phase > 255) global lfo_phase = global lfo_phase - 256;
    }
    

    if (global lfo_phase < 128) {
        lfo_output = global lfo_phase * 2;
    } else {
        lfo_output = 255 - ((global lfo_phase - 128) * 2);
    }
    
    return lfo_output;
}
```

### Rhythmic Gate Sequencer

```impala

global array gate_pattern[16] = {1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0}
global int current_step = 0
global int clocks_per_step = 6
global int step_clock = 0

function update_synced_gate()
locals int gate_open, int gate_level, int audio_sample
{
    if (global midi_running == 0) {

        return (int)global signal[0];
    }
    

    global step_clock = global step_clock + 1;
    if (global step_clock >= global clocks_per_step) {
        global step_clock = 0;
        global current_step = global current_step + 1;
        if (global current_step >= 16) global current_step = 0;
    }
    

    gate_open = global gate_pattern[global current_step];
    

    audio_sample = (int)global signal[0];
    
    if (gate_open == 1) {
        gate_level = 255;
    } else {
        gate_level = (int)global params[CLOCK_FREQ_PARAM_INDEX] >> 2;
    }
    

    audio_sample = (audio_sample * gate_level) >> 8;
    

    if (gate_open) {
        global displayLEDs[1] = 255;
    } else {
        global displayLEDs[1] = 32;
    }
    global displayLEDs[2] = global current_step << 4;
    
    return audio_sample;
}
```

## Complete Synchronized Audio Processing

```impala
function process()
locals int input_sample, int delayed_sample, int lfo_value, int gated_sample, int output_sample
{
    loop {

        process_midi_clock();
        update_clock_prediction();
        

        input_sample = (int)global signal[0];
        

        delayed_sample = synced_delay();
        lfo_value = generate_synced_lfo();
        gated_sample = update_synced_gate();
        

        output_sample = gated_sample;
        

        output_sample = (output_sample * (128 + (lfo_value >> 1))) >> 8;
        

        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        

        global signal[0] = output_sample;
        global signal[1] = output_sample;
        

        update_sync_display();
        
        yield();
    }
}


function update_sync_display()
{

    if (global midi_running == 1) {
        global displayLEDs[0] = 255;
    } else {
        global displayLEDs[0] = 64;
    }
    

    if ((global clock_counter % 24) == 0) {
        global displayLEDs[1] = 255;
    } else if (global displayLEDs[1] > 10) {
        global displayLEDs[1] = global displayLEDs[1] - 10;
    }
    

    global displayLEDs[2] = global current_tempo;
}
```

## Parameter Usage Guide

### Control Parameters:
- **params[CLOCK_FREQ_PARAM_INDEX]**: Gate closed level (how much signal when gate closed)
- **params[SWITCHES_PARAM_INDEX]**: Delay division (bits 6-7: 0=1/4, 1=1/8, 2=1/16, 3=1/32)
- **params[OPERATOR_1_PARAM_INDEX]**: Delay feedback amount
- **params[OPERAND_1_HIGH_PARAM_INDEX]**: Delay wet level
- **params[OPERAND_1_LOW_PARAM_INDEX]**: MIDI message input (status bytes)
- **params[OPERATOR_2_PARAM_INDEX]**: MIDI start/stop commands
- **params[OPERAND_2_HIGH_PARAM_INDEX]**: MIDI clock tick input
- **params[OPERAND_2_LOW_PARAM_INDEX]**: LFO rate division (bits 5-7)

## Key Benefits

**Sample-Accurate Timing**: Synchronization with external sequencers through MIDI clock processing.

**Musical Divisions**: Support for standard note divisions (quarter to thirty-second notes).

**Visual Feedback**: LED indicators show sync status, beats, and effect activity.

**Simple Interface**: Uses parameter inputs for MIDI data, making it DAW-compatible.

**Real-Time Performance**: Efficient implementation suitable for live audio processing.

This simplified MIDI sync system provides essential tempo-locked functionality while maintaining Impala compatibility and real-time audio performance.