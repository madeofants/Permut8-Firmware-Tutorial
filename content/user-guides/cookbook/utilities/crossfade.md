# Crossfade

*Smooth transitions between two audio signals for seamless blending*

## What This Does

Crossfading enables smooth transitions between two audio signals, eliminating clicks and pops that occur with abrupt switching. Essential for professional-sounding transitions between oscillator waveforms, effects, or complete patches.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Signal A level (0-255)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Signal B level (0-255) 
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Crossfade position (0-255)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Curve type (0-255)

**Core Techniques:**
- **Linear crossfade**: Simple A/B mixing
- **Equal power crossfade**: Maintains consistent loudness
- **Curve shaping**: Different transition feels
- **Automated transitions**: Time-based morphing

**Key Concepts:** Equal power law, crossfade curves, signal blending, transition timing

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

// Crossfade system state
global int phase_a = 0              // Phase for oscillator A
global int phase_b = 0              // Phase for oscillator B
global int crossfade_position = 128  // Crossfade position (0-255)
global int curve_type = 0           // 0=linear, 1=equal power

// Equal power lookup table (scaled to 255)
global array equal_power_cos[16] = {255, 252, 245, 234, 219, 200, 178, 153, 
                                   126, 98, 70, 42, 16, 0, 0, 0}
global array equal_power_sin[16] = {0, 42, 70, 98, 126, 153, 178, 200,
                                   219, 234, 245, 252, 255, 255, 255, 255}

function process()
locals signal_a_level, signal_b_level, crossfade_pos, curve_select, signal_a, signal_b, gain_a, gain_b, output_a, output_b, mixed_output, table_index, input_sample
{
    loop {
        // Read control parameters
        signal_a_level = params[CLOCK_FREQ_PARAM_INDEX];    // Signal A level (0-255)
        signal_b_level = params[SWITCHES_PARAM_INDEX];    // Signal B level (0-255)
        crossfade_pos = params[OPERATOR_1_PARAM_INDEX];     // Crossfade position (0-255)
        curve_select = params[OPERAND_1_HIGH_PARAM_INDEX];      // Curve type (0-255)
        
        // Generate test signals (sine and sawtooth)
        // Signal A: Sine wave
        global phase_a = global phase_a + (signal_a_level + 32);  // Frequency control
        if (global phase_a >= 2048) global phase_a = global phase_a - 2048;
        
        if (global phase_a < 512) {
            signal_a = (global phase_a << 2);  // Rising edge
        } else if (global phase_a < 1536) {
            signal_a = 2047 - ((global phase_a - 512) << 1);  // Falling edge
        } else {
            signal_a = -2047 + ((global phase_a - 1536) << 2);  // Rising from bottom
        }
        
        // Signal B: Sawtooth wave
        global phase_b = global phase_b + (signal_b_level + 16);  // Different frequency
        if (global phase_b >= 2048) global phase_b = global phase_b - 2048;
        signal_b = global phase_b - 1024;  // Center around zero
        
        // Calculate crossfade gains based on curve type
        if (curve_select > 128) {
            // Equal power crossfade using lookup table
            table_index = crossfade_pos >> 4;  // Scale to 0-15 range
            if (table_index > 15) table_index = 15;
            
            gain_a = global equal_power_cos[table_index];
            gain_b = global equal_power_sin[table_index];
            
        } else {
            // Linear crossfade
            gain_a = 255 - crossfade_pos;  // Full A at pos=0
            gain_b = crossfade_pos;        // Full B at pos=255
        }
        
        // Apply crossfade gains
        output_a = (signal_a * gain_a) >> 8;  // Scale by gain_a
        output_b = (signal_b * gain_b) >> 8;  // Scale by gain_b
        
        // Mix the signals
        mixed_output = output_a + output_b;
        
        // Prevent clipping
        if (mixed_output > 2047) mixed_output = 2047;
        if (mixed_output < -2047) mixed_output = -2047;
        
        // Apply to audio output
        global signal[0] = mixed_output;
        global signal[1] = mixed_output;
        
        // Visual feedback on LEDs
        global displayLEDs[0] = gain_a;           // Signal A level
        global displayLEDs[1] = gain_b;           // Signal B level
        global displayLEDs[2] = crossfade_pos;    // Crossfade position
        if (curve_select > 128) {
            global displayLEDs[3] = 255;  // Equal power mode
        } else {
            global displayLEDs[3] = 64;   // Linear mode
        }
        
        yield();
    }
}

