# Automation Sequencing

*Create automated parameter sequences for dynamic, evolving effects*

## What This Does

Provides step-based automation sequencing for parameters, enabling complex evolving effects and rhythmic parameter modulation. Create sequences of parameter values that play back automatically with internal timing.

## Quick Reference

**Essential Parameters:**
- `params[0]`: Sequence speed (0-255)
- `params[1]`: Step length (1-16 steps)
- `params[2]`: Pattern type (0-255)
- `params[3]`: Sequence enable (>128 = on)

**Core Techniques:**
- **Step sequencing**: Preset parameter values advance over time
- **Pattern programming**: Create rhythmic parameter changes
- **Tempo control**: Adjust sequence playback speed
- **Multi-parameter automation**: Different sequences for different parameters

**Key Concepts:** Step sequencing, automation patterns, rhythmic control, evolving textures

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Automation sequencer state
global array step_pattern[8]    // 8-step pattern values
global int current_step = 0     // Current step position (0-7)
global int step_counter = 0     // Sample counter for timing
global int step_interval = 4410 // Samples per step (default ~100ms at 44.1kHz)
global int sequence_active = 0  // Sequence on/off state

function process()
locals int sequence_speed, int pattern_length, int pattern_type, int sequence_enable, int step_length, int pattern_value, int cutoff_freq, int resonance, int input_sample, int filtered_sample, int output_sample
{
    loop {
        // Read sequencer control parameters
        sequence_speed = (int)global params[0];           // 0-255 speed
        pattern_length = ((int)global params[1] >> 5) + 1; // 1-8 steps
        pattern_type = (int)global params[2] >> 6;        // 0-3 pattern types
        sequence_enable = (int)global params[3];          // Enable/disable
        
        // Calculate step timing based on speed
        step_length = 11025 - ((sequence_speed * 10800) >> 8); // 225-11025 samples
        if (step_length < 225) step_length = 225;             // Minimum ~5ms
        
        // Enable/disable sequencer
        if (sequence_enable > 127) {
            global sequence_active = 1;
        } else {
            global sequence_active = 0;
            global current_step = 0;
            global step_counter = 0;
        }
        
        // Generate step pattern based on pattern type
        if (pattern_type == 0) {
            // Rising pattern
            global step_pattern[0] = 32;   global step_pattern[1] = 64;
            global step_pattern[2] = 96;   global step_pattern[3] = 128;
            global step_pattern[4] = 160;  global step_pattern[5] = 192;
            global step_pattern[6] = 224;  global step_pattern[7] = 255;
            
        } else if (pattern_type == 1) {
            // Alternating pattern
            global step_pattern[0] = 255;  global step_pattern[1] = 64;
            global step_pattern[2] = 255;  global step_pattern[3] = 64;
            global step_pattern[4] = 255;  global step_pattern[5] = 64;
            global step_pattern[6] = 255;  global step_pattern[7] = 64;
            
        } else if (pattern_type == 2) {
            // Random-ish pattern (pseudo-random based on step number)
            global step_pattern[0] = 128;  global step_pattern[1] = 200;
            global step_pattern[2] = 80;   global step_pattern[3] = 255;
            global step_pattern[4] = 32;   global step_pattern[5] = 180;
            global step_pattern[6] = 150;  global step_pattern[7] = 100;
            
        } else {
            // Falling pattern
            global step_pattern[0] = 255;  global step_pattern[1] = 224;
            global step_pattern[2] = 192;  global step_pattern[3] = 160;
            global step_pattern[4] = 128;  global step_pattern[5] = 96;
            global step_pattern[6] = 64;   global step_pattern[7] = 32;
        }
        
        // Advance sequencer timing
        if (global sequence_active == 1) {
            global step_counter = global step_counter + 1;
            if (global step_counter >= step_length) {
                global step_counter = 0;
                global current_step = global current_step + 1;
                if (global current_step >= pattern_length) {
                    global current_step = 0;
                }
            }
        }
        
        // Get current pattern value
        pattern_value = (int)global step_pattern[global current_step];
        
        // Map pattern value to filter parameters
        cutoff_freq = 200 + ((pattern_value * 1800) >> 8);     // 200-2000 Hz
        resonance = 256 + ((pattern_value * 1280) >> 8);       // 256-1536
        
        // Read input sample
        input_sample = (int)global signal[0];
        
        // Apply sequenced filter
        filtered_sample = cutoff_freq + 
            (((input_sample - cutoff_freq) * resonance) >> 11);
        
        // Limit filter output
        if (filtered_sample > 2047) filtered_sample = 2047;
        if (filtered_sample < -2047) filtered_sample = -2047;
        
        // Apply additional processing based on pattern
        output_sample = filtered_sample;
        if (pattern_value > 200) {
            // High pattern values: add subtle distortion
            if (output_sample > 1536) {
                output_sample = 1536 + ((output_sample - 1536) >> 2);
            }
            if (output_sample < -1536) {
                output_sample = -1536 + ((output_sample + 1536) >> 2);
            }
        }
        
        // Prevent clipping
        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        
        // Output processed signal
        global signal[0] = output_sample;
        global signal[1] = output_sample;
        
        // Display sequencer state on LEDs
        global displayLEDs[0] = global current_step << 5;    // Current step position
        global displayLEDs[1] = pattern_value;               // Current pattern value
        global displayLEDs[2] = pattern_type << 6;           // Pattern type
        if (global sequence_active == 1) {
            global displayLEDs[3] = 255;  // Active indicator
        } else {
            global displayLEDs[3] = 0;    // Inactive indicator
        }
        
        yield();
    }
}
```

## How It Works

**Step Sequencing**: Pre-programmed parameter values advance automatically over time, creating rhythmic parameter changes.

**Pattern Types**: Different mathematical patterns create different musical effects:
- Rising: Gradual build-up
- Alternating: Rhythmic on/off effect
- Random: Unpredictable variation
- Falling: Gradual wind-down

**Timing Control**: Sequence speed parameter controls how fast steps advance. Faster = more rapid changes.

**Pattern Length**: Adjustable from 1-8 steps for different phrase lengths.

**Parameter Control**:
- **Knob 1**: Sequence speed (0-255, fast to slow)
- **Knob 2**: Pattern length (1-8 steps)
- **Knob 3**: Pattern type (0-3 types)
- **Knob 4**: Sequence enable (on/off)

## Try These Settings

```impala
// Fast rhythmic filter
params[0] = 200;  // Fast speed
params[1] = 64;   // 3-step pattern
params[2] = 64;   // Alternating pattern
params[3] = 200;  // Sequence on

