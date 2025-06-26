# Control LEDs

*Master LED control for visual feedback and parameter display*

## What This Does

Provides comprehensive LED control for creating visual feedback systems, parameter displays, and interactive user interfaces. Demonstrates multiple LED patterns, animation techniques, and real-time parameter visualization.

## Quick Reference

**Essential Parameters:**
- `params[CLOCK_FREQ_PARAM_INDEX]`: LED pattern selection (0-255, selects display mode)
- `params[SWITCHES_PARAM_INDEX]`: Brightness control (0-255, LED intensity)
- `params[OPERATOR_1_PARAM_INDEX]`: Animation speed (0-255, timing control)
- `params[OPERAND_1_HIGH_PARAM_INDEX]`: Color/pattern modifier (0-255, visual variation)

**Core Techniques:**
- **LED patterns**: Static displays, animations, parameter visualization
- **Brightness control**: Intensity modulation and fading effects
- **Animation timing**: Synchronized visual feedback with audio processing
- **Multi-ring coordination**: Using all 4 LED rings for complex displays

**Key Concepts:** LED mapping, bit manipulation, visual feedback design, animation patterns

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
extern native yield

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[PARAM_COUNT]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// LED control state
global int animation_counter = 0    // Animation timing
global int led_phase = 0           // Animation phase
global int brightness_envelope = 255  // Brightness modulation

function process()
locals int pattern_mode, brightness, animation_speed, pattern_modifier, i, led_value, chase_position, fade_amount, audio_level, ring_pattern, bit_pattern, wave_position
{
    loop {
        // Read control parameters
        pattern_mode = params[CLOCK_FREQ_PARAM_INDEX] >> 5;      // 0-7 pattern modes
        brightness = params[SWITCHES_PARAM_INDEX];              // 0-255 brightness
        animation_speed = (params[OPERATOR_1_PARAM_INDEX] >> 4) + 1;  // 1-16 speed
        pattern_modifier = params[OPERAND_1_HIGH_PARAM_INDEX];      // 0-255 modifier
        
        // Update animation timing
        global animation_counter = global animation_counter + 1;
        if (global animation_counter >= (17 - animation_speed) * 32) {
            global animation_counter = 0;
            global led_phase = global led_phase + 1;
            if (global led_phase >= 256) global led_phase = 0;
        }
        
        // Get audio level for reactive displays
        audio_level = (int)global signal[0];
        if (audio_level < 0) audio_level = -audio_level;
        audio_level = audio_level >> 3;  // Scale to 0-255 range
        
        // === LED PATTERN SELECTION ===
        if (pattern_mode == 0) {
            // Static parameter display
            global displayLEDs[0] = params[CLOCK_FREQ_PARAM_INDEX];
            global displayLEDs[1] = params[SWITCHES_PARAM_INDEX];
            global displayLEDs[2] = params[OPERATOR_1_PARAM_INDEX];
            global displayLEDs[3] = params[OPERAND_1_HIGH_PARAM_INDEX];
            
        } else if (pattern_mode == 1) {
            // Chase pattern (rotating light)
            chase_position = global led_phase >> 5;  // 0-7 position
            for (i = 0; i < 4; i = i + 1) {
                if ((chase_position + i) & 7 < 2) {
                    global displayLEDs[i] = brightness;
                } else {
                    global displayLEDs[i] = brightness >> 3;  // Dim trail
                }
            }
            
        } else if (pattern_mode == 2) {
            // Audio-reactive level meters
            // Ring 0: Left channel level
            led_value = audio_level;
            if (led_value > brightness) led_value = brightness;
            global displayLEDs[0] = led_value;
            
            // Ring 1: Right channel level
            audio_level = (int)global signal[1];
            if (audio_level < 0) audio_level = -audio_level;
            audio_level = audio_level >> 3;
            if (audio_level > brightness) audio_level = brightness;
            global displayLEDs[1] = audio_level;
            
            // Ring 2: Peak hold
            if (audio_level > global displayLEDs[2]) {
                global displayLEDs[2] = audio_level;
            } else {
                global displayLEDs[2] = global displayLEDs[2] - 1;
                if (global displayLEDs[2] < 0) global displayLEDs[2] = 0;
            }
            
            // Ring 3: Activity indicator
            if (audio_level > 32) {
                global displayLEDs[3] = brightness;
            } else {
                global displayLEDs[3] = global displayLEDs[3] >> 1;
            }
            
        } else if (pattern_mode == 3) {
            // Breathing pattern (sine wave brightness)
            fade_amount = (global led_phase * brightness) >> 8;
            
            // Create breathing effect using triangle wave
            if (global led_phase < 128) {
                fade_amount = global led_phase * 2;
            } else {
                fade_amount = (255 - global led_phase) * 2;
            }
            fade_amount = (fade_amount * brightness) >> 8;
            
            for (i = 0; i < 4; i = i + 1) {
                global displayLEDs[i] = fade_amount;
            }
            
        } else if (pattern_mode == 4) {
            // Wave pattern (propagating across rings)
            wave_position = global led_phase >> 6;  // 0-3 wave position
            
            for (i = 0; i < 4; i = i + 1) {
                if (i == wave_position) {
                    global displayLEDs[i] = brightness;
                } else if (i == (wave_position - 1) & 3 || i == (wave_position + 1) & 3) {
                    global displayLEDs[i] = brightness >> 1;
                } else {
                    global displayLEDs[i] = brightness >> 3;
                }
            }
            
        } else if (pattern_mode == 5) {
            // Binary counter display
            bit_pattern = global led_phase >> 4;  // 0-15 counter
            
            global displayLEDs[0] = (bit_pattern & 1) ? brightness : 0;
            global displayLEDs[1] = (bit_pattern & 2) ? brightness : 0;
            global displayLEDs[2] = (bit_pattern & 4) ? brightness : 0;
            global displayLEDs[3] = (bit_pattern & 8) ? brightness : 0;
            
        } else if (pattern_mode == 6) {
            // Parameter interaction display
            // Show parameter relationships with visual feedback
            ring_pattern = (params[CLOCK_FREQ_PARAM_INDEX] + params[SWITCHES_PARAM_INDEX]) >> 1;
            global displayLEDs[0] = ring_pattern;
            
            ring_pattern = (params[OPERATOR_1_PARAM_INDEX] + params[OPERAND_1_HIGH_PARAM_INDEX]) >> 1;
            global displayLEDs[1] = ring_pattern;
            
            // Cross-modulation display
            ring_pattern = ((int)params[CLOCK_FREQ_PARAM_INDEX] * (int)params[SWITCHES_PARAM_INDEX]) >> 8;
            global displayLEDs[2] = ring_pattern;
            
            // Activity indicator with modifier
            global displayLEDs[3] = (audio_level + pattern_modifier) >> 1;
            
        } else {
            // Pattern mode 7: Custom pattern with modifier
            // User-defined pattern using pattern_modifier
            for (i = 0; i < 4; i = i + 1) {
                ring_pattern = ((global led_phase + (i * 64)) & 255);
                ring_pattern = (ring_pattern * pattern_modifier) >> 8;
                ring_pattern = (ring_pattern * brightness) >> 8;
                global displayLEDs[i] = ring_pattern;
            }
        }
        
        // Pass audio through unchanged
        global signal[0] = (int)global signal[0];
        global signal[1] = (int)global signal[1];
        
        yield();
    }
}
```

## How It Works

**LED Control System**: Each LED ring is controlled independently through `displayLEDs[0-3]`, with values from 0 (off) to 255 (maximum brightness).

**Pattern Modes**: Eight different display modes accessible through the first parameter:
- **Mode 0**: Direct parameter display
- **Mode 1**: Chase/rotating patterns
- **Mode 2**: Audio-reactive level meters
- **Mode 3**: Breathing/pulsing effects
- **Mode 4**: Wave propagation
- **Mode 5**: Binary counter
- **Mode 6**: Parameter interaction visualization
- **Mode 7**: Custom modulated patterns

**Animation Timing**: Controllable animation speed from slow (1) to fast (16) using precise timing counters.

**Audio Reactivity**: LED patterns can respond to input audio levels for dynamic visual feedback.

## Parameter Control

- **Knob 1**: Pattern mode selection (8 different visual modes)
- **Knob 2**: Master brightness control (0-255 intensity)
- **Knob 3**: Animation speed (1-16, slower to faster)
- **Knob 4**: Pattern modifier (varies effect based on mode)

## Try These Settings

```impala
// Audio-reactive level meters
params[CLOCK_FREQ_PARAM_INDEX] = 64;   // Mode 2 (level meters)
params[SWITCHES_PARAM_INDEX] = 200;   // High brightness
params[OPERATOR_1_PARAM_INDEX] = 128;  // Medium speed
params[OPERAND_1_HIGH_PARAM_INDEX] = 180;  // Good sensitivity

