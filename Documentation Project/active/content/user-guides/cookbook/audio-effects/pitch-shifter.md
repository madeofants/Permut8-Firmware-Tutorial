# Pitch Shifter

*Simple pitch shifting using variable delay*

## What This Does

Creates basic pitch shifting by using a variable delay line with modulated read speed. This creates pitch changes by reading the delay buffer faster (higher pitch) or slower (lower pitch), similar to changing tape speed.

## Quick Reference

**Essential Parameters:**
- `params[0]`: Pitch shift (0-255, where 128 = no shift)
- `params[1]`: Buffer size (0-255, affects quality vs latency)
- `params[2]`: Smoothing (0-255, reduces glitches)
- `params[3]`: Dry/wet mix (0-255, blend control)

**Key Concepts:** Variable delay, read speed modulation, simple time-stretch, pitch-time relationship

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine
extern native read              // Read from delay line memory
extern native write             // Write to delay line memory

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Simple pitch shifter state
global array temp_buffer[2]     // Temporary buffer for memory operations
global int write_pos = 0        // Current write position
global int read_pos_frac = 0    // Fractional read position (16-bit fixed point)
global int last_sample_l = 0    // For smoothing left channel
global int last_sample_r = 0    // For smoothing right channel
const int MAX_BUFFER_SIZE = 4096 // Maximum delay buffer size