```

## How It Works

**Signal Generation**: Creates two different test signals (sine and sawtooth) that can be crossfaded between.

**Crossfade Curves**: Two different curve types:
- Linear: Simple A/B mixing, creates slight volume dip at center
- Equal power: Maintains consistent loudness throughout transition

**Equal Power Table**: Pre-calculated cosine/sine values that ensure the total power (gain_a² + gain_b²) remains constant.

**Parameter Control**:
- **Knob 1**: Signal A frequency/level
- **Knob 2**: Signal B frequency/level  
- **Knob 3**: Crossfade position (0=full A, 255=full B)
- **Knob 4**: Curve type (0-128=linear, 129-255=equal power)

## Try These Settings

```impala
// Linear crossfade between different frequencies
params[CLOCK_FREQ_PARAM_INDEX] = 64;   // Signal A: moderate frequency
params[SWITCHES_PARAM_INDEX] = 128;  // Signal B: higher frequency
params[OPERATOR_1_PARAM_INDEX] = 128;  // Center position
params[OPERAND_1_HIGH_PARAM_INDEX] = 64;   // Linear curve

// Equal power crossfade
params[CLOCK_FREQ_PARAM_INDEX] = 80;   // Signal A frequency
params[SWITCHES_PARAM_INDEX] = 120;  // Signal B frequency
params[OPERATOR_1_PARAM_INDEX] = 200;  // Mostly signal B
params[OPERAND_1_HIGH_PARAM_INDEX] = 200;  // Equal power curve

// Smooth transition demo
params[CLOCK_FREQ_PARAM_INDEX] = 100;  // Signal A
params[SWITCHES_PARAM_INDEX] = 160;  // Signal B
params[OPERATOR_1_PARAM_INDEX] = 0;    // Start with A, manually sweep to 255
params[OPERAND_1_HIGH_PARAM_INDEX] = 180;  // Equal power

// High contrast crossfade
params[CLOCK_FREQ_PARAM_INDEX] = 32;   // Low frequency A
params[SWITCHES_PARAM_INDEX] = 200;  // High frequency B
params[OPERATOR_1_PARAM_INDEX] = 128;  // Center position
params[OPERAND_1_HIGH_PARAM_INDEX] = 220;  // Equal power curve
```

## Understanding Crossfade Curves

**Linear Crossfade**: Simple addition where `gain_a = 255 - position` and `gain_b = position`. Creates a volume dip at the center position because the signals don't add constructively.

**Equal Power Crossfade**: Uses trigonometric relationships (cosine/sine) to maintain constant total energy. The gains follow curves where `gain_a² + gain_b² = constant`.

**Musical Applications**: Equal power is standard for professional mixing, while linear can create interesting creative effects with the center dip.

## Try These Changes

- **3-way crossfade**: Add a third signal and use two crossfade positions
- **Frequency-dependent crossfading**: Apply different crossfade curves to high/low frequencies
- **Automated crossfading**: Use an LFO or envelope to control crossfade position
- **Stereo crossfading**: Apply different crossfade positions to left/right channels

## Related Techniques

- **[Mix Multiple Signals](mix-multiple-signals.md)**: Combine more than two signals
- **[Input Monitoring](input-monitoring.md)**: Crossfade between input and generated signals
- **[Parameter Smoothing](../parameters/parameter-smoothing.md)**: Smooth crossfade position changes

---
*Part of the [Permut8 Cookbook](../index.md) series*
