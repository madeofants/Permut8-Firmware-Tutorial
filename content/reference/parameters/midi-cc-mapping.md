# MIDI CC Mapping

*Parameter automation and external control concepts*

## What This Does

Demonstrates parameter automation and external control concepts that can be applied to MIDI CC mapping or other automation sources. Shows how to create responsive parameter control with curves and scaling.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Control source value (0-255)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Target parameter select (0-255)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Response curve type (0-255)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Scale amount (0-255)

**Core Techniques:**
- **Parameter automation**: Dynamic parameter control
- **Response curves**: Linear, exponential, logarithmic mapping
- **Scale factors**: Adjust control sensitivity
- **Multi-target control**: One source controls multiple parameters

**Key Concepts:** External control, parameter automation, curve shaping, control scaling

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


global int control_value = 128
global int target_param = 0
global int curve_type = 0
global int scale_factor = 128

function process()
locals int control_input, int param_select, int curve_select, int scale_input, int scaled_value, int output_value, int cutoff_freq, int resonance, int input_sample, int filtered_sample, int output_sample
{
    loop {

        control_input = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];
        param_select = (int)global (int)global params[SWITCHES_PARAM_INDEX] >> 5;
        curve_select = (int)global (int)global params[OPERATOR_1_PARAM_INDEX] >> 6;
        scale_input = (int)global (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
        

        if (curve_select == 0) {

            scaled_value = control_input;
            
        } else if (curve_select == 1) {

            scaled_value = (control_input * control_input) >> 8;
            
        } else if (curve_select == 2) {

            if (control_input < 16) {
                scaled_value = control_input << 2;
            } else if (control_input < 64) {
                scaled_value = 64 + ((control_input - 16) << 1);
            } else {
                scaled_value = 160 + (control_input - 64);
            }
            
        } else {

            scaled_value = 255 - control_input;
        }
        

        output_value = (scaled_value * scale_input) >> 8;
        

        if (param_select == 0) {

            cutoff_freq = 200 + ((output_value * 1800) >> 8);
            resonance = 512;
            
        } else if (param_select == 1) {

            cutoff_freq = 1000;
            resonance = 256 + ((output_value * 1280) >> 8);
            
        } else if (param_select == 2) {

            cutoff_freq = 200 + ((output_value * 1800) >> 8);
            resonance = 256 + ((output_value * 640) >> 8);
            
        } else {

            cutoff_freq = 1000;
            resonance = 512;
        }
        

        input_sample = (int)global signal[0];
        

        filtered_sample = cutoff_freq + 
            (((input_sample - cutoff_freq) * resonance) >> 11);
        

        if (filtered_sample > 2047) filtered_sample = 2047;
        if (filtered_sample < -2047) filtered_sample = -2047;
        

        output_sample = (filtered_sample * (128 + (output_value >> 1))) >> 8;
        

        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        

        global signal[0] = output_sample;
        global signal[1] = output_sample;
        

        global displayLEDs[0] = control_input;
        global displayLEDs[1] = param_select << 5;
        global displayLEDs[2] = curve_select << 6;
        global displayLEDs[3] = output_value;
        
        yield();
    }
}

```

## How It Works

**Control Source**: Parameter 0 acts as automation input (could be mapped to MIDI CC, envelope, LFO, etc.)

**Response Curves**: Different mathematical curves change how control input affects output:
- Linear: Direct 1:1 mapping
- Exponential: More control at low values
- Logarithmic: More control at high values
- Inverted: Reverse direction

**Parameter Targeting**: Select which parameter(s) the control source affects.

**Scale Factor**: Adjusts sensitivity and range of automated control.

**Parameter Control**:
- **Knob 1**: Control source input (automation value)
- **Knob 2**: Target parameter selection (0-7)
- **Knob 3**: Response curve type (0-3)
- **Knob 4**: Scale factor (control sensitivity)

## Try These Settings

```impala

(int)global params[CLOCK_FREQ_PARAM_INDEX] = 180;
(int)global params[SWITCHES_PARAM_INDEX] = 0;
(int)global params[OPERATOR_1_PARAM_INDEX] = 0;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 100;
(int)global params[SWITCHES_PARAM_INDEX] = 32;
(int)global params[OPERATOR_1_PARAM_INDEX] = 64;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 150;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 150;
(int)global params[SWITCHES_PARAM_INDEX] = 64;
(int)global params[OPERATOR_1_PARAM_INDEX] = 128;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 100;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;
(int)global params[SWITCHES_PARAM_INDEX] = 96;
(int)global params[OPERATOR_1_PARAM_INDEX] = 192;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 255;
```

## Understanding Parameter Automation

**External Control**: Think beyond knobs - automation can come from envelopes, LFOs, sequencers, or MIDI.

**Response Curves**: Linear feels technical, exponential/logarithmic feel more musical and natural.

**Multi-Parameter Control**: One automation source can affect multiple parameters simultaneously.

**Performance Control**: Design automation for real-time musical expression.

## Try These Changes

- **Bipolar control**: Center = no effect, extremes = opposite directions
- **Quantized control**: Snap to specific values (notes, rhythms)
- **Cross-parameter coupling**: One parameter affects another's response
- **Tempo-synced automation**: Sync control changes to musical timing

## Related Techniques

- **[Parameter Smoothing](parameter-smoothing.md)**: Smooth automated parameter changes
- **[Macro Controls](macro-controls.md)**: Group parameters for automation
- **[Read Knobs](read-knobs.md)**: Basic parameter input techniques

---
*Part of the [Permut8 Cookbook](../index.md) series*