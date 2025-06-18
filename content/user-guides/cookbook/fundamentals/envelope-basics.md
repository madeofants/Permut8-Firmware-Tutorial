# Envelope Basics

*Control amplitude over time with ADSR envelopes*

## What This Does

An envelope controls how a parameter changes over time, most commonly the volume of a sound. It creates the shape of a sound from the moment it starts until it completely fades away, making the difference between percussive plucks and sustained pads.

## Quick Reference

**Essential Parameters:**
- `params[0]`: Attack time (0-255, how fast sound reaches full volume)
- `params[1]`: Decay time (0-255, how fast it drops to sustain level)
- `params[2]`: Sustain level (0-255, ongoing level while held)
- `params[3]`: Release time (0-255, how fast it fades when released)

**ADSR Stages:**
- **Attack**: Rise to peak volume
- **Decay**: Drop to sustain level
- **Sustain**: Maintain level while note held
- **Release**: Fade to silence when note released

**Key Concepts:** Time-based control, amplitude shaping, musical expression, parameter automation

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Simple ADSR envelope state
global int envelope_level = 0   // Current envelope level (0-2047)
global int envelope_stage = 0   // Current stage (0=off, 1=attack, 2=decay, 3=sustain, 4=release)
global int stage_counter = 0    // Counter for current stage timing
global int gate_trigger = 0     // Gate input (0=off, 1=on)

function process()
locals int attack, int decay, int sustain, int release, int stage_time, int target_level, int output
{
    loop {
        // Read parameters
        attack = ((int)global params[0] >> 3) + 1;     // 1-32 attack speed
        decay = ((int)global params[1] >> 3) + 1;      // 1-32 decay speed
        sustain = ((int)global params[2] << 3);        // 0-2040 sustain level
        release = ((int)global params[3] >> 3) + 1;    // 1-32 release speed
        
        // Simple gate trigger (could be connected to note input)
        // For demo: use knob position to trigger envelope
        if ((int)global params[4] > 128 && global gate_trigger == 0) {
            global gate_trigger = 1;
            global envelope_stage = 1;  // Start attack
            global stage_counter = 0;
        } else if ((int)global params[4] <= 128 && global gate_trigger == 1) {
            global gate_trigger = 0;
            global envelope_stage = 4;  // Start release
            global stage_counter = 0;
        }
        
        // Process envelope stages
        if (global envelope_stage == 1) {
            // Attack stage - rise to peak
            target_level = 2047;
            global envelope_level = global envelope_level + ((target_level - global envelope_level) >> attack);
            
            // Check if attack is complete
            if (global envelope_level > 1900) {
                global envelope_stage = 2;  // Move to decay
                global stage_counter = 0;
            }
            
        } else if (global envelope_stage == 2) {
            // Decay stage - drop to sustain level
            global envelope_level = global envelope_level + ((sustain - global envelope_level) >> decay);
            
            // Check if decay is complete
            if (global envelope_level <= (sustain + 50) && global envelope_level >= (sustain - 50)) {
                global envelope_stage = 3;  // Move to sustain
            }
            
        } else if (global envelope_stage == 3) {
            // Sustain stage - maintain level
            global envelope_level = sustain;
            
        } else if (global envelope_stage == 4) {
            // Release stage - fade to silence
            global envelope_level = global envelope_level + ((0 - global envelope_level) >> release);
            
            // Check if release is complete
            if (global envelope_level < 10) {
                global envelope_stage = 0;  // Back to idle
                global envelope_level = 0;
            }
            
        } else {
            // Idle stage
            global envelope_level = 0;
        }
        
        // Apply envelope to input signal
        output = ((int)global signal[0] * global envelope_level) >> 11;
        
        // Prevent clipping
        if (output > 2047) output = 2047;
        if (output < -2047) output = -2047;
        
        // Output result
        global signal[0] = output;
        global signal[1] = output;
        
        // Show envelope activity on LEDs
        global displayLEDs[0] = global envelope_level >> 3;  // Show envelope level
        global displayLEDs[1] = global envelope_stage << 6;  // Show current stage
        global displayLEDs[2] = attack << 3;                 // Show attack setting
        global displayLEDs[3] = sustain >> 3;               // Show sustain level
        
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
// Piano envelope
params[0] = 8;    // Fast attack
params[1] = 64;   // Medium decay
params[2] = 100;  // Low sustain
params[3] = 64;   // Medium release

// Pad envelope
params[0] = 200;  // Slow attack
params[1] = 150;  // Slow decay
params[2] = 200;  // High sustain
params[3] = 200;  // Long release

// Percussion envelope
params[0] = 8;    // Very fast attack
params[1] = 32;   // Fast decay
params[2] = 0;    // No sustain
params[3] = 32;   // Fast release

// Bass envelope
params[0] = 16;   // Quick attack
params[1] = 32;   // Short decay
params[2] = 220;  // High sustain
params[3] = 32;   // Short release
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