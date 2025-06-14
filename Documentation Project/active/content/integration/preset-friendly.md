# Preset-Friendly Firmware Design

Creating firmware that works seamlessly with preset systems - enables users to save, share, and recall their settings reliably across different hosts and hardware.

> **Note**: This file contains design concepts with some non-Impala syntax. For a complete working implementation, see [preset-system.md](preset-system.md) which provides proper Impala syntax for preset integration.

## Preset System Fundamentals

Presets are collections of parameter values that recreate a specific sound or configuration. Well-designed firmware makes preset management effortless for users.

### Core Preset Requirements

```impala
// All preset data should be contained in parameter array
// No hidden state that presets can't capture
let reverb_size = params[0];      // Saved in presets
let reverb_damping = params[1];   // Saved in presets  
let output_level = params[2];     // Saved in presets

// Derived values recalculated from parameters
let room_delay = reverb_size * MAX_DELAY_SAMPLES;  // Not saved - computed
let damping_coeff = 1.0 - reverb_damping;         // Not saved - computed
```

**Key Principle**: Parameters contain the complete sonic state - everything else is computed from them.

### Parameter Organization for Presets

```impala
// Group related parameters logically
// Params 0-2: Core sound shaping
let filter_cutoff = params[0];
let filter_resonance = params[1]; 
let filter_type = params[2];       // 0=low, 0.33=high, 0.66=band, 1=notch

// Params 3-5: Modulation  
let lfo_rate = params[3];
let lfo_depth = params[4];
let lfo_target = params[5];        // Which parameter LFO modulates

// Params 6-7: Output section
let output_gain = params[6];
let bypass_state = params[7];
```

**Benefit**: Users can quickly understand and modify presets - similar parameters are grouped together.

## State Management for Presets

### Immediate Parameter Response

```impala
// Parameters take effect immediately when changed
let current_cutoff = params[0];    // Use current value directly

// NO startup delays or gradual parameter loading
if (preset_just_loaded) {
    // Don't do this - creates confusion
    // target_cutoff = params[0];
    // current_cutoff = lerp(current_cutoff, target_cutoff, 0.01);
}

// Apply parameter value right away
let filter_output = apply_filter(input, current_cutoff, params[1]);
```

**User Experience**: When a preset loads, the sound changes immediately to match what's saved.

### Preserving Temporal State

```impala
// Some state should NOT be reset by presets
static let phase_accumulator = 0.0;    // LFO phase continues running
static let random_seed = 12345;        // Random sequences continue
static let delay_buffer[MAX_DELAY];    // Audio in delay line persists

// Reset only when musically appropriate
if (params[7] > 0.5) {  // "Reset LFO" parameter
    phase_accumulator = 0.0;           // User explicitly requested reset
}
```

**Guideline**: Preserve audio continuity - don't create clicks or silence when loading presets.

### Parameter Smoothing Across Presets

```impala
// Smooth only parameters that cause audio artifacts
let target_gain = params[6];
static let smoothed_gain = 0.5;        // Initialize to safe default

// Use fast smoothing to reach new preset values quickly
let smooth_factor = 0.95;              // Faster than normal parameter smoothing
smoothed_gain = smoothed_gain * smooth_factor + target_gain * (1.0 - smooth_factor);

let output = input * smoothed_gain;
```

**Balance**: Fast enough that presets respond quickly, smooth enough to avoid clicks.

## Preset Validation and Error Handling

### Parameter Range Validation

```impala
// Validate all parameters on preset load
for (int i = 0; i < NUM_PARAMETERS; i++) {
    // Clamp to valid range
    if (params[i] < 0.0) params[i] = 0.0;
    if (params[i] > 1.0) params[i] = 1.0;
    
    // Handle invalid floating point values
    if (isnan(params[i]) || isinf(params[i])) {
        params[i] = get_default_value(i);  // Use safe default
    }
}
```

### Graceful Degradation

```impala
// Handle missing or corrupted parameter data
let expected_param_count = 8;
let actual_param_count = get_preset_param_count();

if (actual_param_count < expected_param_count) {
    // Fill missing parameters with defaults
    for (int i = actual_param_count; i < expected_param_count; i++) {
        params[i] = get_default_value(i);
    }
}

// Function to provide sensible defaults
float get_default_value(int param_index) {
    switch (param_index) {
        case 0: return 0.5;    // Filter cutoff - middle position
        case 1: return 0.0;    // Resonance - minimal
        case 2: return 0.0;    // Filter type - lowpass
        case 6: return 0.75;   // Output gain - slightly below unity
        case 7: return 0.0;    // Bypass - effect enabled
        default: return 0.5;   // Generic middle value
    }
}
```

**Result**: Presets work even when created with older firmware versions or corrupted data.

## Preset-Friendly Parameter Design

### Meaningful Default Values

```impala
// Choose defaults that create useful starting points
let mix_amount = params[0];            // Default 0.5 = 50% wet/dry mix
let delay_time = params[1];            // Default 0.33 = 1/8 note timing  
let feedback = params[2];              // Default 0.25 = moderate feedback
let tone_control = params[3];          // Default 0.5 = neutral tone

// Avoid defaults that create silence or extreme sounds
// Bad: Default delay feedback of 0.0 (no delay heard)
// Good: Default delay feedback of 0.25 (clearly audible but stable)
```

### Parameter Scaling for Musical Results

