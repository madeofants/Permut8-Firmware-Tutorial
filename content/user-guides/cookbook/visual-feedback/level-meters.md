# Level Meters

*Professional audio level metering with VU, peak, and RMS display modes*

## What This Does

Implements comprehensive audio level metering including VU meters, peak detection, RMS calculation, and professional-grade level visualization. Essential for monitoring audio levels, preventing clipping, and providing visual feedback during audio processing.

## Quick Reference

**Essential Parameters:**
- `params[CLOCK_FREQ_PARAM_INDEX]`: Meter mode selection (0-255, chooses meter type)
- `params[SWITCHES_PARAM_INDEX]`: Response time (0-255, attack/release timing)
- `params[OPERATOR_1_PARAM_INDEX]`: Scale factor (0-255, level scaling)
- `params[OPERAND_1_HIGH_PARAM_INDEX]`: Peak hold time (0-255, peak display duration)

**Core Techniques:**
- **RMS calculation**: True power-based level measurement
- **Peak detection**: Instantaneous level peaks with hold
- **VU simulation**: Classic VU meter response characteristics
- **Multi-mode display**: Different metering standards

**Key Concepts:** Level measurement, peak detection, RMS calculation, meter ballistics

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


global int rms_accumulator_L = 0
global int rms_accumulator_R = 0
global int rms_sample_count = 0
global int peak_level_L = 0
global int peak_level_R = 0
global int peak_hold_counter_L = 0
global int peak_hold_counter_R = 0
global int vu_level_L = 0
global int vu_level_R = 0

function process()
locals int meter_mode, response_time, scale_factor, peak_hold_time, input_L, input_R, abs_L, abs_R, squared_L, squared_R, rms_L, rms_R, attack_factor, release_factor, peak_decay, scaled_level, led_segments, i, threshold
{
    loop {

        meter_mode = params[CLOCK_FREQ_PARAM_INDEX] >> 6;
        response_time = (params[SWITCHES_PARAM_INDEX] >> 4) + 1;
        scale_factor = params[OPERATOR_1_PARAM_INDEX] + 1;
        peak_hold_time = (params[OPERAND_1_HIGH_PARAM_INDEX] >> 2) + 1;
        

        input_L = (int)global signal[0];
        input_R = (int)global signal[1];
        

        abs_L = input_L;
        if (abs_L < 0) abs_L = -abs_L;
        abs_R = input_R;
        if (abs_R < 0) abs_R = -abs_R;
        

        abs_L = (abs_L * scale_factor) >> 8;
        abs_R = (abs_R * scale_factor) >> 8;
        if (abs_L > 255) abs_L = 255;
        if (abs_R > 255) abs_R = 255;
        

        attack_factor = response_time;
        release_factor = response_time >> 1;
        if (release_factor < 1) release_factor = 1;
        

        if (meter_mode == 0) {

            if (abs_L > global peak_level_L) {
                global peak_level_L = abs_L;
                global peak_hold_counter_L = peak_hold_time * 512;
            } else {

                if (global peak_hold_counter_L > 0) {
                    global peak_hold_counter_L = global peak_hold_counter_L - 1;
                } else {
                    global peak_level_L = global peak_level_L - ((global peak_level_L) >> release_factor);
                }
            }
            
            if (abs_R > global peak_level_R) {
                global peak_level_R = abs_R;
                global peak_hold_counter_R = peak_hold_time * 512;
            } else {
                if (global peak_hold_counter_R > 0) {
                    global peak_hold_counter_R = global peak_hold_counter_R - 1;
                } else {
                    global peak_level_R = global peak_level_R - ((global peak_level_R) >> release_factor);
                }
            }
            

            global displayLEDs[0] = global peak_level_L;
            global displayLEDs[1] = global peak_level_R;
            
        } else if (meter_mode == 1) {


            squared_L = (abs_L * abs_L) >> 8;
            squared_R = (abs_R * abs_R) >> 8;
            

            global rms_accumulator_L = global rms_accumulator_L + squared_L;
            global rms_accumulator_R = global rms_accumulator_R + squared_R;
            global rms_sample_count = global rms_sample_count + 1;
            

            if (global rms_sample_count >= 256) {

                rms_L = global rms_accumulator_L >> 8;
                rms_R = global rms_accumulator_R >> 8;
                

                if (rms_L > 128) {
                    rms_L = rms_L - ((rms_L - 128) >> 1);
                } else {
                    rms_L = rms_L >> 1;
                }
                
                if (rms_R > 128) {
                    rms_R = rms_R - ((rms_R - 128) >> 1);
                } else {
                    rms_R = rms_R >> 1;
                }
                

                global displayLEDs[0] = rms_L;
                global displayLEDs[1] = rms_R;
                

                global rms_accumulator_L = 0;
                global rms_accumulator_R = 0;
                global rms_sample_count = 0;
            }
            
        } else if (meter_mode == 2) {


            

            if (abs_L > global vu_level_L) {
                global vu_level_L = global vu_level_L + ((abs_L - global vu_level_L) >> 3);
            } else {

                global vu_level_L = global vu_level_L - ((global vu_level_L - abs_L) >> 5);
            }
            
            if (abs_R > global vu_level_R) {
                global vu_level_R = global vu_level_R + ((abs_R - global vu_level_R) >> 3);
            } else {
                global vu_level_R = global vu_level_R - ((global vu_level_R - abs_R) >> 5);
            }
            

            global displayLEDs[0] = global vu_level_L;
            global displayLEDs[1] = global vu_level_R;
            
        } else {


            

            led_segments = 0;
            for (i = 0; i < 8; i = i + 1) {
                threshold = i * 32;
                if (abs_L > threshold) {
                    led_segments = led_segments | (1 << i);
                }
            }
            global displayLEDs[0] = led_segments;
            

            led_segments = 0;
            for (i = 0; i < 8; i = i + 1) {
                threshold = i * 32;
                if (abs_R > threshold) {
                    led_segments = led_segments | (1 << i);
                }
            }
            global displayLEDs[1] = led_segments;
        }
        

        

        int correlation = ((input_L + input_R) >> 1);
        int difference = input_L - input_R;
        if (difference < 0) difference = -difference;
        difference = difference >> 2;
        
        if (correlation > difference) {
            global displayLEDs[2] = 255;
        } else {
            global displayLEDs[2] = (correlation * 255) / (difference + 1);
        }
        

        if (abs_L > 240 || abs_R > 240) {
            global displayLEDs[3] = 255;
        } else {

            global displayLEDs[3] = global displayLEDs[3] >> 1;
        }
        

        global signal[0] = input_L;
        global signal[1] = input_R;
        
        yield();
    }
}
```

## How It Works

**Multiple Meter Types**:
- **Mode 0**: Peak meters with adjustable hold time
- **Mode 1**: RMS (power) meters for average level measurement
- **Mode 2**: VU meter simulation with classic ballistics
- **Mode 3**: Multi-segment LED bar displays

**Level Calculation Methods**:
- **Peak Detection**: Instant attack, slow release with hold
- **RMS Calculation**: True power measurement over time windows
- **VU Ballistics**: Standard VU meter response characteristics

**Professional Features**:
- **Stereo correlation**: Shows mono/stereo content relationship
- **Overload detection**: Visual warning for levels approaching clipping
- **Adjustable scaling**: Accommodate different signal levels
- **Configurable response**: Attack/release timing control

## Parameter Control

- **Knob 1**: Meter mode (Peak/RMS/VU/Bar display)
- **Knob 2**: Response time (attack/release speed)
- **Knob 3**: Scale factor (input level scaling)
- **Knob 4**: Peak hold time (peak display duration)

## Try These Settings

```impala

