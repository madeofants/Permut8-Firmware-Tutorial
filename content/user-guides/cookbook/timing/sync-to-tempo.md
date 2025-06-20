# Sync to Tempo

*Create tempo-synchronized effects that lock to rhythmic timing*

## What This Does

Creates tempo-synchronized effects using internal timing for rhythmic delays, gates, and modulation. Demonstrates beat tracking, subdivision timing, and tempo-locked processing.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Tempo/BPM (0-255)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Subdivision (whole, half, quarter, eighth notes)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Gate width (0-255)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Effect amount (0-255)

**Core Techniques:**
- **Beat tracking**: Count samples to track musical beats
- **Subdivision timing**: Create different note values
- **Rhythmic gating**: On/off effects synced to beats
- **Tempo-locked delays**: Delays that match musical timing

**Key Concepts:** Sample counting, musical timing, rhythmic modulation, tempo calculation

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
global array params[PARAM_COUNT]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Tempo synchronization state
global int sample_counter = 0       // Current position in beat
global int beat_counter = 0         // Current beat number
global int samples_per_beat = 22050 // Default: 120 BPM at 44.1kHz
global int gate_state = 0           // Current gate state (0/1)
global array delay_buffer[44100]    // 1-second delay buffer
global int delay_write_pos = 0      // Write position in delay buffer

function process()
locals int tempo_param, int subdivision, int gate_width, int effect_amount, int bpm_value, int beat_length, int gate_samples, int beat_position, int input_sample, int delayed_sample, int gated_sample, int output_sample, int delay_read_pos
{
    loop {
        // Read tempo and timing parameters
        tempo_param = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];      // 0-255 tempo control
        subdivision = (int)global (int)global params[SWITCHES_PARAM_INDEX] >> 6; // 0-3 subdivision (4 types)
        gate_width = (int)global (int)global params[OPERATOR_1_PARAM_INDEX];       // 0-255 gate width
        effect_amount = (int)global (int)global params[OPERAND_1_HIGH_PARAM_INDEX];    // 0-255 effect intensity
        
        // Calculate BPM from parameter (60-180 BPM range)
        bpm_value = 60 + ((tempo_param * 120) >> 8);  // 60-180 BPM
        
        // Calculate samples per beat at 44.1kHz
        // Formula: (60 * sample_rate) / BPM
        global samples_per_beat = (60 * 44100) / bpm_value;
        
        // Apply subdivision (whole, half, quarter, eighth notes)
        if (subdivision == 0) {
            // Whole note (4 beats)
            beat_length = global samples_per_beat << 2;  // 4x longer
        } else if (subdivision == 1) {
            // Half note (2 beats)
            beat_length = global samples_per_beat << 1;  // 2x longer
        } else if (subdivision == 2) {
            // Quarter note (1 beat)
            beat_length = global samples_per_beat;       // Normal beat
        } else {
            // Eighth note (1/2 beat)
            beat_length = global samples_per_beat >> 1;  // 2x faster
        }
        
        // Advance sample counter
        global sample_counter = global sample_counter + 1;
        
        // Check for beat boundary
        if (global sample_counter >= beat_length) {
            global sample_counter = 0;
            global beat_counter = global beat_counter + 1;
            if (global beat_counter >= 16) global beat_counter = 0; // 16-beat cycle
        }
        
        // Calculate gate timing based on gate width parameter
        gate_samples = (beat_length * gate_width) >> 8;  // Gate width as fraction of beat
        
        // Update gate state
        if (global sample_counter < gate_samples) {
            global gate_state = 1;  // Gate on
        } else {
            global gate_state = 0;  // Gate off
        }
        
        // Calculate beat position for delay timing
        beat_position = global sample_counter;
        
        // Read input sample
        input_sample = (int)global signal[0];
        
        // Tempo-synced delay (read from delay buffer)
        delay_read_pos = global delay_write_pos - beat_length;
        if (delay_read_pos < 0) delay_read_pos = delay_read_pos + 44100;
        if (delay_read_pos >= 44100) delay_read_pos = delay_read_pos - 44100;
        
        delayed_sample = (int)global delay_buffer[delay_read_pos];
        
        // Apply rhythmic gating to signal
        if (global gate_state == 1) {
            gated_sample = input_sample;  // Full volume during gate
        } else {
            gated_sample = input_sample >> 2;  // Quarter volume during gate off
        }
        
        // Mix dry signal with tempo-synced delay
        output_sample = gated_sample + 
            ((delayed_sample * effect_amount) >> 8);
        
        // Store current sample in delay buffer
        global delay_buffer[global delay_write_pos] = input_sample;
        global delay_write_pos = global delay_write_pos + 1;
        if (global delay_write_pos >= 44100) global delay_write_pos = 0;
        
        // Prevent clipping
        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        
        // Output processed signal
        global signal[0] = output_sample;
        global signal[1] = output_sample;
        
        // Visual feedback on LEDs
        global displayLEDs[0] = bpm_value;                    // Show BPM
        global displayLEDs[1] = subdivision << 6;             // Show subdivision
        if (global gate_state == 1) {
            global displayLEDs[2] = 255;  // Gate on
        } else {
            global displayLEDs[2] = 0;    // Gate off
        }
        global displayLEDs[3] = beat_position >> 8;          // Beat position
        
        yield();
    }
}

