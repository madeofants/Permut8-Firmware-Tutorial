# MIDI CC Mapping

*Parameter automation and external control concepts*

## What This Does

Demonstrates parameter automation and external control concepts that can be applied to MIDI CC mapping or other automation sources. Shows how to create responsive parameter control with curves and scaling.

## Quick Reference

**Essential Parameters:**
- `params[0]`: Control source value (0-255)
- `params[1]`: Target parameter select (0-255)
- `params[2]`: Response curve type (0-255)
- `params[3]`: Scale amount (0-255)

**Core Techniques:**
- **Parameter automation**: Dynamic parameter control
- **Response curves**: Linear, exponential, logarithmic mapping
- **Scale factors**: Adjust control sensitivity
- **Multi-target control**: One source controls multiple parameters

**Key Concepts:** External control, parameter automation, curve shaping, control scaling

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Parameter automation state
global int control_value = 128     // Current control value
global int target_param = 0        // Which parameter to control
global int curve_type = 0          // Response curve type
global int scale_factor = 128      // Control scale factor

function process()
locals int control_input, int param_select, int curve_select, int scale_input, int scaled_value, int output_value, int cutoff_freq, int resonance, int input_sample, int filtered_sample, int output_sample
{
    loop {
        // Read automation control inputs
        control_input = (int)global params[0];     // 0-255 control source
        param_select = (int)global params[1] >> 5; // 0-7 parameter selection  
        curve_select = (int)global params[2] >> 6; // 0-3 curve types
        scale_input = (int)global params[3];       // 0-255 scale factor
        
        // Apply response curve to control input
        if (curve_select == 0) {
            // Linear response
            scaled_value = control_input;
            
        } else if (curve_select == 1) {
            // Exponential response (squared)
            scaled_value = (control_input * control_input) >> 8;
            
        } else if (curve_select == 2) {
            // Logarithmic response (square root approximation)
            if (control_input < 16) {
                scaled_value = control_input << 2;
            } else if (control_input < 64) {
                scaled_value = 64 + ((control_input - 16) << 1);
            } else {
                scaled_value = 160 + (control_input - 64);
            }
            
        } else {
            // Inverted linear response
            scaled_value = 255 - control_input;
        }
        
        // Apply scale factor
        output_value = (scaled_value * scale_input) >> 8;
        
        // Map to target parameters based on selection
        if (param_select == 0) {
            // Control filter cutoff
            cutoff_freq = 200 + ((output_value * 1800) >> 8);  // 200-2000 Hz
            resonance = 512;  // Fixed resonance
            
        } else if (param_select == 1) {
            // Control filter resonance
            cutoff_freq = 1000;  // Fixed cutoff
            resonance = 256 + ((output_value * 1280) >> 8);    // 256-1536
            
        } else if (param_select == 2) {
            // Control both cutoff and resonance together
            cutoff_freq = 200 + ((output_value * 1800) >> 8);
            resonance = 256 + ((output_value * 640) >> 8);     // 256-896
            
        } else {
            // Default: moderate settings
            cutoff_freq = 1000;
            resonance = 512;
        }
        
        // Read input sample
        input_sample = (int)global signal[0];
        
        // Apply simple filter using automated parameters
        filtered_sample = cutoff_freq + 
            (((input_sample - cutoff_freq) * resonance) >> 11);
        
        // Limit filter output
        if (filtered_sample > 2047) filtered_sample = 2047;
        if (filtered_sample < -2047) filtered_sample = -2047;
        
        // Apply volume control based on automation
        output_sample = (filtered_sample * (128 + (output_value >> 1))) >> 8;
        
        // Prevent clipping
        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        
        // Output processed signal
        global signal[0] = output_sample;
        global signal[1] = output_sample;
        
        // Display automation state on LEDs
        global displayLEDs[0] = control_input;          // Control source value
        global displayLEDs[1] = param_select << 5;      // Parameter selection
        global displayLEDs[2] = curve_select << 6;      // Curve type
        global displayLEDs[3] = output_value;           // Final automated value
        
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
// Linear cutoff control
params[0] = 180;  // High control value
params[1] = 0;    // Control cutoff
params[2] = 0;    // Linear curve
params[3] = 200;  // High sensitivity

// Exponential resonance control
params[0] = 100;  // Medium control value
params[1] = 32;   // Control resonance
params[2] = 64;   // Exponential curve
params[3] = 150;  // Medium sensitivity

// Combined control with log curve
params[0] = 150;  // Control value
params[1] = 64;   // Combined control
params[2] = 128;  // Logarithmic curve
params[3] = 100;  // Lower sensitivity

// Inverted control
params[0] = 200;  // High input
params[1] = 96;   // Any parameter
params[2] = 192;  // Inverted curve
params[3] = 255;  // Maximum sensitivity
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