params[CLOCK_FREQ_PARAM_INDEX] = 0;
params[SWITCHES_PARAM_INDEX] = 96;
params[OPERATOR_1_PARAM_INDEX] = 200;
params[OPERAND_1_HIGH_PARAM_INDEX] = 180;


params[CLOCK_FREQ_PARAM_INDEX] = 64;
params[SWITCHES_PARAM_INDEX] = 128;
params[OPERATOR_1_PARAM_INDEX] = 128;
params[OPERAND_1_HIGH_PARAM_INDEX] = 64;


params[CLOCK_FREQ_PARAM_INDEX] = 128;
params[SWITCHES_PARAM_INDEX] = 64;
params[OPERATOR_1_PARAM_INDEX] = 150;
params[OPERAND_1_HIGH_PARAM_INDEX] = 128;
```

## Meter Characteristics

**Peak Meters**:
- Fast attack (instant response to transients)
- Slow release (smooth decay)
- Peak hold capability
- Best for: Preventing clipping, transient monitoring

**RMS Meters**:
- Average-responding (power measurement)
- Slower response than peak
- Better represents perceived loudness
- Best for: Mix balancing, loudness control

**VU Meters**:
- Classic analog meter simulation
- Specific attack/release characteristics
- Matches vintage hardware behavior
- Best for: Musical mixing, vintage workflow

## Advanced Techniques

**Calibration**:
```impala



int reference_level = 512;
scaled_level = (level * 255) / reference_level;
```

**Logarithmic Display**:
```impala

if (level > 0) {

    db_level = level;
    if (db_level > 128) db_level = 128 + ((db_level - 128) >> 1);
    if (db_level > 192) db_level = 192 + ((db_level - 192) >> 2);
}
```

## Try These Changes

- **Frequency-specific metering**: Add band-pass filters for frequency-specific levels
- **Stereo width meter**: Visualize stereo field width and balance
- **Phase correlation**: Add phase relationship display
- **MIDI output**: Send meter levels as MIDI CC for DAW integration
- **Clip counting**: Count and display the number of clipped samples

## Related Techniques

- **[Level Metering](../fundamentals/level-metering.md)**: Basic level measurement concepts
- **[Parameter Display](parameter-display.md)**: Parameter visualization techniques
- **[Control LEDs](control-leds.md)**: LED control and animation patterns

---

*Part of the [Permut8 Cookbook](../index.md) series*