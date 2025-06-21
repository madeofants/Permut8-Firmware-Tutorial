# Granular Synthesis

*Create textural effects by chopping audio into tiny grains and playing them back*

## What This Does

Creates granular synthesis by capturing audio into a buffer and playing back small chunks (grains) with controllable position and size. Produces everything from subtle textures to dramatic time-stretching and glitched effects.

## Quick Reference

**Essential Parameters:**
- `params[CLOCK_FREQ_PARAM_INDEX]`: Grain size (20-100 samples, controls grain duration)
- `params[SWITCHES_PARAM_INDEX]`: Playback position (0-255, where in buffer to read)
- `params[OPERATOR_1_PARAM_INDEX]`: Grain trigger rate (0-255, how often new grains start)
- `params[OPERAND_1_HIGH_PARAM_INDEX]`: Dry/wet mix (0-255, blend control)

**Key Concepts:** Circular buffering, grain windowing, position control, texture creation

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
extern native read              // Read from delay line memory
extern native write             // Write to delay line memory

// Standard global variables
global int clock = 0            // Sample counter for timing
global array signal[2]          // Left/Right audio samples
global array params[PARAM_COUNT] // Parameter values (0-255)
global array displayLEDs[4]     // LED displays
global int clockFreqLimit = 132300 // Current clock frequency limit

// Simple granular state
global array temp_buffer[2]     // Temporary buffer for memory operations
global int write_pos = 0        // Current write position
global int grain_pos = 0        // Current grain read position
global int grain_counter = 0    // Current position within grain
global int grain_trigger = 0    // Timer for grain triggering
const int BUFFER_SIZE = 2048    // Circular buffer size for granular processing

function process()
locals int grain_size, int position, int trigger_rate, int mix, int grain_sample_l, int grain_sample_r, int output_l, int output_r, int envelope, int half_size, int read_pos, int offset
{
    loop {
        // Read parameters
        grain_size = ((int)global params[CLOCK_FREQ_PARAM_INDEX] >> 2) + 20;  // 20-83 samples
        position = (int)global params[SWITCHES_PARAM_INDEX];                // 0-255 position
        trigger_rate = ((int)global params[OPERATOR_1_PARAM_INDEX] >> 3) + 1; // 1-32 rate
        mix = (int)global params[OPERAND_1_HIGH_PARAM_INDEX];                     // 0-255 mix
        
        // Safety bounds for grain size
        if (grain_size > 100) grain_size = 100;
        if (grain_size < 20) grain_size = 20;
        
        // Write current input to buffer (left channel)
        global temp_buffer[0] = global signal[0];
        write(global write_pos, 1, global temp_buffer);
        
        // Write current input to buffer (right channel at offset)
        global temp_buffer[0] = global signal[1];
        write(global write_pos + BUFFER_SIZE, 1, global temp_buffer);
        
        // Trigger new grain?
        global grain_trigger = global grain_trigger + 1;
        if (global grain_trigger >= trigger_rate) {
            global grain_trigger = 0;
            
            // Calculate grain start position based on parameter with safety bounds
            offset = ((position * (BUFFER_SIZE >> 2)) >> 8) + grain_size;
            global grain_pos = (global write_pos - offset + BUFFER_SIZE) % BUFFER_SIZE;
            global grain_counter = 0;
        }
        
        // Generate grain output
        if (global grain_counter < grain_size) {
            // Calculate safe read position with circular buffer wrapping
            read_pos = (global grain_pos + global grain_counter) % BUFFER_SIZE;
            
            // Read grain sample from buffer (left channel)
            read(read_pos, 1, global temp_buffer);
            grain_sample_l = (int)global temp_buffer[0];
            
            // Read grain sample from buffer (right channel)
            read(read_pos + BUFFER_SIZE, 1, global temp_buffer);
            grain_sample_r = (int)global temp_buffer[0];
            
            // Simple envelope (triangle window for smooth edges)
            half_size = grain_size >> 1;
            if (half_size == 0) half_size = 1;  // Prevent division by zero
            
            if (global grain_counter < half_size) {
                // Attack half: ramp up (0-255 range)
                envelope = (global grain_counter * 255) / half_size;
            } else {
                // Release half: ramp down (0-255 range)
                envelope = ((grain_size - global grain_counter) * 255) / half_size;
            }
            
            // Apply envelope to grain samples
            grain_sample_l = (grain_sample_l * envelope) >> 8;
            grain_sample_r = (grain_sample_r * envelope) >> 8;
            global grain_counter = global grain_counter + 1;
        } else {
            grain_sample_l = 0;  // No grain playing
            grain_sample_r = 0;
        }
        
        // Mix dry and wet signals (stereo processing)
        output_l = ((int)global signal[0] * (255 - mix) + grain_sample_l * mix) >> 8;
        output_r = ((int)global signal[1] * (255 - mix) + grain_sample_r * mix) >> 8;
        
        // Prevent clipping
        if (output_l > 2047) output_l = 2047;
        if (output_l < -2047) output_l = -2047;
        if (output_r > 2047) output_r = 2047;
        if (output_r < -2047) output_r = -2047;
        
        // Output stereo result
        global signal[0] = output_l;
        global signal[1] = output_r;
        
        // Show activity on LEDs with proper scaling
        global displayLEDs[0] = (grain_size - 20) << 2;    // Grain size (offset and scaled)
        global displayLEDs[1] = (global grain_counter << 8) / grain_size;  // Grain progress (0-255)
        global displayLEDs[2] = position;                   // Position parameter
        global displayLEDs[3] = (mix >> 2);                 // Mix level
        
        // Update write position with circular buffer wrapping
        global write_pos = (global write_pos + 1) % BUFFER_SIZE;
        
        yield();
    }
}

