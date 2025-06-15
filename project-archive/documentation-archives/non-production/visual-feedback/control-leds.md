# Control LEDs

## What This Does
Shows how to control the four 8-segment LED displays for audio levels, parameter feedback, and visual effects. Demonstrates bit patterns, animations, and real-time audio visualization techniques.

## Quick Reference
**Parameters**:
- **Knob 1 (params[3])**: Position indicator demonstration (0-255)
- **Knob 2-4**: [Available for additional LED control examples]
- **Audio Inputs**: Left/right channels for level meter visualization

**Key Concepts**: Bit manipulation, LED patterns, audio level detection, animation counters

## Complete Code
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// LED control state
global int animation_counter = 0    // Counter for time-based animations

function process()
locals int audio_level_left, int audio_level_right, int led_count_left, int led_count_right, int level_pattern_left, int level_pattern_right, int knob_position, int animation_step, int i
{
    loop {
        // Read audio levels
        audio_level_left = (int)global signal[0];
        audio_level_right = (int)global signal[1];
        
        // Get absolute values for level detection
        if (audio_level_left < 0) audio_level_left = -audio_level_left;
        if (audio_level_right < 0) audio_level_right = -audio_level_right;
        
        // === LED DISPLAY 0: LEFT CHANNEL LEVEL METER ===
        // Scale audio level (0-2047) to LED count (0-8)
        led_count_left = audio_level_left >> 8;  // Divide by 256
        if (led_count_left > 8) led_count_left = 8;
        
        // Create bar graph pattern (manual bit setting)
        level_pattern_left = 0;
        if (led_count_left >= 1) level_pattern_left = 1;
        if (led_count_left >= 2) level_pattern_left = level_pattern_left | 2;
        if (led_count_left >= 3) level_pattern_left = level_pattern_left | 4;
        if (led_count_left >= 4) level_pattern_left = level_pattern_left | 8;
        if (led_count_left >= 5) level_pattern_left = level_pattern_left | 16;
        if (led_count_left >= 6) level_pattern_left = level_pattern_left | 32;
        if (led_count_left >= 7) level_pattern_left = level_pattern_left | 64;
        if (led_count_left >= 8) level_pattern_left = level_pattern_left | 128;
        global displayLEDs[0] = level_pattern_left;
        
        // === LED DISPLAY 1: RIGHT CHANNEL LEVEL METER ===
        led_count_right = audio_level_right >> 8;  // Divide by 256
        if (led_count_right > 8) led_count_right = 8;
        
        // Create bar graph pattern (manual bit setting)
        level_pattern_right = 0;
        if (led_count_right >= 1) level_pattern_right = 1;
        if (led_count_right >= 2) level_pattern_right = level_pattern_right | 2;
        if (led_count_right >= 3) level_pattern_right = level_pattern_right | 4;
        if (led_count_right >= 4) level_pattern_right = level_pattern_right | 8;
        if (led_count_right >= 5) level_pattern_right = level_pattern_right | 16;
        if (led_count_right >= 6) level_pattern_right = level_pattern_right | 32;
        if (led_count_right >= 7) level_pattern_right = level_pattern_right | 64;
        if (led_count_right >= 8) level_pattern_right = level_pattern_right | 128;
        global displayLEDs[1] = level_pattern_right;
        
        // === LED DISPLAY 2: PARAMETER POSITION INDICATOR ===
        // Show knob 1 position as single moving dot
        knob_position = (int)global params[0] >> 5;  // Convert 0-255 to 0-7
        if (knob_position > 7) knob_position = 7;
        global displayLEDs[2] = 1 << knob_position;
        
        // === LED DISPLAY 3: ANIMATION AND STATUS ===
        global animation_counter = global animation_counter + 1;
        
        // Create rotating dot pattern
        animation_step = (global animation_counter >> 6) & 7;  // Slow rotation
        global displayLEDs[3] = 1 << animation_step;
        
        // Override with flash pattern when audio is very loud
        if (audio_level_left > 1500 || audio_level_right > 1500) {
            global displayLEDs[3] = 255;  // All LEDs on for loud signals
        }
        
        // Pass audio through unchanged
        // (Audio is already in signal[] array)
        
        yield();
    }
}
```

## Try These Changes
- **VU meters**: Use `(1 << ledCount) - 1` for solid bar instead of individual segments
- **Inverted display**: Use `0xFF >> (8 - ledCount)` for right-to-left level meters
- **Blinking effects**: Use `if ((animationCounter & 15) < 8)` to blink LEDs on/off
- **Chase patterns**: Use `1 << ((animationCounter >> 2) & 7)` for different animation speeds
- **Threshold indicators**: Light specific LEDs when audio crosses predefined volume levels

## How It Works
Each `displayLEDs[]` element controls one 8-segment display using 8-bit patterns where each bit represents one LED segment. Bit 0 (rightmost) corresponds to the first LED, bit 7 (leftmost) to the eighth LED.

The level meter algorithm converts audio amplitude to a visual representation by dividing the sample value by 256, giving a 0-8 range that maps directly to LED count. The `|` (OR) operator combines multiple bits to create bar graph patterns, while the `<<` (left shift) operator positions individual dots.

Animation counters use bit masking (`&`) to create timing divisions - `animationCounter & 7` creates an 8-sample cycle, while `animationCounter >> 3` provides a slower rotation rate. The bit operations ensure efficient real-time performance without expensive division operations.

## Related Techniques
- **[Read Knobs](../parameters/read-knobs.md)**: Parameter to LED position mapping
- **[Audio Level Detection](../fundamentals/gain-and-volume.md)**: Audio amplitude measurement
- **[Pattern Sequencer](pattern-sequencer.md)**: Advanced LED sequence programming

---
*Part of the [Permut8 Cookbook](../index.md) series*