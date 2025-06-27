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


global int phase_a = 0
global int phase_b = 0
global int crossfade_position = 128
global int curve_type = 0


global array equal_power_cos[16] = {255, 252, 245, 234, 219, 200, 178, 153, 
                                   126, 98, 70, 42, 16, 0, 0, 0}
global array equal_power_sin[16] = {0, 42, 70, 98, 126, 153, 178, 200,
                                   219, 234, 245, 252, 255, 255, 255, 255}

function process()
locals signal_a_level, signal_b_level, crossfade_pos, curve_select, signal_a, signal_b, gain_a, gain_b, output_a, output_b, mixed_output, table_index, input_sample
{
    loop {

        signal_a_level = params[CLOCK_FREQ_PARAM_INDEX];
        signal_b_level = params[SWITCHES_PARAM_INDEX];
        crossfade_pos = params[OPERATOR_1_PARAM_INDEX];
        curve_select = params[OPERAND_1_HIGH_PARAM_INDEX];
        


        global phase_a = global phase_a + (signal_a_level + 32);
        if (global phase_a >= 2048) global phase_a = global phase_a - 2048;
        
        if (global phase_a < 512) {
            signal_a = (global phase_a << 2);
        } else if (global phase_a < 1536) {
            signal_a = 2047 - ((global phase_a - 512) << 1);
        } else {
            signal_a = -2047 + ((global phase_a - 1536) << 2);
        }
        

        global phase_b = global phase_b + (signal_b_level + 16);
        if (global phase_b >= 2048) global phase_b = global phase_b - 2048;
        signal_b = global phase_b - 1024;
        

        if (curve_select > 128) {

            table_index = crossfade_pos >> 4;
            if (table_index > 15) table_index = 15;
            
            gain_a = global equal_power_cos[table_index];
            gain_b = global equal_power_sin[table_index];
            
        } else {

            gain_a = 255 - crossfade_pos;
            gain_b = crossfade_pos;
        }
        

        output_a = (signal_a * gain_a) >> 8;
        output_b = (signal_b * gain_b) >> 8;
        

        mixed_output = output_a + output_b;
        

        if (mixed_output > 2047) mixed_output = 2047;
        if (mixed_output < -2047) mixed_output = -2047;
        

        global signal[0] = mixed_output;
        global signal[1] = mixed_output;
        

        global displayLEDs[0] = gain_a;
        global displayLEDs[1] = gain_b;
        global displayLEDs[2] = crossfade_pos;
        if (curve_select > 128) {
            global displayLEDs[3] = 255;
        } else {
            global displayLEDs[3] = 64;
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

params[CLOCK_FREQ_PARAM_INDEX] = 64;
params[SWITCHES_PARAM_INDEX] = 128;
params[OPERATOR_1_PARAM_INDEX] = 128;
params[OPERAND_1_HIGH_PARAM_INDEX] = 64;


params[CLOCK_FREQ_PARAM_INDEX] = 80;
params[SWITCHES_PARAM_INDEX] = 120;
params[OPERATOR_1_PARAM_INDEX] = 200;
params[OPERAND_1_HIGH_PARAM_INDEX] = 200;


params[CLOCK_FREQ_PARAM_INDEX] = 100;
params[SWITCHES_PARAM_INDEX] = 160;
params[OPERATOR_1_PARAM_INDEX] = 0;
params[OPERAND_1_HIGH_PARAM_INDEX] = 180;


params[CLOCK_FREQ_PARAM_INDEX] = 32;
params[SWITCHES_PARAM_INDEX] = 200;
params[OPERATOR_1_PARAM_INDEX] = 128;
params[OPERAND_1_HIGH_PARAM_INDEX] = 220;
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
