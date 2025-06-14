# MIDI Synchronization Techniques

## Overview
Implement MIDI clock synchronization for tempo-locked effects, ensuring sample-accurate timing with external sequencers, DAWs, and hardware devices.

## MIDI Clock Fundamentals

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// MIDI clock state management
global int midi_running = 0     // Clock running state
global int clock_counter = 0    // Current clock tick count
global int samples_per_clock = 1024  // Samples between MIDI clock ticks (24 per beat)
global int sample_counter = 0   // Sample counter within current clock
global int current_tempo = 120  // Current tempo in BPM
global int clock_received = 0   // Flag for received clock tick
```

### MIDI Clock Processing

```impala
// Process MIDI clock messages from parameter inputs
function process_midi_clock()
locals int midi_message, int start_message, int stop_message, int clock_tick
{
    // Read MIDI messages from parameters
    midi_message = (int)global params[4];   // MIDI status byte
    start_message = (int)global params[5];  // Start/stop commands
    clock_tick = (int)global params[6];     // Clock tick input
    
    // Handle MIDI Start (FA)
    if (start_message == 250) {  // 0xFA
        global midi_running = 1;
        global clock_counter = 0;
        global sample_counter = 0;
        reset_synced_effects();
    }
    
    // Handle MIDI Stop (FC)
    if (start_message == 252) {  // 0xFC
        global midi_running = 0;
    }
    
    // Handle MIDI Clock (F8) - 24 per quarter note
    if (clock_tick == 248) {  // 0xF8
        global clock_received = 1;
        global clock_counter = global clock_counter + 1;
        global sample_counter = 0;  // Reset for precise timing
        update_tempo_estimation();
    }
}

// Reset synchronized effects on start
function reset_synced_effects()
{
    // Reset any tempo-locked effect state here
    global clock_counter = 0;
    global sample_counter = 0;
    
    // Visual feedback
    global displayLEDs[0] = 255;  // Start indicator
}

// Simple tempo estimation
function update_tempo_estimation()
{
    // Update samples per clock based on simple calculation
    // At 120 BPM: 24 clocks per beat, 2 beats per second = 48 clocks/sec
    // At 44.1kHz: 44100/48 = 919 samples per clock
    // This is simplified - real implementation would measure actual timing
    global samples_per_clock = 44100 / ((global current_tempo * 24) / 60);
}
```

## Clock Prediction and Timing

```impala
// Predict timing between MIDI clocks for smooth operation
function update_clock_prediction()
locals int clock_phase_256
{
    if (global midi_running == 0) return;
    
    // Update sample counter
    global sample_counter = global sample_counter + 1;
    
    // Calculate phase between MIDI clocks (0-255 for easier math)
    if (global samples_per_clock > 0) {
        clock_phase_256 = (global sample_counter * 256) / global samples_per_clock;
        if (clock_phase_256 > 255) clock_phase_256 = 255;
    } else {
        clock_phase_256 = 0;
    }
    
    // Reset if we've passed expected clock time
    if (global sample_counter >= global samples_per_clock) {
        if (global clock_received == 0) {
            // Clock is late - adjust timing slightly
            global samples_per_clock = global samples_per_clock + 1;
        }
        global sample_counter = 0;
        global clock_received = 0;
    }
    
    // Store phase for use by synced effects
    global displayLEDs[3] = clock_phase_256;  // Visual phase indicator
}
```

## Synchronized Effects

### Beat-Locked Delay

```impala
// Delay synchronized to MIDI clock divisions
global int delay_buffer[4096]   // Simple delay buffer
global int delay_write_pos = 0  // Write position in buffer
global int delay_time = 1024    // Current delay time in samples

function synced_delay()
locals int division, int clocks_per_note, int samples_per_note, int target_delay
locals int input, int delayed, int feedback, int output
{
    // Read delay division setting from parameter
    division = (int)global params[1] >> 6;  // 0-3 from top 2 bits
    
    // Division settings: 1/4, 1/8, 1/16, 1/32 notes
    if (division == 0) {
        clocks_per_note = 24;      // Quarter note
    } else if (division == 1) {
        clocks_per_note = 12;      // Eighth note
    } else if (division == 2) {
        clocks_per_note = 6;       // Sixteenth note
    } else {
        clocks_per_note = 3;       // Thirty-second note
    }
    
    // Calculate delay time in samples
    samples_per_note = global samples_per_clock * clocks_per_note;
    if (samples_per_note > 4000) samples_per_note = 4000;  // Limit to buffer size
    
    // Smooth delay time changes
    target_delay = samples_per_note;
    if (global delay_time < target_delay) {
        global delay_time = global delay_time + 1;
    } else if (global delay_time > target_delay) {
        global delay_time = global delay_time - 1;
    }
    
    // Process delay
    input = (int)global signal[0];
    feedback = (int)global params[2];  // Feedback amount
    
    // Read from delay buffer
    delayed = global delay_buffer[global delay_write_pos];
    
    // Write to delay buffer with feedback
    global delay_buffer[global delay_write_pos] = input + ((delayed * feedback) >> 8);
    
    // Advance write position
    global delay_write_pos = global delay_write_pos + 1;
    if (global delay_write_pos >= global delay_time) {
        global delay_write_pos = 0;
    }
    
    // Mix delayed signal with input
    output = input + ((delayed * (int)global params[3]) >> 8);  // Wet level
    
    return output;
}
```

### Tempo-Locked LFO

```impala
// LFO synchronized to MIDI clock
global int lfo_phase = 0        // LFO phase accumulator
global int lfo_rate_division = 24  // MIDI clocks per LFO cycle