```

## How It Works

**Beat Tracking**: Counts audio samples to track musical beats. At 44.1kHz, 120 BPM = 22,050 samples per beat.

**Subdivision Timing**: Divides or multiplies beat length to create different note values:
- Whole note: 4x beat length
- Half note: 2x beat length  
- Quarter note: 1x beat length
- Eighth note: 0.5x beat length

**Rhythmic Gating**: Creates on/off effect synced to beat timing. Gate width controls how much of each beat has full volume.

**Tempo-Locked Delay**: Delay time matches musical timing exactly, creating rhythmic echoes that sync with the beat.

**Parameter Control**:
- **Knob 1**: Tempo/BPM (60-180 range)
- **Knob 2**: Note subdivision (whole/half/quarter/eighth)
- **Knob 3**: Gate width (duty cycle)
- **Knob 4**: Effect amount (delay feedback)

## Try These Settings

```impala
// Fast rhythmic gating
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;  // High tempo (170 BPM)
(int)global params[SWITCHES_PARAM_INDEX] = 192;  // Eighth note subdivision
(int)global params[OPERATOR_1_PARAM_INDEX] = 100;  // Short gate width
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 150;  // Medium delay feedback

// Slow tempo with long gates
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 80;   // Low tempo (100 BPM)
(int)global params[SWITCHES_PARAM_INDEX] = 64;   // Half note subdivision
(int)global params[OPERATOR_1_PARAM_INDEX] = 200;  // Long gate width
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 100;  // Light delay feedback

// Medium tempo, quarter notes
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 128;  // Medium tempo (120 BPM)
(int)global params[SWITCHES_PARAM_INDEX] = 128;  // Quarter note subdivision
(int)global params[OPERATOR_1_PARAM_INDEX] = 128;  // 50% gate width
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 180;  // Heavy delay feedback

// Very slow whole notes
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 60;   // Slow tempo (90 BPM)
(int)global params[SWITCHES_PARAM_INDEX] = 0;    // Whole note subdivision
(int)global params[OPERATOR_1_PARAM_INDEX] = 255;  // Full gate width
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 80;   // Subtle delay
```

## Understanding Tempo Sync

**Sample Rate Math**: Musical timing converts to sample counts. 120 BPM = one beat every 0.5 seconds = 22,050 samples at 44.1kHz.

**Beat Subdivisions**: Different note values create different rhythmic feels. Eighth notes feel twice as fast as quarter notes.

**Gate Timing**: Controls the duty cycle of rhythmic effects. 50% gate = half of each beat is "on".

**Musical Alignment**: Tempo-synced effects feel musical because they align with beat timing rather than arbitrary delays.

## Try These Changes

- **Triplet timing**: Multiply beat length by 2/3 for triplet feels
- **Swing timing**: Alternate between long and short beat lengths
- **Polyrhythms**: Run multiple tempo-synced effects at different subdivisions
- **Tempo ramping**: Gradually change tempo over time

## Related Techniques

- **[Clock Dividers](clock-dividers.md)**: Create multiple tempo relationships
- **[Swing Timing](swing-timing.md)**: Add rhythmic swing to tempo sync
- **[Automation Sequencing](../parameters/automation-sequencing.md)**: Sequence parameters in tempo

---
*Part of the [Permut8 Cookbook](../index.md) series*