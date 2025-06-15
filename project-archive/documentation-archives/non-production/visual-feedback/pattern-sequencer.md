# Pattern Sequencer

*Create visual step sequencers using LED displays for musical pattern creation and playback*

## What This Does

Creates a visual step sequencer that uses LED rings for pattern visualization. Each LED represents a sequencer step, showing active steps, current playback position, and gate activity with real-time visual feedback.

## Quick Reference

**Essential Parameters:**
- `params[0]`: Tempo (0-255, controls BPM from 60-180)
- `params[1]`: Pattern length (0-255, sets 1-8 steps)
- `params[2]`: Pattern select (0-255, future enhancement)
- `params[3]`: Gate length (0-255, future enhancement)

**Core Techniques:**
- **Pattern storage**: 16-bit pattern data with bit manipulation
- **Step sequencing**: Timed progression through pattern steps
- **Visual feedback**: LED rings show pattern state and playback
- **Gate generation**: Triggers based on active pattern steps

**Key Concepts:** Step sequencing, pattern data, LED visualization, timing control

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Pattern sequencer state
global int pattern = 37449         // 16-bit pattern (1001001001001001)
global int current_step = 0        // Current playback position (0-7)
global int pattern_length = 8      // Active pattern length (1-8)
global int step_counter = 0        // Clock counter for timing
global int steps_per_beat = 4410   // Steps per sequencer beat
global int gate_active = 0         // Current gate state (0/1)
global int gate_counter = 0        // Gate timing counter
global int smooth_output = 0       // Smoothed audio output

function process()
locals int tempo, int output, int diff, int step_is_active, int led_pattern, int i
{
    loop {
        // Read control parameters
        tempo = 60 + (((int)global params[0] * 120) >> 8);  // 60-180 BPM
        global pattern_length = 1 + (((int)global params[1] * 7) >> 8);  // 1-8 steps
        
        // Calculate timing (simplified)
        global steps_per_beat = 44100 / (tempo >> 2);  // Approximate timing
        
        // Update step counter
        global step_counter = global step_counter + 1;
        
        // Check for step advance
        if (global step_counter >= global steps_per_beat) {
            global step_counter = 0;
            
            // Advance to next step
            global current_step = global current_step + 1;
            if (global current_step >= global pattern_length) {
                global current_step = 0;
            }
            
            // Check if current step should trigger
            step_is_active = (global pattern >> global current_step) & 1;
            if (step_is_active > 0) {
                global gate_active = 1;
                global gate_counter = 2205;  // 50ms gate length
            }
        }
        
        // Update gate timing
        if (global gate_active > 0) {
            global gate_counter = global gate_counter - 1;
            if (global gate_counter <= 0) {
                global gate_active = 0;
            }
        }
        
        // Generate output based on gate state
        if (global gate_active > 0) {
            output = 1500;
        } else {
            output = 0;
        }
        
        // Apply simple envelope for smoothing
        diff = output - global smooth_output;
        global smooth_output = global smooth_output + (diff >> 6);
        
        // Prevent clipping
        if (global smooth_output > 2047) global smooth_output = 2047;
        if (global smooth_output < -2047) global smooth_output = -2047;
        
        // === LED VISUALIZATION ===
        // Show pattern on LED ring 0
        led_pattern = 0;
        if ((global pattern & 1) > 0) led_pattern = led_pattern | 1;
        if ((global pattern & 2) > 0) led_pattern = led_pattern | 2;
        if ((global pattern & 4) > 0) led_pattern = led_pattern | 4;
        if ((global pattern & 8) > 0) led_pattern = led_pattern | 8;
        if ((global pattern & 16) > 0) led_pattern = led_pattern | 16;
        if ((global pattern & 32) > 0) led_pattern = led_pattern | 32;
        if ((global pattern & 64) > 0) led_pattern = led_pattern | 64;
        if ((global pattern & 128) > 0) led_pattern = led_pattern | 128;
        global displayLEDs[0] = led_pattern;
        
        // Show current step on LED ring 1
        global displayLEDs[1] = 1 << global current_step;
        
        // Show gate activity on LED ring 2  
        if (global gate_active > 0) {
            global displayLEDs[2] = 255;  // All LEDs on when gate active
        } else {
            global displayLEDs[2] = 0;    // All LEDs off
        }
        
        // Show pattern length on LED ring 3
        led_pattern = 0;
        if (global pattern_length >= 1) led_pattern = led_pattern | 1;
        if (global pattern_length >= 2) led_pattern = led_pattern | 2;
        if (global pattern_length >= 3) led_pattern = led_pattern | 4;
        if (global pattern_length >= 4) led_pattern = led_pattern | 8;
        if (global pattern_length >= 5) led_pattern = led_pattern | 16;
        if (global pattern_length >= 6) led_pattern = led_pattern | 32;
        if (global pattern_length >= 7) led_pattern = led_pattern | 64;
        if (global pattern_length >= 8) led_pattern = led_pattern | 128;
        global displayLEDs[3] = led_pattern;
        
        // Output audio
        global signal[0] = global smooth_output;
        global signal[1] = global smooth_output;
        
        yield();
    }
}
```

## How It Works

**Pattern Storage**: Uses a 16-bit integer to store pattern data, where each bit represents a step (1=active, 0=inactive).

**Step Sequencing**: Advances through pattern steps based on tempo timing, triggering gates when active steps are reached.

**Visual Feedback**: Four LED rings show different aspects:
- Ring 0: Pattern bits (which steps are active)
- Ring 1: Current step position
- Ring 2: Gate activity (all LEDs flash when step triggers)
- Ring 3: Pattern length (bar graph showing active length)

**Parameter Control**:
- **Knob 1**: Tempo (60-180 BPM)
- **Knob 2**: Pattern length (1-8 steps)
- **Knob 3**: Reserved for pattern selection
- **Knob 4**: Reserved for gate length control

## Try These Settings

```impala
// Fast techno pattern
params[0] = 200;  // ~140 BPM
params[1] = 128;  // 4 steps
// Pattern: 1001 (kick on 1 and 4)