// Smooth breathing pattern
params[CLOCK_FREQ_PARAM_INDEX] = 96;   // Mode 3 (breathing)
params[SWITCHES_PARAM_INDEX] = 150;   // Moderate brightness
params[OPERATOR_1_PARAM_INDEX] = 64;   // Slow breathing
params[OPERAND_1_HIGH_PARAM_INDEX] = 255; // Full modulation

// Fast chase pattern
params[CLOCK_FREQ_PARAM_INDEX] = 32;   // Mode 1 (chase)
params[SWITCHES_PARAM_INDEX] = 255;   // Maximum brightness
params[OPERATOR_1_PARAM_INDEX] = 240;  // Very fast
params[OPERAND_1_HIGH_PARAM_INDEX] = 128; // Standard modifier
```

## LED Display Techniques

**Bit Manipulation for Patterns**:
```impala
// Set specific LED positions
led_pattern = 0;
led_pattern = led_pattern | (1 << position);  // Turn on LED at position

// Create walking patterns
walking_bit = 1 << (counter & 7);  // Moves bit 0-7

// Combine multiple patterns
combined = pattern1 | pattern2;
```

**Brightness Modulation**:
```impala
// Fade effects
faded_brightness = (base_brightness * fade_factor) >> 8;

// Pulse effects using triangle waves
if (phase < 128) {
    pulse_brightness = phase * 2;
} else {
    pulse_brightness = (255 - phase) * 2;
}
```

## Try These Changes

- **Color coding**: Use different brightness levels to represent parameter ranges
- **Multi-pattern**: Combine multiple animation modes simultaneously
- **MIDI reactive**: Make patterns respond to MIDI input velocity/CC
- **Audio analysis**: Add frequency-specific LED responses
- **Parameter memory**: Save and recall LED states with parameter presets

## Related Techniques

- **[Parameter Display](parameter-display.md)**: Advanced parameter visualization
- **[Level Metering](../fundamentals/level-metering.md)**: Audio level measurement
- **[Read Knobs](../../../reference/parameters/read-knobs.md)**: Parameter input handling

---

*Part of the [Permut8 Cookbook](../index.md) series*