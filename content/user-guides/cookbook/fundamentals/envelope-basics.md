# Envelope Basics

*Control amplitude over time with ADSR envelopes*

## What This Does

An envelope controls how a parameter changes over time, most commonly the volume of a sound. It creates the shape of a sound from the moment it starts until it completely fades away, making the difference between percussive plucks and sustained pads.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Attack time (0-255, how fast sound reaches full volume)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Decay time (0-255, how fast it drops to sustain level)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Sustain level (0-255, ongoing level while held)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Release time (0-255, how fast it fades when released)

**ADSR Stages:**
- **Attack**: Rise to peak volume
- **Decay**: Drop to sustain level
- **Sustain**: Maintain level while note held
- **Release**: Fade to silence when note released

**Key Concepts:** Time-based control, amplitude shaping, musical expression, parameter automation

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2


const int AUDIO_MAX = 2047
const int AUDIO_MIN = -2047
const int PARAM_MAX = 255
const int PARAM_HALF = 128
const int ENVELOPE_PEAK = 2047
const int ENVELOPE_ATTACK_THRESHOLD = 1900
const int ENVELOPE_DECAY_TOLERANCE = 50
const int ENVELOPE_SILENCE_THRESHOLD = 10


const int OPERAND_1_HIGH_PARAM_INDEX = 0
const int OPERAND_1_LOW_PARAM_INDEX = 1
const int OPERAND_2_HIGH_PARAM_INDEX = 2
const int OPERAND_2_LOW_PARAM_INDEX = 3
const int OPERATOR_1_PARAM_INDEX = 4
const int OPERATOR_2_PARAM_INDEX = 5
const int SWITCHES_PARAM_INDEX = 6
const int CLOCK_FREQ_PARAM_INDEX = 7
const int PARAM_COUNT = 8


const int STAGE_OFF = 0
const int STAGE_ATTACK = 1
const int STAGE_DECAY = 2
const int STAGE_SUSTAIN = 3
const int STAGE_RELEASE = 4


extern native yield


global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]


global int envelope_level = 0
global int envelope_stage = 0
global int stage_counter = 0
global int gate_trigger = 0

function process()
locals int attack, int decay, int sustain, int release, int stage_time, int target_level, int output
{
    loop {

        attack = (params[CLOCK_FREQ_PARAM_INDEX] >> 3) + 1;
        decay = (params[SWITCHES_PARAM_INDEX] >> 3) + 1;
        sustain = (params[OPERATOR_1_PARAM_INDEX] << 3);
        release = (params[OPERAND_1_HIGH_PARAM_INDEX] >> 3) + 1;
        


        if (params[OPERAND_1_LOW_PARAM_INDEX] > PARAM_HALF && global gate_trigger == 0) {
            global gate_trigger = 1;
            global envelope_stage = STAGE_ATTACK;
            global stage_counter = 0;
        } else if (params[OPERAND_1_LOW_PARAM_INDEX] <= PARAM_HALF && global gate_trigger == 1) {
            global gate_trigger = 0;
            global envelope_stage = STAGE_RELEASE;
            global stage_counter = 0;
        }
        

        if (global envelope_stage == STAGE_ATTACK) {

            target_level = ENVELOPE_PEAK;
            global envelope_level = global envelope_level + ((target_level - global envelope_level) >> attack);
            

            if (global envelope_level > ENVELOPE_ATTACK_THRESHOLD) {
                global envelope_stage = STAGE_DECAY;
                global stage_counter = 0;
            }
            
        } else if (global envelope_stage == STAGE_DECAY) {

            global envelope_level = global envelope_level + ((sustain - global envelope_level) >> decay);
            

            if (global envelope_level <= (sustain + ENVELOPE_DECAY_TOLERANCE) && global envelope_level >= (sustain - ENVELOPE_DECAY_TOLERANCE)) {
                global envelope_stage = STAGE_SUSTAIN;
            }
            
        } else if (global envelope_stage == STAGE_SUSTAIN) {

            global envelope_level = sustain;
            
        } else if (global envelope_stage == STAGE_RELEASE) {

            global envelope_level = global envelope_level + ((0 - global envelope_level) >> release);
            

            if (global envelope_level < ENVELOPE_SILENCE_THRESHOLD) {
                global envelope_stage = STAGE_OFF;
                global envelope_level = 0;
            }
            
        } else {

            global envelope_level = 0;
        }
        

        output = (signal[0] * global envelope_level) >> 11;
        

        if (output > AUDIO_MAX) output = AUDIO_MAX;
        if (output < AUDIO_MIN) output = AUDIO_MIN;
        

        signal[0] = output;
        signal[1] = output;
        

        displayLEDs[0] = global envelope_level >> 3;
        displayLEDs[1] = global envelope_stage << 6;
        displayLEDs[2] = attack << 3;
        displayLEDs[3] = sustain >> 3;
        
        yield();
    }
}

```

## How It Works

**Envelope Stages**: The envelope moves through four stages - attack, decay, sustain, and release - each with different target levels and timing.

**Stage Transitions**: Each stage automatically moves to the next when its goal is reached or conditions are met.

**Gate Control**: A gate signal (note on/off) triggers the attack or release phases.

**Level Interpolation**: Each stage smoothly moves toward its target level using simple low-pass filtering.

**Parameter Control**:
- **Control 1**: Attack time (lower = faster attack)
- **Control 2**: Decay time (lower = faster decay)
- **Control 3**: Sustain level (higher = louder sustain)
- **Control 4**: Release time (lower = faster release)
- **Knob 5**: Gate trigger (above 128 = note on, below 128 = note off)

## Try These Settings

```impala

(int)global params[CLOCK_FREQ_PARAM_INDEX] = 8;
(int)global params[SWITCHES_PARAM_INDEX] = 64;
(int)global params[OPERATOR_1_PARAM_INDEX] = 100;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 64;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;
(int)global params[SWITCHES_PARAM_INDEX] = 150;
(int)global params[OPERATOR_1_PARAM_INDEX] = 200;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 8;
(int)global params[SWITCHES_PARAM_INDEX] = 32;
(int)global params[OPERATOR_1_PARAM_INDEX] = 0;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 32;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 16;
(int)global params[SWITCHES_PARAM_INDEX] = 32;
(int)global params[OPERATOR_1_PARAM_INDEX] = 220;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 32;
```

## Understanding ADSR

**Attack Phase**: Determines how percussive or smooth the beginning of a sound is. Fast attack = sharp, immediate sound. Slow attack = gradual fade-in.

**Decay Phase**: Controls how quickly the sound drops from its peak to the sustain level. Creates the initial "bloom" of a sound.

**Sustain Phase**: The ongoing level while a note is held. Piano notes naturally decay, but synthesizers can sustain indefinitely.

**Release Phase**: How the sound fades away after the note is released. Short release = abrupt cutoff. Long release = gradual fade.

**Musical Applications**: Different instruments have characteristic envelope shapes that define their character and musical behavior.

## Try These Changes

- **Envelope modulation**: Use the envelope to control filter cutoff or oscillator pitch
- **Multiple envelopes**: Create separate envelopes for different parameters
- **Velocity sensitivity**: Scale envelope levels based on note velocity
- **Curved envelopes**: Replace linear interpolation with exponential curves

## Related Techniques

- **[Basic Oscillator](basic-oscillator.md)**: Generate tones to shape with envelopes
- **[Basic Filter](basic-filter.md)**: Use envelopes to control filter parameters

---
*Part of the [Permut8 Cookbook](../index.md) series*