# Swing Timing

*Transform rigid mechanical timing into natural, human-feeling grooves*

## What This Does

Adds groove and humanization to rhythmic sequences by applying swing timing and micro-timing variations. Transforms mechanical beats into natural, musical timing with everything from subtle shuffle to heavy jazz swing.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Swing amount (0-255)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Humanization level (0-255)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Groove pattern (0-255)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Effect intensity (0-255)

**Core Techniques:**
- **Swing timing**: Delay off-beat events for groove
- **Humanization**: Add random timing variations
- **Groove patterns**: Different swing styles (jazz, shuffle, latin)
- **Velocity swing**: Apply groove to dynamics, not just timing

**Key Concepts:** Off-beat delay, micro-timing, humanization, groove templates, swing ratios

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


global int step_counter = 0
global int base_step_time = 5512
global int swing_offset = 0
global int random_seed = 12345
global int current_step = 0

function process()
locals swing_amount, humanization, groove_pattern, effect_intensity, step_time, is_offbeat, timing_offset, random_variation, input_sample, delayed_sample, output_sample, gate_state
{
    loop {

        swing_amount = params[CLOCK_FREQ_PARAM_INDEX];
        humanization = params[SWITCHES_PARAM_INDEX];
        groove_pattern = params[OPERATOR_1_PARAM_INDEX] >> 6;
        effect_intensity = params[OPERAND_1_HIGH_PARAM_INDEX];
        

        global step_counter = global step_counter + 1;
        

        is_offbeat = (global current_step % 2);
        

        if (groove_pattern == 0) {

            timing_offset = 0;
            
        } else if (groove_pattern == 1) {

            if (is_offbeat == 1) {
                timing_offset = ((swing_amount - 128) * 32) >> 7;
            } else {
                timing_offset = 0;
            }
            
        } else if (groove_pattern == 2) {

            if (is_offbeat == 1) {
                timing_offset = ((swing_amount - 128) * 64) >> 7;
            } else {
                timing_offset = 0;
            }
            
        } else {

            if (global current_step == 1 || global current_step == 5) {
                timing_offset = ((swing_amount - 128) * 24) >> 7;
            } else if (global current_step == 3 || global current_step == 7) {
                timing_offset = ((swing_amount - 128) * 40) >> 7;
            } else {
                timing_offset = 0;
            }
        }
        

        if (humanization > 0) {

            global random_seed = (global random_seed * 1103515245 + 12345) & 0x7FFFFFFF;
            random_variation = (global random_seed % (humanization + 1)) - (humanization >> 1);
            timing_offset = timing_offset + random_variation;
        }
        

        step_time = global base_step_time + timing_offset;
        if (step_time < 1000) step_time = 1000;
        

        gate_state = 0;
        if (global step_counter >= step_time) {
            global step_counter = 0;
            global current_step = (global current_step + 1) % 8;
            gate_state = 1;
        }
        

        input_sample = signal[0];
        

        if (gate_state == 1) {

            if (is_offbeat == 1 && swing_amount > 128) {

                delayed_sample = input_sample + (input_sample >> 2);
            } else {

                delayed_sample = input_sample;
            }
        } else {

            delayed_sample = input_sample - (input_sample >> 3);
        }
        

        output_sample = ((input_sample * (255 - effect_intensity)) + 
                        (delayed_sample * effect_intensity)) >> 8;
        

        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        

        global signal[0] = output_sample;
        global signal[1] = output_sample;
        

        global displayLEDs[0] = swing_amount;
        global displayLEDs[1] = groove_pattern << 6;
        if (gate_state == 1) {
            global displayLEDs[2] = 255;
        } else {
            global displayLEDs[2] = 32;
        }
        global displayLEDs[3] = global current_step << 5;
        
        yield();
    }
}

```

## How It Works

**Swing Timing**: Delays off-beat events to create groove. Higher swing amounts = more pronounced delay.

**Groove Patterns**: Different mathematical patterns create different feels:
- Straight: No timing offset (mechanical)
- Standard swing: Delay every other beat
- Shuffle: Triplet-based feel with longer delays
- Complex: Varies delay amount by step position

**Humanization**: Adds random timing variations to prevent mechanical feel. Small amounts sound natural, large amounts sound sloppy.

**Effect Processing**: Applies different audio processing based on swing timing and step position.

**Parameter Control**:
- **Knob 1**: Swing amount (128=straight, 255=heavy swing)
- **Knob 2**: Humanization (random timing variation)
- **Knob 3**: Groove pattern (0-3 different styles)
- **Knob 4**: Effect intensity (wet/dry mix)

## Try These Settings

```impala

params[CLOCK_FREQ_PARAM_INDEX] = 128;
params[SWITCHES_PARAM_INDEX] = 16;
params[OPERATOR_1_PARAM_INDEX] = 0;
params[OPERAND_1_HIGH_PARAM_INDEX] = 100;


params[CLOCK_FREQ_PARAM_INDEX] = 180;
params[SWITCHES_PARAM_INDEX] = 32;
params[OPERATOR_1_PARAM_INDEX] = 64;
params[OPERAND_1_HIGH_PARAM_INDEX] = 150;


params[CLOCK_FREQ_PARAM_INDEX] = 220;
params[SWITCHES_PARAM_INDEX] = 64;
params[OPERATOR_1_PARAM_INDEX] = 128;
params[OPERAND_1_HIGH_PARAM_INDEX] = 200;


params[CLOCK_FREQ_PARAM_INDEX] = 200;
params[SWITCHES_PARAM_INDEX] = 80;
params[OPERATOR_1_PARAM_INDEX] = 192;
params[OPERAND_1_HIGH_PARAM_INDEX] = 180;
```

## Understanding Swing Timing

**Swing Ratios**: Classic swing is often described as 2:1 triplet feel, but musical swing varies continuously.

**Off-Beat Emphasis**: Swing isn't just timing - it affects dynamics, tone, and musical emphasis.

**Humanization vs Swing**: Swing is systematic timing offset. Humanization is random variation that mimics human playing.

**Musical Context**: Different genres use different swing amounts. Jazz uses heavy swing, rock uses light swing or straight timing.

## Try These Changes

- **Velocity swing**: Apply groove to volume/dynamics, not just timing
- **Frequency-dependent swing**: Different swing amounts for different frequency bands
- **Polyrhythmic swing**: Different swing patterns running simultaneously
- **Adaptive swing**: Swing amount changes based on musical content

## Related Techniques

- **[Sync to Tempo](sync-to-tempo.md)**: Combine swing with tempo-locked effects
- **[Clock Dividers](clock-dividers.md)**: Apply swing to multiple clock divisions
- **[Automation Sequencing](../parameters/automation-sequencing.md)**: Sequence swing parameters

---
*Part of the [Permut8 Cookbook](../index.md) series*