# Parameter Display

*Show parameter values and knob positions using LED displays for real-time visual feedback*

## What This Does

Provides real-time visual feedback for patch parameters using LED positioning and different visualization modes. Shows knob positions, parameter ranges, and value changes with smooth visual transitions.

## Quick Reference

**Essential Parameters:**
- `params[0]`: Parameter 1 value (0-255, displayed on ring 0)
- `params[1]`: Parameter 2 value (0-255, displayed on ring 1)
- `params[2]`: Parameter 3 value (0-255, displayed on ring 2)
- `params[3]`: Display mode (0-255, selects visualization style)

**Core Techniques:**
- **Single LED**: Show exact parameter position
- **Bar graph**: Show parameter as filled bar
- **Bipolar**: Show parameter relative to center
- **Stepped**: Show discrete parameter values

**Key Concepts:** Parameter mapping, LED positioning, visual feedback, smooth transitions

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Parameter display state
global array smoothed_params[4] = {128, 128, 128, 128}  // Smoothed parameter values
global int oscillator_phase = 0     // Phase for audio generation

function process()
locals int display_mode, int param0, int param1, int param2, int param3, int led_position, int led_count, int led_pattern, int center_pos, int offset, int step, int leds_per_step, int i, int frequency, int resonance, int gain, int sine_index, int oscillator_output, int diff
{
    loop {
        // Read control parameters
        param0 = (int)global params[0];      // Parameter 0 (0-255)
        param1 = (int)global params[1];      // Parameter 1 (0-255)
        param2 = (int)global params[2];      // Parameter 2 (0-255)
        display_mode = (int)global params[3] >> 6;  // Display mode (0-3)
        
        // Smooth parameter values to avoid LED flickering
        diff = param0 - (int)global smoothed_params[0];
        global smoothed_params[0] = (int)global smoothed_params[0] + (diff >> 3);
        
        diff = param1 - (int)global smoothed_params[1];
        global smoothed_params[1] = (int)global smoothed_params[1] + (diff >> 3);
        
        diff = param2 - (int)global smoothed_params[2];
        global smoothed_params[2] = (int)global smoothed_params[2] + (diff >> 3);
        
        // === DISPLAY PARAMETER 0 ON LED RING 0 ===
        if (display_mode == 0) {
            // Single LED mode
            led_position = (int)global smoothed_params[0] >> 5;  // Scale to 0-7
            if (led_position > 7) led_position = 7;
            global displayLEDs[0] = 1 << led_position;
            
        } else if (display_mode == 1) {
            // Bar graph mode
            led_count = ((int)global smoothed_params[0] >> 5) + 1;  // 1-8 LEDs
            if (led_count > 8) led_count = 8;
            
            led_pattern = 0;
            if (led_count >= 1) led_pattern = led_pattern | 1;
            if (led_count >= 2) led_pattern = led_pattern | 2;
            if (led_count >= 3) led_pattern = led_pattern | 4;
            if (led_count >= 4) led_pattern = led_pattern | 8;
            if (led_count >= 5) led_pattern = led_pattern | 16;
            if (led_count >= 6) led_pattern = led_pattern | 32;
            if (led_count >= 7) led_pattern = led_pattern | 64;
            if (led_count >= 8) led_pattern = led_pattern | 128;
            global displayLEDs[0] = led_pattern;
            
        } else if (display_mode == 2) {
            // Bipolar mode (center-based)
            center_pos = 4;  // Center of 8 LEDs
            offset = ((int)global smoothed_params[0] - 128) >> 4;  // -8 to +7 range
            
            led_position = center_pos + offset;
            if (led_position < 0) led_position = 0;
            if (led_position > 7) led_position = 7;
            
            global displayLEDs[0] = (1 << center_pos) | (1 << led_position);
            
        } else {
            // Stepped mode (discrete values)
            step = (int)global smoothed_params[0] >> 6;  // 0-3 steps
            leds_per_step = 2;  // 2 LEDs per step
            
            led_pattern = 0;
            if (step == 0) {
                led_pattern = 3;  // LEDs 0,1
            } else if (step == 1) {
                led_pattern = 12; // LEDs 2,3  
            } else if (step == 2) {
                led_pattern = 48; // LEDs 4,5
            } else {
                led_pattern = 192; // LEDs 6,7
            }
            global displayLEDs[0] = led_pattern;
        }
        
        // === DISPLAY PARAMETER 1 ON LED RING 1 (Bar graph) ===
        led_count = ((int)global smoothed_params[1] >> 5) + 1;
        if (led_count > 8) led_count = 8;
        
        led_pattern = 0;
        if (led_count >= 1) led_pattern = led_pattern | 1;
        if (led_count >= 2) led_pattern = led_pattern | 2;
        if (led_count >= 3) led_pattern = led_pattern | 4;
        if (led_count >= 4) led_pattern = led_pattern | 8;
        if (led_count >= 5) led_pattern = led_pattern | 16;
        if (led_count >= 6) led_pattern = led_pattern | 32;
        if (led_count >= 7) led_pattern = led_pattern | 64;
        if (led_count >= 8) led_pattern = led_pattern | 128;
        global displayLEDs[1] = led_pattern;
        
        // === DISPLAY PARAMETER 2 ON LED RING 2 (Single LED) ===
        led_position = (int)global smoothed_params[2] >> 5;
        if (led_position > 7) led_position = 7;
        global displayLEDs[2] = 1 << led_position;
        
        // === DISPLAY MODE INDICATOR ON LED RING 3 ===
        global displayLEDs[3] = (display_mode + 1) << 6;  // Show current mode
        
        // === AUDIO GENERATION USING PARAMETERS ===
        // Use parameters to control audio
        frequency = 200 + (((int)global smoothed_params[0] * 1800) >> 8);  // 200-1900 Hz
        resonance = (int)global smoothed_params[1];  // 0-255
        gain = (int)global smoothed_params[2];       // 0-255
        
        // Simple oscillator
        global oscillator_phase = global oscillator_phase + (frequency << 6);
        if (global oscillator_phase >= 2048000) global oscillator_phase = global oscillator_phase - 2048000;
        
        // Triangle wave approximation
        sine_index = global oscillator_phase >> 11;  // Scale to 0-255 range
        if (sine_index < 128) {
            oscillator_output = (sine_index << 4) - 1024;  // Rising edge
        } else {
            oscillator_output = 1024 - ((sine_index - 128) << 4);  // Falling edge
        }
        
        // Apply gain
        oscillator_output = (oscillator_output * gain) >> 8;
        
        // Prevent clipping
        if (oscillator_output > 2047) oscillator_output = 2047;
        if (oscillator_output < -2047) oscillator_output = -2047;
        
        // Output audio
        global signal[0] = oscillator_output;
        global signal[1] = oscillator_output;
        
        yield();
    }
}
```

## How It Works

**Parameter Mapping**: Converts parameter values (0-255) to LED positions (0-7) using simple scaling and bit shifting.

**Display Modes**: Four different visualization styles:
- Single LED: Shows exact parameter position
- Bar graph: Shows parameter as filled bar from bottom
- Bipolar: Shows parameter relative to center position
- Stepped: Shows discrete parameter values in groups

**Smoothing**: Exponential smoothing prevents LED flickering when parameters change rapidly.

**Parameter Control**:
- **Knob 1**: Parameter 1 (displayed with selected mode)
- **Knob 2**: Parameter 2 (displayed as bar graph)
- **Knob 3**: Parameter 3 (displayed as single LED)
- **Knob 4**: Display mode selection (0-3)

## Try These Settings

```impala
// Single LED mode
params[0] = 128;  // Middle position
params[1] = 200;  // High value
params[2] = 64;   // Low-mid value
params[3] = 0;    // Single LED mode

