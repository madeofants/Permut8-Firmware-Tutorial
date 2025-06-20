# Mix Multiple Signals

*Combine multiple audio sources with proper level management and headroom control*

## What This Does

Provides efficient multi-signal mixing techniques for combining oscillators, effects returns, or layered sounds. Essential for preventing clipping while maintaining good signal-to-noise ratios in complex patches.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Input 1 level (0-255)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Input 2 level (0-255) 
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Input 3 level (0-255)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Master level (0-255)

**Core Techniques:**
- **Signal summing**: Linear addition of multiple sources
- **Level balancing**: Individual input gain control
- **Headroom management**: Prevent clipping with proper scaling
- **Master control**: Final output level adjustment

**Key Concepts:** Signal summing, headroom management, gain staging, clipping prevention

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

// Mixer state variables
global int phase1 = 0               // Phase for oscillator 1
global int phase2 = 0               // Phase for oscillator 2
global int noise_seed = 12345       // Random seed for noise generation
global int mix_buffer = 0           // Accumulation buffer

function process()
locals int input1_level, int input2_level, int input3_level, int master_level, int signal1, int signal2, int signal3, int external_input, int input1_scaled, int input2_scaled, int input3_scaled, int external_scaled, int mixed_output
{
    loop {
        // Read mixer parameters
        input1_level = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];      // Input 1 level (0-255)
        input2_level = (int)global (int)global params[SWITCHES_PARAM_INDEX];      // Input 2 level (0-255)
        input3_level = (int)global (int)global params[OPERATOR_1_PARAM_INDEX];      // Input 3 level (0-255)
        master_level = (int)global (int)global params[OPERAND_1_HIGH_PARAM_INDEX];      // Master level (0-255)
        
        // Generate test signals
        // Signal 1: Sine wave
        global phase1 = global phase1 + (input1_level + 32);
        if (global phase1 >= 2048) global phase1 = global phase1 - 2048;
        
        if (global phase1 < 512) {
            signal1 = (global phase1 << 2);  // Rising edge
        } else if (global phase1 < 1536) {
            signal1 = 2047 - ((global phase1 - 512) << 1);  // Falling edge
        } else {
            signal1 = -2047 + ((global phase1 - 1536) << 2);  // Rising from bottom
        }
        
        // Signal 2: Sawtooth wave
        global phase2 = global phase2 + (input2_level + 16);
        if (global phase2 >= 2048) global phase2 = global phase2 - 2048;
        signal2 = global phase2 - 1024;  // Center around zero
        
        // Signal 3: Noise
        global noise_seed = (global noise_seed * 1103515245 + 12345) & 0x7FFFFFFF;
        signal3 = (global noise_seed >> 16) - 1024;  // Center around zero
        
        // External input (from audio input)
        external_input = (int)global signal[0];
        
        // Scale each input by its level control (0-255 maps to 0-100% gain)
        input1_scaled = (signal1 * input1_level) >> 8;      // Scale by level
        input2_scaled = (signal2 * input2_level) >> 8;      // Scale by level
        input3_scaled = (signal3 * input3_level) >> 8;      // Scale by level
        external_scaled = (external_input * 128) >> 8;      // Fixed 50% for external
        
        // Mix all signals with headroom management
        // Divide by 4 to prevent clipping when all inputs are at maximum
        global mix_buffer = (input1_scaled + input2_scaled + input3_scaled + external_scaled) >> 2;
        
        // Apply master level control
        mixed_output = (global mix_buffer * master_level) >> 8;
        
        // Final clipping protection
        if (mixed_output > 2047) mixed_output = 2047;
        if (mixed_output < -2047) mixed_output = -2047;
        
        // Output mixed signal
        global signal[0] = mixed_output;
        global signal[1] = mixed_output;
        
        // Display individual input levels on LEDs
        global displayLEDs[0] = input1_level;         // Input 1 level
        global displayLEDs[1] = input2_level;         // Input 2 level
        global displayLEDs[2] = input3_level;         // Input 3 level
        global displayLEDs[3] = master_level;         // Master level
        
        yield();
    }
}

```

## How It Works

**Signal Generation**: Creates three different test signals (sine wave, sawtooth, and noise) plus external audio input for mixing demonstration.

**Individual Level Control**: Each input has independent gain control from 0-255, scaled to 0-100% gain for mixing.

**Headroom Management**: Divides the final mix by 4 to prevent clipping when all inputs are at maximum level. This reserves headroom for safe mixing.

**Master Level**: Final output level control applied after mixing, allowing overall volume adjustment.

**Parameter Control**:
- **Knob 1**: Input 1 level (sine wave)
- **Knob 2**: Input 2 level (sawtooth wave) 
- **Knob 3**: Input 3 level (noise)
- **Knob 4**: Master output level

## Try These Settings

```impala
// Balanced mix of all sources
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 128;  // 50% sine wave
(int)global params[SWITCHES_PARAM_INDEX] = 128;  // 50% sawtooth
(int)global params[OPERATOR_1_PARAM_INDEX] = 64;   // 25% noise (background)
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;  // 78% master level

// Sine wave dominant
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;  // 78% sine wave
(int)global params[SWITCHES_PARAM_INDEX] = 64;   // 25% sawtooth
(int)global params[OPERATOR_1_PARAM_INDEX] = 32;   // 12% noise
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 150;  // 59% master level

// Noise texture emphasis
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 100;  // 39% sine wave
(int)global params[SWITCHES_PARAM_INDEX] = 80;   // 31% sawtooth
(int)global params[OPERATOR_1_PARAM_INDEX] = 180;  // 70% noise
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 120;  // 47% master level

// Clean oscillator mix
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 160;  // 63% sine wave
(int)global params[SWITCHES_PARAM_INDEX] = 160;  // 63% sawtooth
(int)global params[OPERATOR_1_PARAM_INDEX] = 0;    // 0% noise
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 180;  // 70% master level
```

## Understanding Mixing Mathematics

**Linear Addition**: Basic mixing is mathematical addition: `output = input1 + input2 + input3`

**Headroom Management**: With multiple inputs at maximum level, the sum can exceed the available range. Dividing by the number of inputs prevents overflow.

**Gain Staging**: Each input is scaled by its level control before mixing, allowing individual balance control while maintaining overall headroom.

**Master Control**: Final level adjustment applied after mixing for overall volume control.

## Try These Changes

- **Logarithmic faders**: Use `level = (param * param) >> 8` for more natural volume curves
- **Stereo panning**: Add pan controls for each input to create stereo positioning
- **Mute/solo controls**: Implement mute and solo functionality for live performance
- **Send effects**: Route portions of each input to reverb or delay effects

## Related Techniques

- **[Crossfade](crossfade.md)**: Smooth transitions between mixed signals
- **[Input Monitoring](input-monitoring.md)**: Monitor signal levels for mixing feedback
- **[Parameter Smoothing](../parameters/parameter-smoothing.md)**: Smooth level changes to prevent clicks

---
*Part of the [Permut8 Cookbook](../index.md) series*