```

## How It Works

**Buffer Capture**: Continuously writes incoming audio to a circular buffer using safe memory management with proper bounds checking.

**Grain Generation**: Periodically triggers new grains that read from different positions in the captured buffer using circular buffer arithmetic for safety.

**Triangle Envelope**: Uses a triangle window (0-255 range) to smooth grain edges and prevent clicks, with division-by-zero protection.

**Position Control**: Parameter controls where in the buffer grains are read from, creating time-stretch effects with safe memory addressing.

**Stereo Processing**: Independent left and right channel processing maintains stereo image during granular synthesis.

**Parameter Control**:
- **Control 1**: Grain size (larger = smoother, smaller = more granular)
- **Control 2**: Read position (different timing relationships)
- **Control 3**: Trigger rate (faster = denser texture)
- **Control 4**: Dry/wet mix (blend original with granular)

## Try These Settings

```impala
// Smooth texture
global params[CLOCK_FREQ_PARAM_INDEX] = 200;  // Large grains
global params[SWITCHES_PARAM_INDEX] = 64;   // Slight delay
global params[OPERATOR_1_PARAM_INDEX] = 128;  // Medium rate
global params[OPERAND_1_HIGH_PARAM_INDEX] = 128;  // 50% mix

// Glitchy texture
global params[CLOCK_FREQ_PARAM_INDEX] = 50;   // Small grains
global params[SWITCHES_PARAM_INDEX] = 200;  // Distant position
global params[OPERATOR_1_PARAM_INDEX] = 32;   // Fast triggers
global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;  // Mostly wet
```

## Try These Changes

- **Reverse grains**: Read grains backwards for different textures
- **Multiple grain voices**: Layer 2-3 grains with different positions
- **Pitch shifting**: Change grain playback speed
- **Stereo granular**: Different grain patterns for left/right channels

## Related Techniques

- **[Make a Delay](make-a-delay.md)**: Buffer management fundamentals
- **[Circular Buffer Guide](../fundamentals/circular-buffer-guide.md)**: Buffer techniques

---
*Part of the [Permut8 Cookbook](../index.md) series*