// Slow ambient pattern  
params[0] = 80;   // ~80 BPM
params[1] = 255;  // 8 steps
// Pattern: 10010010 (sparse triggers)

// Medium house pattern
params[0] = 150;  // ~120 BPM
params[1] = 192;  // 6 steps  
// Pattern: 100100 (every 3 steps)
```

## Pattern Examples

The default pattern `37449` (binary: 1001001001001001) creates a classic 4/4 kick drum pattern when using 4-step length.

**Common Patterns:**
- `21845` (0101010101010101): Every other step
- `4369` (0001000100010001): Classic kick pattern  
- `34952` (1000100010001000): Off-beat pattern
- `65535` (1111111111111111): Every step

## Understanding Bit Patterns

Each bit in the pattern represents one step:
- Bit 0 (rightmost): Step 1
- Bit 1: Step 2
- Bit 2: Step 3
- etc.

Use bit shifting to check individual steps: `(pattern >> step) & 1`

## Try These Changes

- **Multiple patterns**: Use different pattern values for various tracks
- **Pattern editing**: Add real-time pattern modification via additional parameters
- **Swing timing**: Modify step timing for musical feel
- **Gate length control**: Variable gate duration based on parameters

## Related Techniques

- **[Level Meters](level-meters.md)**: Audio level visualization techniques
- **[Control LEDs](control-leds.md)**: Basic LED patterns and control
- **[Sync to Tempo](../timing/sync-to-tempo.md)**: Advanced timing synchronization
- **[Clock Dividers](../timing/clock-dividers.md)**: Rhythm subdivision techniques

---

*This pattern sequencer provides essential step sequencing with visual feedback. Perfect for rhythm generation, musical triggers, and learning sequencer fundamentals through immediate LED visualization.*