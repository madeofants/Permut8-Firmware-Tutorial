# Parameter Display

*Show parameter values and knob positions using LED displays for real-time visual feedback*

## What This Does

Provides real-time visual feedback for patch parameters using LED positioning and different visualization modes. Shows knob positions, parameter ranges, and value changes with smooth visual transitions.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Parameter 1 value (0-255, displayed on ring 0)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Parameter 2 value (0-255, displayed on ring 1)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Parameter 3 value (0-255, displayed on ring 2)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Display mode (0-255, selects visualization style)

**Core Techniques:**
- **Single LED**: Show exact parameter position
- **Bar graph**: Show parameter as filled bar
- **Bipolar**: Show parameter relative to center
- **Stepped**: Show discrete parameter values

**Key Concepts:** Parameter mapping, LED positioning, visual feedback, smooth transitions

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2


const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT



extern native yield


global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]


global array smoothed_params[4] = {128, 128, 128, 128}
global int oscillator_phase = 0

function process()
locals display_mode, param0, param1, param2, param3, led_position, led_count, led_pattern, center_pos, offset, step, leds_per_step, i, frequency, resonance, gain, sine_index, oscillator_output, diff
{
    loop {

        param0 = params[CLOCK_FREQ_PARAM_INDEX];
        param1 = params[SWITCHES_PARAM_INDEX];
        param2 = params[OPERATOR_1_PARAM_INDEX];
        display_mode = params[OPERAND_1_HIGH_PARAM_INDEX] >> 6;
        

        diff = param0 - global smoothed_params[0];
        global smoothed_params[0] = global smoothed_params[0] + (diff >> 3);
        
        diff = param1 - global smoothed_params[1];
        global smoothed_params[1] = global smoothed_params[1] + (diff >> 3);
        
        diff = param2 - global smoothed_params[2];
        global smoothed_params[2] = global smoothed_params[2] + (diff >> 3);
        

        if (display_mode == 0) {

            led_position = global smoothed_params[0] >> 5;
            if (led_position > 7) led_position = 7;
            global displayLEDs[0] = 1 << led_position;
            
        } else if (display_mode == 1) {

            led_count = (global smoothed_params[0] >> 5) + 1;
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

            center_pos = 4;
            offset = (global smoothed_params[0] - 128) >> 4;
            
            led_position = center_pos + offset;
            if (led_position < 0) led_position = 0;
            if (led_position > 7) led_position = 7;
            
            global displayLEDs[0] = (1 << center_pos) | (1 << led_position);
            
        } else {

            step = global smoothed_params[0] >> 6;
            leds_per_step = 2;
            
            led_pattern = 0;
            if (step == 0) {
                led_pattern = 3;
            } else if (step == 1) {
                led_pattern = 12;
            } else if (step == 2) {
                led_pattern = 48;
            } else {
                led_pattern = 192;
            }
            global displayLEDs[0] = led_pattern;
        }
        

        led_count = (global smoothed_params[1] >> 5) + 1;
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
        

        led_position = global smoothed_params[2] >> 5;
        if (led_position > 7) led_position = 7;
        global displayLEDs[2] = 1 << led_position;
        

        global displayLEDs[3] = (display_mode + 1) << 6;
        


        frequency = 200 + ((global smoothed_params[0] * 1800) >> 8);
        resonance = global smoothed_params[1];
        gain = global smoothed_params[2];
        

        global oscillator_phase = global oscillator_phase + (frequency << 6);
        if (global oscillator_phase >= 2048000) global oscillator_phase = global oscillator_phase - 2048000;
        

        sine_index = global oscillator_phase >> 11;
        if (sine_index < 128) {
            oscillator_output = (sine_index << 4) - 1024;
        } else {
            oscillator_output = 1024 - ((sine_index - 128) << 4);
        }
        

        oscillator_output = (oscillator_output * gain) >> 8;
        

        if (oscillator_output > 2047) oscillator_output = 2047;
        if (oscillator_output < -2047) oscillator_output = -2047;
        

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

params[CLOCK_FREQ_PARAM_INDEX] = 128;
params[SWITCHES_PARAM_INDEX] = 200;
params[OPERATOR_1_PARAM_INDEX] = 64;
params[OPERAND_1_HIGH_PARAM_INDEX] = 0;


params[CLOCK_FREQ_PARAM_INDEX] = 160;
params[SWITCHES_PARAM_INDEX] = 255;
params[OPERATOR_1_PARAM_INDEX] = 80;
params[OPERAND_1_HIGH_PARAM_INDEX] = 64;


params[CLOCK_FREQ_PARAM_INDEX] = 200;
params[SWITCHES_PARAM_INDEX] = 100;
params[OPERATOR_1_PARAM_INDEX] = 60;
params[OPERAND_1_HIGH_PARAM_INDEX] = 128;


params[CLOCK_FREQ_PARAM_INDEX] = 180;
params[SWITCHES_PARAM_INDEX] = 150;
params[OPERATOR_1_PARAM_INDEX] = 220;
params[OPERAND_1_HIGH_PARAM_INDEX] = 192;
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