// Bar graph mode
params[0] = 160;  // 5 LEDs lit
params[1] = 255;  // All LEDs lit
params[2] = 80;   // 2-3 LEDs lit
params[3] = 64;   // Bar graph mode

// Bipolar mode
params[0] = 200;  // Above center
params[1] = 100;  // Average level
params[2] = 60;   // Below center
params[3] = 128;  // Bipolar mode

// Stepped mode
params[0] = 180;  // Step 2 of 4
params[1] = 150;  // Medium level
params[2] = 220;  // High value
params[3] = 192;  // Stepped mode
```
## How It Works

### **Parameter Mapping Theory**
Converting parameter values to LED positions requires careful scaling. Linear mapping works for most parameters, while logarithmic curves suit frequency parameters and exponential curves work for gain parameters.

### **Smoothing Algorithms**
Visual parameter updates use exponential smoothing to avoid distracting flicker while maintaining responsiveness to parameter changes.

### **Display Mode Selection**
Different visualization modes serve different purposes - single LED for precise positioning, bar graphs for level-style parameters, bipolar for centered controls, and stepped for discrete values.

## Memory Usage

The parameter display system uses minimal memory:
- Parameter arrays: 8 integers (4 parameters × 2 arrays)
- State variables: 5 integers
- Total: ~50 bytes

## Related Techniques

- **level-meters.md** - Audio level visualization techniques
- **control-leds.md** - Basic LED control and patterns
- **read-knobs.md** - Parameter reading and scaling
- **parameter-smoothing.md** - Advanced parameter smoothing techniques

---

*This parameter display system provides intuitive visual feedback for all patch parameters. Perfect for real-time performance, patch development, and understanding parameter relationships through immediate visual representation.*

## Understanding Display Modes

**Single LED Mode**: Shows exact parameter position as a single LED. Good for precise positioning and frequency controls.

**Bar Graph Mode**: Shows parameter as filled bar from bottom. Good for level-style parameters like volume, filter cutoff, or envelope amounts.

**Bipolar Mode**: Shows parameter relative to center position. Good for pan controls, pitch bend, or any centered parameter.

**Stepped Mode**: Shows discrete parameter values in groups. Good for switch positions, quantized values, or mode selection.

**Smoothing**: Prevents visual flickering by gradually updating LED positions when parameters change.

## Try These Changes

- **Multi-parameter ring**: Show multiple parameters on one ring using different LED segments
- **Change detection**: Flash LEDs when parameters change significantly
- **Range indication**: Show parameter range limits with dimmer LEDs
- **Breathing effects**: Add pulsing or breathing patterns to parameter displays

## Related Techniques

- **[Level Meters](level-meters.md)**: Audio level visualization techniques
- **[Control LEDs](control-leds.md)**: Basic LED control and patterns
- **[Read Knobs](../parameters/read-knobs.md)**: Parameter reading and scaling

---
*Part of the [Permut8 Cookbook](../index.md) series*