```impala
// Scale parameters so middle positions are musically useful
let filter_param = params[0];

// Linear scaling often doesn't work musically
// let bad_cutoff = filter_param * 20000.0;  // 50% = 10kHz (too high)

// Logarithmic scaling puts useful frequencies in middle range
let min_freq = 80.0;   // 80 Hz minimum (useful bass)
let max_freq = 8000.0; // 8 kHz maximum (useful treble)
let log_range = log(max_freq / min_freq);
let musical_cutoff = min_freq * exp(filter_param * log_range);
// 50% = ~800 Hz (musically useful midrange)
```

### Inter-Parameter Relationships

```impala
// Design parameters to work well together in any combination
let distortion_amount = params[0];
let distortion_output = params[1];

// Auto-compensate for level changes
let input_gain = 1.0 + distortion_amount * 3.0;     // More drive = more input gain
let output_gain = (1.0 + distortion_amount) * params[1]; // Compensated output level

// This way, any preset combination sounds balanced
let processed = distort(input * input_gain) * output_gain;
```

## Factory Preset Strategies

### Covering the Parameter Space

```impala
// Design factory presets to demonstrate parameter ranges
// Preset 1: "Subtle" - parameters near default positions
// params = [0.4, 0.3, 0.6, 0.5, 0.2, 0.7, 0.8, 0.0]

// Preset 2: "Extreme" - parameters at useful extremes  
// params = [0.9, 0.8, 1.0, 0.1, 0.9, 0.3, 0.9, 0.0]

// Preset 3: "Minimal" - minimal effect for subtle use
// params = [0.1, 0.0, 0.2, 0.5, 0.1, 0.8, 0.7, 0.0]

// Each preset teaches users about parameter behavior
```

### Educational Preset Design

```impala
// Create presets that isolate specific features
// "Just Filter" preset - only filter active
let educational_preset_1[] = {
    0.7,  // Filter cutoff - clearly audible
    0.3,  // Filter resonance - noticeable but not harsh
    0.0,  // Filter type - lowpass
    0.0,  // LFO rate - no modulation
    0.0,  // LFO depth - no modulation  
    0.0,  // LFO target - unused
    0.8,  // Output gain - clear level
    0.0   // Bypass - effect enabled
};

// "Just LFO" preset - only modulation active
let educational_preset_2[] = {
    0.5,  // Filter cutoff - neutral
    0.0,  // Filter resonance - minimal
    0.0,  // Filter type - lowpass
    0.4,  // LFO rate - medium speed
    0.6,  // LFO depth - clearly audible
    0.0,  // LFO target - modulate cutoff
    0.8,  // Output gain - clear level
    0.0   // Bypass - effect enabled
};
```

## Preset Compatibility Across Versions

### Forward Compatibility

```impala
// Design parameter layout for future expansion
// Always add new parameters at the end
let version_1_params[] = {
    params[0],  // Filter cutoff - established in v1
    params[1],  // Filter resonance - established in v1
    params[2],  // Output gain - established in v1
};

// Version 2 adds new features at end
let version_2_params[] = {
    params[0],  // Filter cutoff - unchanged position
    params[1],  // Filter resonance - unchanged position  
    params[2],  // Output gain - unchanged position
    params[3],  // NEW: LFO rate - added in v2
    params[4],  // NEW: LFO depth - added in v2
};

// Old presets still work - missing parameters use defaults
```

### Backward Compatibility Testing

```impala
// Test preset loading with missing parameters
void test_preset_compatibility() {
    // Simulate loading preset from older firmware version
    float old_preset[3] = {0.7, 0.3, 0.8};  // Only 3 parameters
    
    // Load what's available
    for (int i = 0; i < 3; i++) {
        params[i] = old_preset[i];
    }
    
    // Fill remaining with defaults
    for (int i = 3; i < NUM_PARAMETERS; i++) {
        params[i] = get_default_value(i);
    }
    
    // Verify firmware still works correctly
    assert(firmware_state_is_valid());
}
```

## Testing Preset Functionality

### Automated Preset Testing

```impala
// Test all parameter combinations work in presets
void test_preset_robustness() {
    for (int test = 0; test < 1000; test++) {
        // Generate random parameter values
        for (int i = 0; i < NUM_PARAMETERS; i++) {
            params[i] = random_float(0.0, 1.0);
        }
        
        // Process audio with these settings
        float test_input = generate_test_signal();
        float test_output = process_audio(test_input);
        
        // Verify output is valid
        assert(!isnan(test_output));
        assert(!isinf(test_output));
        assert(fabs(test_output) < MAX_SAFE_LEVEL);
    }
}
```

### User Testing Checklist

1. **Preset Loading Speed**: Presets change sound immediately
2. **Parameter Consistency**: Same preset always sounds the same
3. **No Audio Artifacts**: No clicks, pops, or silence when loading presets  
4. **Parameter Interaction**: All parameter combinations work in presets
5. **Host Integration**: Presets work in all major DAWs and hardware
6. **File Compatibility**: Presets created in different hosts are interchangeable

### Common Preset Problems to Avoid

```impala
// DON'T: Hidden state that presets can't capture
static let secret_mode = calculate_something_complex();  // Lost when preset loads

// DON'T: Parameters that only work in certain combinations  
if (params[0] > 0.8 && params[1] < 0.2) {
    // This combination creates special behavior - confusing in presets
}

// DON'T: Initialization that breaks preset loading
void init_firmware() {
    // Bad: Always reset to default values
    params[0] = 0.5;  // Overwrites loaded preset!
    
    // Good: Only set defaults if no preset is loaded
    if (!preset_was_loaded) {
        params[0] = 0.5;
    }
}
```

This comprehensive approach ensures your firmware integrates seamlessly with any preset system, making it more professional and user-friendly for preset sharing and workflow integration.
