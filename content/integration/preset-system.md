# Preset System Integration

## Overview
Design firmware that works seamlessly with external preset management systems, allowing users to save, recall, and organize complete parameter states.

## Core Pattern

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


global array preset_(int)global params[OPERAND_1_LOW_PARAM_INDEX]
global int preset_led_state = 0
global int preset_mode = 0
global int smooth_counter = 0

```

## Preset Recall Implementation

```impala

function recall_preset()
locals int i, int target, int current, int diff
{

    i = 0;
    loop {
        if (i >= 4) break;
        
        target = global preset_params[i];
        current = (int)global params[i];
        diff = target - current;
        

        global params[i] = current + (diff >> 6);
        
        i = i + 1;
    }
    

    global displayLEDs[0] = global preset_led_state;
    

    global preset_mode = global preset_mode;
}
```

## External Integration Points

```impala

function handle_preset_change()
locals int cc_num, int value
{

    cc_num = (int)global (int)global params[OPERAND_1_LOW_PARAM_INDEX];

    value = (int)global (int)global params[OPERATOR_2_PARAM_INDEX];
    
    if (cc_num == 0) {
        global (int)global params[CLOCK_FREQ_PARAM_INDEX] = value << 3;
    } else if (cc_num == 1) {
        global (int)global params[SWITCHES_PARAM_INDEX] = value << 3;
    } else if (cc_num == 2) {
        global (int)global params[OPERATOR_1_PARAM_INDEX] = value << 3;
    } else if (cc_num == 3) {
        global (int)global params[OPERAND_1_HIGH_PARAM_INDEX] = value << 3;
    }
}


function handle_program_change()
locals int program_num
{
    program_num = (int)global (int)global params[OPERAND_2_HIGH_PARAM_INDEX];
    if (program_num < 4) {
        recall_preset();
    }
}


function process()
locals int input_sample, int output_sample, int mix_level
{
    loop {

        handle_preset_change();
        handle_program_change();
        

        input_sample = (int)global signal[0];
        

        mix_level = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];
        output_sample = (input_sample * mix_level) >> 8;
        

        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        

        global signal[0] = output_sample;
        global signal[1] = output_sample;
        

        global displayLEDs[1] = mix_level;
        global displayLEDs[2] = global preset_mode << 6;
        global displayLEDs[3] = (int)global (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
        
        yield();
    }
}
```

## Design Guidelines

### Parameter Organization
- Keep related parameters together in consecutive slots
- Use consistent value ranges (0-255 for Impala params)
- Avoid hidden or internal-only parameters in preset data
- Document parameter functions clearly

### State Management
- Include all user-controllable state in presets
- Exclude temporary/calculated values
- Handle edge cases gracefully (invalid ranges, etc.)
- Provide sensible defaults

### Performance Considerations
- Smooth parameter changes to prevent audio glitches
- Batch parameter updates when possible
- Avoid expensive operations during preset recall
- Keep preset data structures simple and fast

## Best Practices

1. **Consistent Behavior**: Same parameter values should always produce the same sound
2. **Complete State**: Presets should capture everything needed to recreate the sound
3. **Graceful Degradation**: Handle missing or corrupted preset data safely
4. **Clear Mapping**: Document which MIDI CCs map to which parameters
5. **Version Compatibility**: Design presets to work across firmware updates when possible

This pattern ensures your firmware integrates smoothly with DAWs, hardware controllers, and preset management software.
