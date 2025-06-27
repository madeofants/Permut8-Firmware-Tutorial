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


global int sample_counter = 0
global int beat_counter = 0
global int samples_per_beat = 22050
global int gate_state = 0
global array delay_buffer[44100]
global int delay_write_pos = 0

function process()
locals tempo_param, subdivision, gate_width, effect_amount, bpm_value, beat_length, gate_samples, beat_position, input_sample, delayed_sample, gated_sample, output_sample, delay_read_pos
{
    loop {

        tempo_param = params[CLOCK_FREQ_PARAM_INDEX];
        subdivision = params[SWITCHES_PARAM_INDEX] >> 6;
        gate_width = params[OPERATOR_1_PARAM_INDEX];
        effect_amount = params[OPERAND_1_HIGH_PARAM_INDEX];
        

        bpm_value = 60 + ((tempo_param * 120) >> 8);
        


        global samples_per_beat = (60 * 44100) / bpm_value;
        

        if (subdivision == 0) {

            beat_length = global samples_per_beat << 2;
        } else if (subdivision == 1) {

            beat_length = global samples_per_beat << 1;
        } else if (subdivision == 2) {

            beat_length = global samples_per_beat;
        } else {

            beat_length = global samples_per_beat >> 1;
        }
        

        global sample_counter = global sample_counter + 1;
        

        if (global sample_counter >= beat_length) {
            global sample_counter = 0;
            global beat_counter = global beat_counter + 1;
            if (global beat_counter >= 16) global beat_counter = 0;
        }
        

        gate_samples = (beat_length * gate_width) >> 8;
        

        if (global sample_counter < gate_samples) {
            global gate_state = 1;
        } else {
            global gate_state = 0;
        }
        

        beat_position = global sample_counter;
        

        input_sample = signal[0];
        

        delay_read_pos = global delay_write_pos - beat_length;
        if (delay_read_pos < 0) delay_read_pos = delay_read_pos + 44100;
        if (delay_read_pos >= 44100) delay_read_pos = delay_read_pos - 44100;
        
        delayed_sample = delay_buffer[delay_read_pos];
        

        if (global gate_state == 1) {
            gated_sample = input_sample;
        } else {
            gated_sample = input_sample >> 2;
        }
        

        output_sample = gated_sample + 
            ((delayed_sample * effect_amount) >> 8);
        

        global delay_buffer[global delay_write_pos] = input_sample;
        global delay_write_pos = global delay_write_pos + 1;
        if (global delay_write_pos >= 44100) global delay_write_pos = 0;
        

        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        

        global signal[0] = output_sample;
        global signal[1] = output_sample;
        

        global displayLEDs[0] = bpm_value;
        global displayLEDs[1] = subdivision << 6;
        if (global gate_state == 1) {
            global displayLEDs[2] = 255;
        } else {
            global displayLEDs[2] = 0;
        }
        global displayLEDs[3] = beat_position >> 8;
        
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

params[CLOCK_FREQ_PARAM_INDEX] = 200;
params[SWITCHES_PARAM_INDEX] = 192;
params[OPERATOR_1_PARAM_INDEX] = 100;
params[OPERAND_1_HIGH_PARAM_INDEX] = 150;


params[CLOCK_FREQ_PARAM_INDEX] = 80;
params[SWITCHES_PARAM_INDEX] = 64;
params[OPERATOR_1_PARAM_INDEX] = 200;
params[OPERAND_1_HIGH_PARAM_INDEX] = 100;


params[CLOCK_FREQ_PARAM_INDEX] = 128;
params[SWITCHES_PARAM_INDEX] = 128;
params[OPERATOR_1_PARAM_INDEX] = 128;
params[OPERAND_1_HIGH_PARAM_INDEX] = 180;


params[CLOCK_FREQ_PARAM_INDEX] = 60;
params[SWITCHES_PARAM_INDEX] = 0;
params[OPERATOR_1_PARAM_INDEX] = 255;
params[OPERAND_1_HIGH_PARAM_INDEX] = 80;
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