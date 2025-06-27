# Clock Dividers

*Create sophisticated rhythm subdivision systems from a single master clock*

## What This Does

Generates multiple polyrhythmic outputs from a single master clock, enabling complex rhythmic relationships and musical timing patterns. Creates everything from simple beat divisions to complex polyrhythmic sequences.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Division 1 ratio (0-255)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Division 2 ratio (0-255)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Division 3 ratio (0-255)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Master clock rate (0-255)

**Core Techniques:**
- **Clock division**: Generate slower clocks from faster master
- **Polyrhythms**: Multiple rhythmic patterns simultaneously
- **Musical ratios**: Standard note subdivisions
- **Gate generation**: Create rhythmic pulses for effects

**Key Concepts:** Clock division, polyrhythms, musical timing, gate patterns, rhythmic modulation

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


global int master_counter = 0
global int division_counter_0 = 0
global int division_counter_1 = 0
global int division_counter_2 = 0
global int gate_output_0 = 0
global int gate_output_1 = 0
global int gate_output_2 = 0
global int master_rate = 11025

function process()
locals division1, division2, division3, clock_rate, master_pulse, gate_state, input_sample, output_sample
{
    loop {

        division1 = (params[CLOCK_FREQ_PARAM_INDEX] >> 4) + 1;
        division2 = (params[SWITCHES_PARAM_INDEX] >> 4) + 1;
        division3 = (params[OPERATOR_1_PARAM_INDEX] >> 4) + 1;
        clock_rate = params[OPERAND_1_HIGH_PARAM_INDEX];
        

        global master_rate = 2756 + ((clock_rate * 19600) >> 8);
        

        global master_counter = global master_counter + 1;
        

        master_pulse = 0;
        if (global master_counter >= global master_rate) {
            global master_counter = 0;
            master_pulse = 1;
        }
        

        if (master_pulse == 1) {

            global division_counter_0 = global division_counter_0 + 1;
            if (global division_counter_0 >= division1) {
                global division_counter_0 = 0;
                global gate_output_0 = 1;
            } else {
                global gate_output_0 = 0;
            }
            

            global division_counter_1 = global division_counter_1 + 1;
            if (global division_counter_1 >= division2) {
                global division_counter_1 = 0;
                global gate_output_1 = 1;
            } else {
                global gate_output_1 = 0;
            }
            

            global division_counter_2 = global division_counter_2 + 1;
            if (global division_counter_2 >= division3) {
                global division_counter_2 = 0;
                global gate_output_2 = 1;
            } else {
                global gate_output_2 = 0;
            }
        }
        

        input_sample = signal[0];
        

        gate_state = 0;
        if (global gate_output_0 == 1) gate_state = gate_state + 1;
        if (global gate_output_1 == 1) gate_state = gate_state + 2;
        if (global gate_output_2 == 1) gate_state = gate_state + 4;
        

        if (gate_state == 0) {

            output_sample = input_sample;
            
        } else if (gate_state == 1) {

            output_sample = input_sample - (input_sample >> 3);
            
        } else if (gate_state == 2) {

            output_sample = input_sample - (input_sample >> 2);
            
        } else if (gate_state == 4) {

            output_sample = input_sample - (input_sample >> 1);
            
        } else {

            output_sample = input_sample + (input_sample >> 2);
        }
        

        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        

        global signal[0] = output_sample;
        global signal[1] = output_sample;
        

        if (global gate_output_0 == 1) {
            global displayLEDs[0] = 255;
        } else {
            global displayLEDs[0] = 32;
        }
        
        if (global gate_output_1 == 1) {
            global displayLEDs[1] = 255;
        } else {
            global displayLEDs[1] = 32;
        }
        
        if (global gate_output_2 == 1) {
            global displayLEDs[2] = 255;
        } else {
            global displayLEDs[2] = 32;
        }
        
        if (master_pulse == 1) {
            global displayLEDs[3] = 255;
        } else {
            global displayLEDs[3] = 16;
        }
        
        yield();
    }
}

```

## How It Works

**Master Clock**: Generates regular timing pulses based on sample counting. Faster clock rates = more frequent pulses.

**Division Counters**: Each division has its own counter that advances with master clock pulses. When counter reaches division ratio, generate output pulse.

**Musical Ratios**: Common divisions create standard musical relationships:
- Division 1: Quarter notes
- Division 2: Half notes
- Division 4: Whole notes
- Division 8: Very slow pulses

**Gate Combination**: Multiple division outputs can trigger simultaneously, creating complex rhythmic patterns.

**Parameter Control**:
- **Knob 1**: Division 1 ratio (1-16)
- **Knob 2**: Division 2 ratio (1-16)
- **Knob 3**: Division 3 ratio (1-16)
- **Knob 4**: Master clock speed (slow to fast)

## Try These Settings

```impala

params[CLOCK_FREQ_PARAM_INDEX] = 16;
params[SWITCHES_PARAM_INDEX] = 32;
params[OPERATOR_1_PARAM_INDEX] = 64;
params[OPERAND_1_HIGH_PARAM_INDEX] = 128;


params[CLOCK_FREQ_PARAM_INDEX] = 16;
params[SWITCHES_PARAM_INDEX] = 48;
params[OPERATOR_1_PARAM_INDEX] = 80;
params[OPERAND_1_HIGH_PARAM_INDEX] = 200;


params[CLOCK_FREQ_PARAM_INDEX] = 112;
params[SWITCHES_PARAM_INDEX] = 160;
params[OPERATOR_1_PARAM_INDEX] = 208;
params[OPERAND_1_HIGH_PARAM_INDEX] = 64;


params[CLOCK_FREQ_PARAM_INDEX] = 16;
params[SWITCHES_PARAM_INDEX] = 64;
params[OPERATOR_1_PARAM_INDEX] = 128;
params[OPERAND_1_HIGH_PARAM_INDEX] = 150;
```

## Understanding Clock Dividers

**Division Math**: A division ratio of N means "output pulse every N master pulses". Higher ratios = slower outputs.

**Polyrhythmic Relationships**: Different division ratios create complex rhythmic interactions that repeat at the least common multiple.

**Musical Timing**: Standard divisions (2, 3, 4, 8) create familiar musical relationships.

**Phase Relationships**: Different divisions start at the same time but pulse at different rates, creating shifting phase relationships.

## Try These Changes

- **Prime number divisions**: Use 3, 5, 7, 11 for complex non-repeating patterns
- **Euclidean patterns**: Distribute pulses evenly across divisions
- **Swing timing**: Offset alternate pulses for groove
- **Probabilistic gates**: Random chance for each division to pulse

## Related Techniques

- **[Sync to Tempo](sync-to-tempo.md)**: Use clock dividers with tempo sync
- **[Swing Timing](swing-timing.md)**: Add groove to clock divisions
- **[Automation Sequencing](../parameters/automation-sequencing.md)**: Sequence parameters with clock divisions

---
*Part of the [Permut8 Cookbook](../index.md) series*