function generate_synced_lfo()
locals int lfo_division, int clocks_per_cycle, int phase_increment, int lfo_output
{
    // Read LFO rate from parameter
    lfo_division = (int)global params[7] >> 5;  // 0-7 divisions
    
    // Set clock division for LFO rate
    if (lfo_division == 0) {
        clocks_per_cycle = 96;     // 1 bar (4 beats)
    } else if (lfo_division == 1) {
        clocks_per_cycle = 48;     // 2 beats
    } else if (lfo_division == 2) {
        clocks_per_cycle = 24;     // 1 beat
    } else if (lfo_division == 3) {
        clocks_per_cycle = 12;     // 1/2 beat
    } else {
        clocks_per_cycle = 6;      // 1/4 beat
    }
    
    if (global midi_running == 1) {
        // Sync to MIDI clock
        global lfo_phase = ((global clock_counter % clocks_per_cycle) * 256) / clocks_per_cycle;
        
        // Add inter-clock interpolation
        phase_increment = (global sample_counter * 256) / (global samples_per_clock * clocks_per_cycle);
        global lfo_phase = global lfo_phase + phase_increment;
        if (global lfo_phase > 255) global lfo_phase = global lfo_phase - 256;
    } else {
        // Free-running mode
        phase_increment = 256 / 1000;  // Slow free-running rate
        global lfo_phase = global lfo_phase + phase_increment;
        if (global lfo_phase > 255) global lfo_phase = global lfo_phase - 256;
    }
    
    // Generate triangle wave (simple LFO shape)
    if (global lfo_phase < 128) {
        lfo_output = global lfo_phase * 2;           // Rising
    } else {
        lfo_output = 255 - ((global lfo_phase - 128) * 2);  // Falling
    }
    
    return lfo_output;
}
```

### Rhythmic Gate Sequencer

```impala
// Simple gate sequencer synced to MIDI clock
global array gate_pattern[16] = {1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0}
global int current_step = 0
global int clocks_per_step = 6  // 16th note steps
global int step_clock = 0

function update_synced_gate()
locals int gate_open, int gate_level, int audio_sample
{
    if (global midi_running == 0) {
        // No sync - gate always open
        return (int)global signal[0];
    }
    
    // Update step position based on MIDI clock
    global step_clock = global step_clock + 1;
    if (global step_clock >= global clocks_per_step) {
        global step_clock = 0;
        global current_step = global current_step + 1;
        if (global current_step >= 16) global current_step = 0;
    }
    
    // Get gate state from pattern
    gate_open = global gate_pattern[global current_step];
    
    // Process audio through gate
    audio_sample = (int)global signal[0];
    
    if (gate_open == 1) {
        gate_level = 255;  // Gate open
    } else {
        gate_level = (int)global params[0] >> 2;  // Closed level (0-63)
    }
    
    // Apply gate
    audio_sample = (audio_sample * gate_level) >> 8;
    
    // Visual feedback
    global displayLEDs[1] = gate_open ? 255 : 32;
    global displayLEDs[2] = global current_step << 4;  // Show step
    
    return audio_sample;
}
```

## Complete Synchronized Audio Processing

```impala
function process()
locals int input_sample, int delayed_sample, int lfo_value, int gated_sample, int output_sample
{
    loop {
        // Handle MIDI clock system
        process_midi_clock();
        update_clock_prediction();
        
        // Read input
        input_sample = (int)global signal[0];
        
        // Apply synchronized effects
        delayed_sample = synced_delay();
        lfo_value = generate_synced_lfo();
        gated_sample = update_synced_gate();
        
        // Combine effects
        output_sample = gated_sample;
        
        // Apply LFO modulation to output level
        output_sample = (output_sample * (128 + (lfo_value >> 1))) >> 8;
        
        // Prevent clipping
        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        
        // Output processed signal
        global signal[0] = output_sample;
        global signal[1] = output_sample;
        
        // Update sync display
        update_sync_display();
        
        yield();
    }
}

// Visual feedback for synchronization status
function update_sync_display()
{
    // Show running status
    if (global midi_running == 1) {
        global displayLEDs[0] = 255;  // Bright when running
    } else {
        global displayLEDs[0] = 64;   // Dim when stopped
    }
    
    // Beat indicator - flash on quarter notes
    if ((global clock_counter % 24) == 0) {
        global displayLEDs[1] = 255;  // Beat flash
    } else if (global displayLEDs[1] > 10) {
        global displayLEDs[1] = global displayLEDs[1] - 10;  // Fade
    }
    
    // Show current tempo/timing
    global displayLEDs[2] = global current_tempo;
}
```

## Parameter Usage Guide

### Control Parameters:
- **params[0]**: Gate closed level (how much signal when gate closed)
- **params[1]**: Delay division (bits 6-7: 0=1/4, 1=1/8, 2=1/16, 3=1/32)
- **params[2]**: Delay feedback amount
- **params[3]**: Delay wet level
- **params[4]**: MIDI message input (status bytes)
- **params[5]**: MIDI start/stop commands
- **params[6]**: MIDI clock tick input
- **params[7]**: LFO rate division (bits 5-7)

## Key Benefits

**Sample-Accurate Timing**: Synchronization with external sequencers through MIDI clock processing.

**Musical Divisions**: Support for standard note divisions (quarter to thirty-second notes).

**Visual Feedback**: LED indicators show sync status, beats, and effect activity.

**Simple Interface**: Uses parameter inputs for MIDI data, making it DAW-compatible.

**Real-Time Performance**: Efficient implementation suitable for live audio processing.

This simplified MIDI sync system provides essential tempo-locked functionality while maintaining Impala compatibility and real-time audio performance.