# Simple Reverb

*Create spacious reverb effects using delay and feedback*

## What This Does

Creates basic reverb by using multiple delay lines with feedback to simulate the sound of audio bouncing around a room. Produces everything from subtle room ambience to dramatic hall reverberation.

## Quick Reference

**Essential Parameters:**
- `params[CLOCK_FREQ_PARAM_INDEX]`: Room size (0-255, delay time)
- `params[SWITCHES_PARAM_INDEX]`: Decay time (0-255, how long reverb lasts)
- `params[OPERATOR_1_PARAM_INDEX]`: Damping (0-255, high frequency rolloff)
- `params[OPERAND_1_HIGH_PARAM_INDEX]`: Dry/wet mix (0-255, blend control)

**Key Concepts:** Multiple delays, feedback loops, frequency damping, spatial simulation

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
global int clock                 // Sample counter for timing
global array signal[2]          // Left/Right audio samples
global array params[PARAM_COUNT] // Parameter values (0-255)
global array displayLEDs[4]     // LED displays
global int clockFreqLimit        // Current clock frequency limit

// Simple reverb state
global array temp_buffer[2]     // Temporary buffer for memory operations
global int write_pos1 = 0       // Write position for first delay
global int write_pos2 = 100     // Write position for second delay (offset)
global int write_pos3 = 200     // Write position for third delay (offset)
global int damping_state = 0    // Simple damping filter state

function process()
locals int room_size, int decay, int damping, int mix, int delay1_time, int delay2_time, int delay3_time, int delayed1, int delayed2, int delayed3, int reverb_sum, int reverb_out, int output, int new_reverb
{
    loop {
        // Read parameters
        room_size = ((int)global params[CLOCK_FREQ_PARAM_INDEX] >> 2) + 10;   // 10-73 delay range
        decay = ((int)global params[SWITCHES_PARAM_INDEX] >> 1) + 64;       // 64-191 feedback amount
        damping = ((int)global params[OPERATOR_1_PARAM_INDEX] >> 4) + 1;      // 1-16 damping strength
        mix = (int)global params[OPERAND_1_HIGH_PARAM_INDEX];                     // 0-255 dry/wet mix
        
        // Calculate delay times (different for each delay line)
        delay1_time = room_size;
        delay2_time = room_size + 17;  // Prime number offset
        delay3_time = room_size + 31;  // Different prime offset
        
        // Read from first delay line
        read(global write_pos1 - delay1_time, 1, global temp_buffer);
        delayed1 = (int)global temp_buffer[0];
        
        // Read from second delay line  
        read(global write_pos2 - delay2_time, 1, global temp_buffer);
        delayed2 = (int)global temp_buffer[0];
        
        // Read from third delay line
        read(global write_pos3 - delay3_time, 1, global temp_buffer);
        delayed3 = (int)global temp_buffer[0];
        
        // Sum delayed signals for reverb
        reverb_sum = (delayed1 + delayed2 + delayed3) / 3;
        
        // Simple damping filter (reduces high frequencies over time)
        global damping_state = global damping_state + ((reverb_sum - global damping_state) >> damping);
        reverb_out = global damping_state;
        
        // Add input and feedback to create new reverb content
        new_reverb = (int)global signal[0] + ((reverb_out * decay) >> 8);
        
        // Prevent runaway feedback
        if (new_reverb > 2047) new_reverb = 2047;
        if (new_reverb < -2047) new_reverb = -2047;
        
        // Write new reverb to all delay lines (with slight variations)
        global temp_buffer[0] = new_reverb;
        global temp_buffer[1] = new_reverb;
        write(global write_pos1, 1, global temp_buffer);
        
        global temp_buffer[0] = new_reverb + (delayed2 >> 4);  // Cross-couple
        write(global write_pos2, 1, global temp_buffer);
        
        global temp_buffer[0] = new_reverb - (delayed1 >> 4);  // Cross-couple opposite
        write(global write_pos3, 1, global temp_buffer);
        
        // Mix dry and wet signals
        output = (((int)global signal[0] * (255 - mix)) + (reverb_out * mix)) >> 8;
        
        // Prevent clipping
        if (output > 2047) output = 2047;
        if (output < -2047) output = -2047;
        
        // Output result
        global signal[0] = output;
        global signal[1] = output;
        
        // Show activity on LEDs
        global displayLEDs[0] = room_size << 2;
        global displayLEDs[1] = (decay - 64) << 2;
        global displayLEDs[2] = (reverb_out >> 3) + 128;  // Show reverb level
        global displayLEDs[3] = (mix >> 2);
        
        // Update write positions
        global write_pos1 = global write_pos1 + 1;
        global write_pos2 = global write_pos2 + 1;
        global write_pos3 = global write_pos3 + 1;
        
        yield();
    }
}

```

## How It Works

**Multiple Delay Lines**: Three delay lines with different lengths create complex echo patterns.

**Feedback Control**: The decay parameter controls how much of the reverb feeds back, determining reverb length.

**Cross-Coupling**: Delay lines feed into each other slightly, creating more complex reverb texture.

**Simple Damping**: A low-pass filter reduces high frequencies over time, simulating natural absorption.

**Parameter Control**:
- **Control 1**: Room size (larger = longer delays, bigger space feel)
- **Control 2**: Decay time (higher = longer reverb tail)
- **Control 3**: Damping (higher = darker, more natural sound)
- **Control 4**: Dry/wet mix (blend original with reverb)

## Try These Settings

```impala
// Small room
global params[CLOCK_FREQ_PARAM_INDEX] = 64;   // Small size
global params[SWITCHES_PARAM_INDEX] = 128;  // Medium decay
global params[OPERATOR_1_PARAM_INDEX] = 128;  // Some damping
global params[OPERAND_1_HIGH_PARAM_INDEX] = 100;  // Subtle mix

// Large hall
global params[CLOCK_FREQ_PARAM_INDEX] = 200;  // Large size
global params[SWITCHES_PARAM_INDEX] = 200;  // Long decay
global params[OPERATOR_1_PARAM_INDEX] = 64;   // Light damping
global params[OPERAND_1_HIGH_PARAM_INDEX] = 150;  // More noticeable

// Ambient space
global params[CLOCK_FREQ_PARAM_INDEX] = 255;  // Maximum size
global params[SWITCHES_PARAM_INDEX] = 240;  // Very long decay
global params[OPERATOR_1_PARAM_INDEX] = 180;  // Heavy damping
global params[OPERAND_1_HIGH_PARAM_INDEX] = 180;  // Mostly wet
```

## Try These Changes

- **Early reflections**: Add a fourth delay line with very short delay for room reflections
- **Stereo reverb**: Use different delay times for left and right channels
- **Modulation**: Slightly vary delay times with LFO for chorus-like movement
- **Multiple rooms**: Switch between different delay time sets

## How Reverb Works

**Natural Reverb**: When sound is produced in a space, it bounces off walls, ceiling, and objects, creating thousands of echoes that blend together.

**Digital Simulation**: We approximate this with several delay lines that simulate different path lengths the sound takes bouncing around the room.

**Feedback**: Each bounce is slightly quieter, which we simulate by feeding some output back to the input with reduced volume.

**Frequency Response**: High frequencies are absorbed more than low frequencies, which we simulate with the damping filter.

## Related Techniques

- **[Make a Delay](make-a-delay.md)**: Basic delay fundamentals
- **[Basic Filter](../fundamentals/basic-filter.md)**: Filtering for damping

---
*Part of the [Permut8 Cookbook](../index.md) series*