function process()
locals int pitch_shift
locals int buffer_size
locals int smoothing
locals int mix
locals int pitch_speed
locals int new_read_pos
locals int current_sample_l
locals int current_sample_r
locals int smoothed_sample_l
locals int smoothed_sample_r
locals int output_l
locals int output_r
locals int smooth_factor
{
    loop {
        // Read parameters
        pitch_shift = (int)global params[0];             // 0-255 pitch control
        buffer_size = ((int)global params[1] >> 2) + 32; // 32-95 buffer size
        smoothing = ((int)global params[2] >> 3) + 1;    // 1-32 smoothing
        mix = (int)global params[3];                     // 0-255 dry/wet mix
        
        // Safety bounds for buffer size
        if (buffer_size > 1000) buffer_size = 1000;
        
        // Write current input to delay buffer (left channel)
        global temp_buffer[0] = global signal[0];
        write(global write_pos, 1, global temp_buffer);
        
        // Write current input to delay buffer (right channel, offset location)
        global temp_buffer[0] = global signal[1];
        write(global write_pos + MAX_BUFFER_SIZE, 1, global temp_buffer);
        
        // Calculate pitch shift speed (improved mapping)
        // Map 0-255 to 0.5x-2.0x speed range, with 128 = 1.0x (unity)
        if (pitch_shift < 128) {
            pitch_speed = 128 + (pitch_shift >> 1);  // 128-191 (0.5x-0.75x)
        } else {
            pitch_speed = 128 + ((pitch_shift - 128) << 1);  // 128-384 (1.0x-2.0x)
        }
        
        // Update fractional read position with proper overflow handling
        global read_pos_frac = (global read_pos_frac + pitch_speed) & 65535;
        
        // Extract integer part for actual read position
        new_read_pos = global write_pos - (global read_pos_frac >> 8) - buffer_size;
        
        // Handle negative wraparound for circular buffer
        while (new_read_pos < 0) {
            new_read_pos = new_read_pos + MAX_BUFFER_SIZE;
        }
        
        // Read samples from delay buffer (left channel)
        read(new_read_pos, 1, global temp_buffer);
        current_sample_l = (int)global temp_buffer[0];
        
        // Read samples from delay buffer (right channel)
        read(new_read_pos + MAX_BUFFER_SIZE, 1, global temp_buffer);
        current_sample_r = (int)global temp_buffer[0];
        
        // Limit smoothing factor for reasonable range
        smooth_factor = smoothing & 7;  // Limit to 0-7 for reasonable smoothing
        
        // Simple smoothing to reduce glitches (left channel)
        smoothed_sample_l = global last_sample_l + ((current_sample_l - global last_sample_l) >> smooth_factor);
        global last_sample_l = smoothed_sample_l;
        
        // Simple smoothing to reduce glitches (right channel)
        smoothed_sample_r = global last_sample_r + ((current_sample_r - global last_sample_r) >> smooth_factor);
        global last_sample_r = smoothed_sample_r;
        
        // Gradual correction when read position drifts too far
        int position_diff = global write_pos - new_read_pos;
        if (position_diff > (buffer_size + 100)) {
            // Gradually correct instead of hard reset
            global read_pos_frac = global read_pos_frac - 256;
        }
        
        // Mix dry and wet signals (left channel)
        output_l = (((int)global signal[0] * (255 - mix)) + (smoothed_sample_l * mix)) >> 8;
        
        // Mix dry and wet signals (right channel)
        output_r = (((int)global signal[1] * (255 - mix)) + (smoothed_sample_r * mix)) >> 8;
        
        // Prevent clipping (left channel)
        if (output_l > 2047) output_l = 2047;
        if (output_l < -2047) output_l = -2047;
        
        // Prevent clipping (right channel)
        if (output_r > 2047) output_r = 2047;
        if (output_r < -2047) output_r = -2047;
        
        // Output stereo result
        global signal[0] = output_l;
        global signal[1] = output_r;
        
        // Show activity on LEDs with proper scaling
        global displayLEDs[0] = pitch_shift;                    // Pitch control
        global displayLEDs[1] = (global read_pos_frac >> 8);    // Read position (high byte)
        global displayLEDs[2] = (buffer_size - 32) << 2;       // Buffer size (offset and scaled)
        global displayLEDs[3] = (mix >> 2);                    // Mix level
        
        // Update write position with circular buffer wrapping
        global write_pos = (global write_pos + 1) % MAX_BUFFER_SIZE;
        
        yield();
    }
}
```

## How It Works

**Variable Delay**: Uses a delay buffer with a variable read position that moves at different speeds.

**Pitch Speed Control**: Reading faster creates higher pitch, reading slower creates lower pitch.

**Fractional Positioning**: Uses fixed-point arithmetic for smooth read position changes.

**Simple Smoothing**: Reduces glitches by interpolating between samples.

**Parameter Control**:
- **Knob 1**: Pitch shift (128 = normal, <128 = lower, >128 = higher)
- **Knob 2**: Buffer size (larger = better quality, more latency)  
- **Knob 3**: Smoothing (higher = smoother but less responsive, limited to reasonable range)
- **Knob 4**: Dry/wet mix (blend original with pitch-shifted)

**Stereo Processing**: Left and right channels processed independently for true stereo pitch shifting.

## Try These Settings

```impala
// Octave up
params[0] = 200;  // Fast read speed
params[1] = 128;  // Medium buffer
params[2] = 64;   // Some smoothing
params[3] = 200;  // Mostly wet

// Octave down
params[0] = 64;   // Slow read speed
params[1] = 180;  // Large buffer
params[2] = 128;  // More smoothing
params[3] = 180;  // Mostly wet

// Subtle detuning
params[0] = 140;  // Slightly fast
params[1] = 64;   // Small buffer
params[2] = 32;   // Light smoothing
params[3] = 128;  // 50% mix
```

## Limitations & Improvements

**Current Limitations**:
- Time stretching (pitch affects duration)
- Periodic glitches at buffer boundaries
- Limited pitch range before artifacts

**Possible Improvements**:
- **Windowing**: Add crossfading between buffer regions
- **Interpolation**: Better sample interpolation for smoother results
- **Multiple voices**: Overlap multiple delay lines for artifact reduction

## Try These Changes

- **Stereo pitch**: Different pitch amounts for left/right channels
- **LFO modulation**: Slowly vary pitch for vibrato effects
- **Harmonic pitch**: Add multiple pitch-shifted voices for chord effects
- **Feedback**: Add some output back to input for resonance

## Related Techniques

- **[Make a Delay](make-a-delay.md)**: Delay buffer fundamentals
- **[Chorus Effect](chorus-effect.md)**: Similar modulated delay concepts

---
*Part of the [Permut8 Cookbook](../index.md) series*