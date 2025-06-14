# Preset System Integration

## Overview
Design firmware that works seamlessly with external preset management systems, allowing users to save, recall, and organize complete parameter states.

## Core Pattern

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Preset state management
global array preset_params[4]   // Stored parameter values
global int preset_led_state = 0 // Stored LED state
global int preset_mode = 0      // Stored internal mode
global int smooth_counter = 0   // Parameter smoothing counter
```

## Preset Recall Implementation

```impala
// Smooth parameter transitions to avoid clicks
function recall_preset()
locals int i, int target, int current, int diff
{
    // Smooth parameter transitions
    i = 0;
    loop {
        if (i >= 4) break;
        
        target = global preset_params[i];
        current = (int)global params[i];
        diff = target - current;
        
        // Gradual transition over 64 samples
        global params[i] = current + (diff >> 6);
        
        i = i + 1;
    }
    
    // Update LED state
    global displayLEDs[0] = global preset_led_state;
    
    // Restore internal mode
    global preset_mode = global preset_mode;
}
```

## External Integration Points

```impala
// Standard MIDI CC mapping for presets
function handle_preset_change()
locals int cc_num, int value
{
    // Read CC number from parameter 4
    cc_num = (int)global params[4];
    // Read CC value from parameter 5
    value = (int)global params[5];
    
    if (cc_num == 0) {
        global params[0] = value << 3;  // CC0 -> param 0
    } else if (cc_num == 1) {
        global params[1] = value << 3;  // CC1 -> param 1
    } else if (cc_num == 2) {
        global params[2] = value << 3;  // CC2 -> param 2
    } else if (cc_num == 3) {
        global params[3] = value << 3;  // CC3 -> param 3
    }
}

// Program change handling
function handle_program_change()
locals int program_num
{
    program_num = (int)global params[6];
    if (program_num < 4) {  // Support 4 presets
        recall_preset();
    }
}

// Complete preset system with audio processing
function process()
locals int input_sample, int output_sample, int mix_level
{
    loop {
        // Handle external preset commands
        handle_preset_change();
        handle_program_change();
        
        // Process audio with current parameters
        input_sample = (int)global signal[0];
        
        // Apply basic processing using preset-controlled parameters
        mix_level = (int)global params[0];  // Main control
        output_sample = (input_sample * mix_level) >> 8;
        
        // Prevent clipping
        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        
        // Output processed signal
        global signal[0] = output_sample;
        global signal[1] = output_sample;
        
        // Show activity on LEDs
        global displayLEDs[1] = mix_level;
        global displayLEDs[2] = global preset_mode << 6;
        global displayLEDs[3] = (int)global params[3];
        
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
