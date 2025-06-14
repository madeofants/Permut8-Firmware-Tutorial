# Swing Timing

*Transform rigid mechanical timing into natural, human-feeling grooves*

## What This Does

Adds groove and humanization to rhythmic sequences by applying swing timing and micro-timing variations. Transforms mechanical beats into natural, musical timing with everything from subtle shuffle to heavy jazz swing.

## Quick Reference

**Essential Parameters:**
- `params[0]`: Swing amount (0-255)
- `params[1]`: Humanization level (0-255)
- `params[2]`: Groove pattern (0-255)
- `params[3]`: Effect intensity (0-255)

**Core Techniques:**
- **Swing timing**: Delay off-beat events for groove
- **Humanization**: Add random timing variations
- **Groove patterns**: Different swing styles (jazz, shuffle, latin)
- **Velocity swing**: Apply groove to dynamics, not just timing

**Key Concepts:** Off-beat delay, micro-timing, humanization, groove templates, swing ratios

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Swing timing system state
global int step_counter = 0         // Current step counter
global int base_step_time = 5512    // Base step duration (eighth notes)
global int swing_offset = 0         // Current swing offset
global int random_seed = 12345      // For humanization
global int current_step = 0         // Step position (0-7)

function process()
locals int swing_amount, int humanization, int groove_pattern, int effect_intensity, int step_time, int is_offbeat, int timing_offset, int random_variation, int input_sample, int delayed_sample, int output_sample, int gate_state
{
    loop {
        // Read swing and timing parameters
        swing_amount = (int)global params[0];       // 0-255 swing amount
        humanization = (int)global params[1];      // 0-255 humanization
        groove_pattern = (int)global params[2] >> 6; // 0-3 groove types
        effect_intensity = (int)global params[3];  // 0-255 effect level
        
        // Advance step counter
        global step_counter = global step_counter + 1;
        
        // Determine if current position is on off-beat
        is_offbeat = (global current_step % 2);  // 1 for off-beats, 0 for on-beats
        
        // Calculate swing offset based on groove pattern
        if (groove_pattern == 0) {
            // Straight timing - no swing
            timing_offset = 0;
            
        } else if (groove_pattern == 1) {
            // Standard swing - delay off-beats
            if (is_offbeat == 1) {
                timing_offset = ((swing_amount - 128) * 32) >> 7;  // 0-32 sample delay
            } else {
                timing_offset = 0;
            }
            
        } else if (groove_pattern == 2) {
            // Shuffle/triplet feel - more extreme off-beat delay
            if (is_offbeat == 1) {
                timing_offset = ((swing_amount - 128) * 64) >> 7;  // 0-64 sample delay
            } else {
                timing_offset = 0;
            }
            
        } else {
            // Complex pattern - alternating swing
            if (global current_step == 1 || global current_step == 5) {
                timing_offset = ((swing_amount - 128) * 24) >> 7;
            } else if (global current_step == 3 || global current_step == 7) {
                timing_offset = ((swing_amount - 128) * 40) >> 7;
            } else {
                timing_offset = 0;
            }
        }
        
        // Add humanization (random timing variation)
        if (humanization > 0) {
            // Simple pseudo-random number generator
            global random_seed = (global random_seed * 1103515245 + 12345) & 0x7FFFFFFF;
            random_variation = (global random_seed % (humanization + 1)) - (humanization >> 1);
            timing_offset = timing_offset + random_variation;
        }
        
        // Calculate total step time with swing
        step_time = global base_step_time + timing_offset;
        if (step_time < 1000) step_time = 1000;  // Minimum step time
        
        // Check for step boundary
        gate_state = 0;
        if (global step_counter >= step_time) {
            global step_counter = 0;
            global current_step = (global current_step + 1) % 8;  // 8-step cycle
            gate_state = 1;  // Trigger gate
        }
        
        // Read input sample
        input_sample = (int)global signal[0];
        
        // Apply swing-based processing
        if (gate_state == 1) {
            // On step trigger: apply effect based on swing timing
            if (is_offbeat == 1 && swing_amount > 128) {
                // Off-beat with swing: emphasize the groove
                delayed_sample = input_sample + (input_sample >> 2);  // Slight boost
            } else {
                // On-beat or straight timing: clean signal
                delayed_sample = input_sample;
            }
        } else {
            // Between steps: use previous processed value
            delayed_sample = input_sample - (input_sample >> 3);  // Slight reduction
        }
        
        // Mix processed signal based on effect intensity
        output_sample = ((input_sample * (255 - effect_intensity)) + 
                        (delayed_sample * effect_intensity)) >> 8;
        
        // Prevent clipping
        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        
        // Output processed signal
        global signal[0] = output_sample;
        global signal[1] = output_sample;
        
        // Display swing state on LEDs
        global displayLEDs[0] = swing_amount;                 // Swing amount
        global displayLEDs[1] = groove_pattern << 6;          // Groove pattern
        if (gate_state == 1) {
            global displayLEDs[2] = 255;  // Step trigger active
        } else {
            global displayLEDs[2] = 32;   // Step trigger inactive
        }
        global displayLEDs[3] = global current_step << 5;     // Step position
        
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
// Straight timing (no swing)
params[0] = 128;  // No swing
params[1] = 16;   // Minimal humanization
params[2] = 0;    // Straight pattern
params[3] = 100;  // Light effect

// Light jazz swing
params[0] = 180;  // Moderate swing
params[1] = 32;   // Light humanization
params[2] = 64;   // Standard swing pattern
params[3] = 150;  // Medium effect

// Heavy shuffle
params[0] = 220;  // Heavy swing
params[1] = 64;   // More humanization
params[2] = 128;  // Shuffle pattern
params[3] = 200;  // Strong effect

// Complex groove
params[0] = 200;  // Strong swing
params[1] = 80;   // Significant humanization
params[2] = 192;  // Complex pattern
params[3] = 180;  // Heavy effect
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