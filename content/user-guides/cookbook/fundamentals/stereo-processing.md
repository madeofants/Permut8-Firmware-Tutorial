# Stereo Processing

*Control stereo field width and channel relationships*

## What This Does

Stereo processing manipulates the relationship between left and right audio channels to create spatial effects, control stereo width, and position sounds in the stereo field.

## Quick Reference

**Essential Parameters:**
- `params[0]`: Panning position (0-255, left to right)
- `params[1]`: Stereo width (0-255, mono to wide)
- `params[2]`: Channel routing (0-255, normal to swapped)

**Core Techniques:**
- **Panning**: Position mono signals in stereo field
- **Width control**: Adjust stereo image from mono to wide
- **Mid-side processing**: Separate center from sides
- **Channel routing**: Swap or mix left/right channels

**Key Concepts:** Spatial positioning, stereo field, mid-side encoding, channel relationships

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

function process()
locals int pan_position, int stereo_width, int channel_mode, int left_input, int right_input, int mid_signal, int side_signal, int left_gain, int right_gain, int mono_input, int output_left, int output_right, int panned_left, int panned_right, int width_left, int width_right
{
    loop {
        // Read parameters
        pan_position = (int)global params[0];    // 0-255 panning
        stereo_width = (int)global params[1];    // 0-255 width control
        channel_mode = (int)global params[2];    // 0-255 routing mode
        
        // Store input signals
        left_input = (int)global signal[0];
        right_input = (int)global signal[1];
        
        // Create mono signal from stereo input
        mono_input = (left_input + right_input) >> 1;
        
        // Calculate mid and side signals
        mid_signal = (left_input + right_input) >> 1;      // Center information
        side_signal = (left_input - right_input) >> 1;    // Stereo information
        
        // Apply stereo width control to side signal
        side_signal = (side_signal * stereo_width) >> 8;
        
        // Calculate panning gains (simple linear panning)
        left_gain = 255 - pan_position;   // More left as pan decreases
        right_gain = pan_position;        // More right as pan increases
        
        // Apply panning to mono signal
        panned_left = (mono_input * left_gain) >> 8;
        panned_right = (mono_input * right_gain) >> 8;
        
        // Reconstruct stereo from mid/side with width control
        width_left = mid_signal + side_signal;
        width_right = mid_signal - side_signal;
        
        // Select processing mode based on channel_mode parameter
        if (channel_mode < 64) {
            // Mode 0: Panning mode (mono input positioned in stereo field)
            output_left = panned_left;
            output_right = panned_right;
            
        } else if (channel_mode < 128) {
            // Mode 1: Width control mode (adjust stereo width)
            output_left = width_left;
            output_right = width_right;
            
        } else if (channel_mode < 192) {
            // Mode 2: Channel swap mode
            output_left = right_input;
            output_right = left_input;
            
        } else {
            // Mode 3: Mid-side monitor mode (mid on left, side on right)
            output_left = mid_signal;
            output_right = side_signal;
        }
        
        // Prevent clipping
        if (output_left > 2047) output_left = 2047;
        if (output_left < -2047) output_left = -2047;
        if (output_right > 2047) output_right = 2047;
        if (output_right < -2047) output_right = -2047;
        
        // Output processed signals
        global signal[0] = output_left;
        global signal[1] = output_right;
        
        // Show processing activity on LEDs
        global displayLEDs[0] = pan_position;                    // Show pan position
        global displayLEDs[1] = stereo_width;                   // Show width setting
        global displayLEDs[2] = channel_mode >> 2;              // Show current mode
        
        // Show stereo content (absolute value without abs function)
        if (side_signal >= 0) {
            global displayLEDs[3] = side_signal >> 3;
        } else {
            global displayLEDs[3] = (-side_signal) >> 3;
        }
        
        yield();
    }
}
```

## How It Works

**Mid-Side Processing**: Separating audio into Mid (center) and Side (stereo) components allows independent control. Mid = (L+R)/2 contains vocals and center-panned elements. Side = (L-R)/2 contains stereo width and spatial information.

**Panning Laws**: Linear panning simply adjusts left/right levels, but can create a "hole in the middle" effect. Equal-power panning maintains constant loudness as sounds move across the stereo field.

**Width Control**: Adjusting the Side signal controls stereo width. Width=0 creates mono, Width=1 preserves original stereo, Width>1 creates enhanced stereo.

**Channel Routing**: Different processing modes handle various stereo tasks - panning mono signals, adjusting width of stereo signals, swapping channels, or monitoring mid/side content.

**Parameter Control**:
- **Control 1**: Pan position or processing parameter
- **Control 2**: Stereo width or processing mode
- **Control 3**: Processing mode or channel routing

## Try These Settings

```impala
// Mono to stereo panning
params[0] = 128;  // Center pan
params[1] = 128;  // Normal width
params[2] = 32;   // Panning mode

// Stereo width adjustment
params[0] = 64;   // Wide left
params[1] = 200;  // Increased width
params[2] = 96;   // Width control mode

// Channel swap
params[0] = 128;  // Any position
params[1] = 128;  // Any width
params[2] = 160;  // Swap mode

// Mid-side monitoring
params[0] = 128;  // Any position
params[1] = 128;  // Any width
params[2] = 224;  // Monitor mode
```

## Understanding Stereo Processing

**Mid-Side Encoding**: Mid signal contains center-panned content (vocals, bass, kick drum). Side signal contains stereo spread content (reverb, wide instruments, ambience).

**Width vs Pan**: Panning positions mono signals in the stereo field. Width control adjusts how wide existing stereo content appears.

**Phase Relationship**: Left and right channels can be in-phase (mono-like) or out-of-phase (wide stereo). Extreme width settings can cause phase cancellation on mono systems.

**Processing Modes**: Different modes handle different stereo tasks efficiently within a single processor.

## Try These Changes

- **Auto-width**: Automatically adjust width based on signal correlation
- **Frequency-dependent width**: Make bass more centered, highs wider
- **Stereo enhancement**: Add subtle width to mono sources
- **Phase correlation monitoring**: Prevent mono compatibility issues

## Related Techniques

- **[Parameter Mapping](parameter-mapping.md)**: Control stereo parameters smoothly
- **[Basic Filter](basic-filter.md)**: Frequency-dependent stereo processing

---
*Part of the [Permut8 Cookbook](../index.md) series*