// Slow evolution
params[0] = 50;   // Slow speed
params[1] = 255;  // 8-step pattern
params[2] = 0;    // Rising pattern
params[3] = 200;  // Sequence on

// Random variations
params[0] = 128;  // Medium speed
params[1] = 160;  // 6-step pattern
params[2] = 128;  // Random pattern
params[3] = 200;  // Sequence on

// Sequence off (manual control)
params[0] = 100;  // Any speed
params[1] = 100;  // Any length
params[2] = 100;  // Any pattern
params[3] = 64;   // Sequence off
```

## Understanding Automation Sequencing

**Musical Timing**: Sequences create musical phrases and rhythmic interest beyond static parameter settings.

**Pattern Design**: Good patterns have musical logic - rises, falls, repetition, and variation.

**Tempo Relationship**: Sequence timing should relate to musical tempo for best results.

**Parameter Choice**: Different parameters create different musical effects when sequenced.

## Try These Changes

- **Multiple sequences**: Run different patterns on different parameters simultaneously
- **Swing timing**: Add rhythmic swing by varying step lengths
- **Pattern chains**: Link multiple patterns together for longer sequences
- **External sync**: Sync sequence timing to external clock or tempo

## Related Techniques

- **[Parameter Smoothing](parameter-smoothing.md)**: Smooth sequence step transitions
- **[Macro Controls](macro-controls.md)**: Sequence macro parameters for complex changes
- **[MIDI CC Mapping](midi-cc-mapping.md)**: External control of sequence parameters

---
*Part of the [Permut8 Cookbook](../index.md) series*