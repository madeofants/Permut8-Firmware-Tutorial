# Global Variables Reference

## Overview

The Permut8 firmware environment provides several global variables that manage system state, audio processing, parameters, and visual feedback. These variables form the core interface between your firmware code and the Permut8 hardware, providing direct access to audio buffers, parameter values, LED controls, and timing systems.

This reference documents all global variables, their data types, access patterns, and usage guidelines for efficient firmware development.

## Audio Processing Variables

### signal[] - Audio Buffer Array

The primary audio processing buffer containing incoming and outgoing audio samples.

```impala
// Global audio buffer
int signal[BUFFER_SIZE];  // Typically 128 samples

// Basic audio processing
void process() {
    for (int i = 0; i < BUFFER_SIZE; i++) {
        signal[i] = signal[i] * 0.5;  // Simple gain reduction
    }
}
```

**Properties**:
- **Type**: `int[]` array
- **Range**: -2047 to 2047 (12-bit signed values)
- **Size**: Platform-dependent, typically 128 samples
- **Access**: Read/write for full patches, read-only for mod patches
- **Thread Safety**: Not thread-safe, access only in audio callback

**Usage Patterns**:

```impala
// Read input samples
int input_sample = signal[i];

// Write output samples
signal[i] = processed_sample;

// In-place processing (most common)
signal[i] = apply_effect(signal[i]);

// Buffer-wide operations
for (int i = 0; i < BUFFER_SIZE; i++) {
    signal[i] = lowpass_filter(signal[i], cutoff);
}
```

**Memory Considerations**:
- Direct hardware buffer access - very fast
- No bounds checking - ensure array indices are valid
- Cleared automatically between processing cycles
- Contains both left and right channels (interleaved or separate based on hardware configuration)

### positions[] - Memory Position Array

Memory addressing system for delay lines, oscillator tables, and state storage.

```impala
// Global memory positions
int positions[MAX_POSITIONS];  // Typically 16-32 positions

// Delay line implementation
void create_delay() {
    int delay_time = params[0] * 1000;  // Delay time in samples
    
    // Write to delay line
    memory[positions[0]] = signal[i];
    positions[0] = (positions[0] + 1) % delay_time;
    
    // Read from delay line
    int delayed_sample = memory[(positions[0] - delay_time + MEMORY_SIZE) % MEMORY_SIZE];
    signal[i] += delayed_sample * 0.3;  // Mix with original
}
```

**Properties**:
- **Type**: `int[]` array
- **Range**: 0 to MEMORY_SIZE-1
- **Size**: Platform-dependent, typically 16-32 positions
- **Access**: Read/write
- **Purpose**: Track current positions in circular buffers and delay lines

**Common Usage Patterns**:

```impala
// Circular buffer management
positions[buffer_id] = (positions[buffer_id] + 1) % buffer_size;

// Delay line reading with offset
int read_pos = (positions[delay_id] - delay_samples + MEMORY_SIZE) % MEMORY_SIZE;
int delayed = memory[read_pos];

// Oscillator table indexing
positions[osc_id] += frequency_increment;
if (positions[osc_id] >= table_size) {
    positions[osc_id] -= table_size;
}
```

**Best Practices**:
- Always use modulo operations to prevent buffer overruns
- Initialize positions to 0 in your init function
- Use different position indices for different delay lines or oscillators
- Consider fixed-point arithmetic for sub-sample precision

## Parameter System Variables

### params[] - Parameter Value Array

Real-time parameter values from knobs, switches, and MIDI controllers.

```impala
// Global parameter array
float params[MAX_PARAMS];  // Typically 8-16 parameters

// Parameter usage examples
void process() {
    float cutoff = params[0] * 0.5;      // Knob 1: Filter cutoff (0.0 to 0.5)
    float resonance = params[1] * 0.9;   // Knob 2: Resonance (0.0 to 0.9)
    int bypass = (int)params[2];         // Switch: Bypass mode (0 or 1)
    float mix = params[3];               // Knob 4: Dry/wet mix (0.0 to 1.0)
    
    for (int i = 0; i < BUFFER_SIZE; i++) {
        if (!bypass) {
            signal[i] = biquad_filter(signal[i], cutoff, resonance);
            signal[i] = signal[i] * mix + original[i] * (1.0 - mix);
        }
    }
}
```

**Properties**:
- **Type**: `float[]` array
- **Range**: 0.0 to 1.0 (normalized values)
- **Size**: Hardware-dependent, typically 8-16 parameters
- **Access**: Read-only (values updated by system)
- **Update Rate**: Audio rate or control rate depending on source

**Parameter Mapping Strategies**:

```impala
// Linear scaling
float frequency = params[0] * 1000.0 + 100.0;  // 100Hz to 1100Hz

// Exponential scaling (musical frequencies)
float freq = 440.0 * pow(2.0, (params[0] * 5.0 - 2.5));  // ~100Hz to ~3kHz

// Logarithmic scaling (decibels)
float gain_db = params[1] * 60.0 - 30.0;  // -30dB to +30dB
float gain_linear = pow(10.0, gain_db / 20.0);

// Discrete values
int mode = (int)(params[2] * 3.99);  // 4 discrete modes (0-3)

// Bipolar scaling
float detune = (params[3] - 0.5) * 2.0;  // -1.0 to +1.0
```

**Smoothing and Stability**:

```impala
// Simple parameter smoothing
static float smooth_cutoff = 0.0;
float target_cutoff = params[0] * 0.5;
smooth_cutoff += (target_cutoff - smooth_cutoff) * 0.01;  // 1% per sample

// Hysteresis for switch parameters
static int last_switch_state = 0;
float switch_val = params[2];
if (switch_val > 0.7 && last_switch_state == 0) {
    last_switch_state = 1;  // Switch on
} else if (switch_val < 0.3 && last_switch_state == 1) {
    last_switch_state = 0;  // Switch off
}
```

## Visual Feedback Variables

### displayLEDs[] - LED Control Array

Direct control over hardware LEDs for visual feedback and status indication.

```impala
// Global LED array
int displayLEDs[LED_COUNT];  // Typically 8-16 LEDs

// Basic LED control
void update_leds() {
    // Set LED brightness (0-255)
    displayLEDs[0] = (int)(params[0] * 255);  // LED 0 follows knob 1
    displayLEDs[1] = signal_level > threshold ? 255 : 0;  // LED 1 shows activity
    displayLEDs[2] = beat_detected ? 255 : 0;  // LED 2 shows beat detection
}
```

**Properties**:
- **Type**: `int[]` array
- **Range**: 0-255 (8-bit brightness values)
- **Size**: Hardware-dependent, typically 8-16 LEDs
- **Access**: Write-only (read current state for animations)
- **Update Rate**: Typically 60Hz refresh rate

**LED Animation Patterns**:

```impala
// Breathing effect
static float breath_phase = 0.0;
breath_phase += 0.02;  // Animation speed
int brightness = (int)((sin(breath_phase) + 1.0) * 127.5);
displayLEDs[0] = brightness;

// VU meter display
int signal_level = abs(signal[current_sample]) >> 3;  // Scale to 0-255
for (int led = 0; led < 8; led++) {
    displayLEDs[led] = signal_level > (led * 32) ? 255 : 0;
}

// Parameter value bargraph
int param_leds = (int)(params[0] * 8.0);  // 0-8 LEDs
for (int led = 0; led < 8; led++) {
    displayLEDs[led] = led < param_leds ? 255 : 0;
}

// Beat-synced flash
static int flash_counter = 0;
if (beat_detected) {
    flash_counter = 1000;  // Flash for 1000 samples
}
displayLEDs[7] = flash_counter > 0 ? 255 : 0;
if (flash_counter > 0) flash_counter--;
```

**LED Usage Best Practices**:

```impala
// Efficient LED updates (don't update every sample)
static int led_update_counter = 0;
led_update_counter++;
if (led_update_counter >= 441) {  // Update at ~100Hz (44.1kHz / 441)
    led_update_counter = 0;
    update_led_display();
}

// LED state management
typedef struct {
    int brightness;
    int target;
    float fade_rate;
} LED_State;

static LED_State led_states[LED_COUNT];

void smooth_led_update() {
    for (int i = 0; i < LED_COUNT; i++) {
        if (led_states[i].brightness != led_states[i].target) {
            float diff = led_states[i].target - led_states[i].brightness;
            led_states[i].brightness += (int)(diff * led_states[i].fade_rate);
            displayLEDs[i] = led_states[i].brightness;
        }
    }
}
```

## Timing and Synchronization Variables

### clock - System Clock Variable

Primary timing reference for tempo synchronization and time-based effects.

```impala
// Global clock variable
extern int clock;  // System sample counter

// Tempo-based effects
void tempo_delay() {
    static int samples_per_beat = 22050;  // 120 BPM at 44.1kHz
    
    // Calculate beat-synchronized delay time
    int beat_delay = samples_per_beat / 4;  // Sixteenth note delay
    
    // Use clock for timing reference
    int beat_position = clock % samples_per_beat;
    int is_beat = beat_position < 100;  // Beat trigger window
    
    if (is_beat) {
        trigger_beat_event();
    }
}
```

**Properties**:
- **Type**: `int` (signed integer)
- **Range**: 0 to INT_MAX (wraps around)
- **Access**: Read-only
- **Resolution**: Sample-accurate timing
- **Update**: Incremented every audio sample

**Timing Calculations**:

```impala
// BPM to samples conversion
float bpm = 120.0;
float sample_rate = 44100.0;
int samples_per_beat = (int)(sample_rate * 60.0 / bpm);

// Musical timing divisions
int whole_note = samples_per_beat * 4;
int half_note = samples_per_beat * 2;
int quarter_note = samples_per_beat;
int eighth_note = samples_per_beat / 2;
int sixteenth_note = samples_per_beat / 4;

// Phase calculation for LFOs
float lfo_frequency = 2.0;  // 2 Hz
float phase = (clock * lfo_frequency * 2.0 * PI) / sample_rate;
float lfo_value = sin(phase);
```

**Synchronization Patterns**:

```impala
// Beat detection and synchronization
static int last_beat_clock = 0;
int current_beat = clock / samples_per_beat;
int last_beat = last_beat_clock / samples_per_beat;

if (current_beat != last_beat) {
    // New beat detected
    trigger_beat_event();
    reset_phase_locked_oscillators();
}
last_beat_clock = clock;

// Clock division for sub-rhythms
int subdivision = 8;  // Eighth note subdivision
int sub_beat = (clock / (samples_per_beat / subdivision)) % subdivision;

// Swing timing implementation
float swing_amount = 0.2;  // 20% swing
int swing_offset = 0;
if (sub_beat % 2 == 1) {  // Odd subdivisions (off-beats)
    swing_offset = (int)(samples_per_beat * swing_amount / subdivision);
}
int swung_position = clock + swing_offset;
```

## System State Variables

### Memory Management Variables

Global variables for managing firmware memory and state.

```impala
// Memory management
extern int memory[];         // Global memory buffer
extern int MEMORY_SIZE;      // Total memory size
extern int BUFFER_SIZE;      // Audio buffer size

// Memory allocation patterns
static int delay_memory_start = 0;
static int delay_memory_size = 8192;
static int reverb_memory_start = 8192;
static int reverb_memory_size = 4096;

void init() {
    // Initialize memory regions
    for (int i = 0; i < delay_memory_size; i++) {
        memory[delay_memory_start + i] = 0;
    }
    for (int i = 0; i < reverb_memory_size; i++) {
        memory[reverb_memory_start + i] = 0;
    }
}
```

### Configuration Constants

System configuration values available as global constants.

```impala
// Audio system constants
#define SAMPLE_RATE     44100
#define BUFFER_SIZE     128
#define MAX_DELAY       32768
#define PI              3.14159265359

// Hardware constants
#define LED_COUNT       8
#define PARAM_COUNT     8
#define POSITION_COUNT  16

// Mathematical constants
#define SQRT2           1.41421356237
#define LOG2            0.69314718056
#define INV_LOG2        1.44269504089
```

**Usage in Calculations**:

```impala
// Frequency to phase increment
float freq_to_phase_inc(float frequency) {
    return (frequency * 65536.0) / SAMPLE_RATE;  // 16-bit fixed point
}

// Time to samples conversion
int ms_to_samples(float milliseconds) {
    return (int)(milliseconds * SAMPLE_RATE / 1000.0);
}

// Decibel conversions
float db_to_linear(float db) {
    return pow(10.0, db / 20.0);
}

float linear_to_db(float linear) {
    return 20.0 * log10(linear);
}
```

## Advanced Usage Patterns

### State Persistence

Managing firmware state across processing cycles.

```impala
// State structure for complex effects
typedef struct {
    float filter_state[4];    // Biquad filter memory
    int delay_positions[8];   // Multiple delay line positions
    float lfo_phase;          // LFO oscillator phase
    int beat_counter;         // Beat counting state
} EffectState;

static EffectState state = {0};  // Initialize to zero

void process() {
    // Use persistent state across audio buffers
    update_filter_state(state.filter_state);
    advance_delay_positions(state.delay_positions);
    update_lfo_phase(&state.lfo_phase);
}
```

### Multi-Parameter Coordination

Coordinating multiple parameters for complex behaviors.

```impala
// Parameter coordination matrix
void coordinate_parameters() {
    float master_intensity = params[0];
    
    // Scale other parameters by master control
    float effective_cutoff = params[1] * master_intensity;
    float effective_resonance = params[2] * master_intensity;
    float effective_drive = params[3] * (1.0 + master_intensity);
    
    // Cross-parameter modulation
    float lfo_rate = params[4] + (params[5] * 0.1);  // Fine tune with param 5
    float mod_depth = params[6] * params[7];         // Depth scaled by expression
    
    apply_coordinated_effects(effective_cutoff, effective_resonance, 
                             effective_drive, lfo_rate, mod_depth);
}
```

### Performance Optimization

Efficient access patterns for real-time performance.

```impala
// Cache frequently accessed values
void optimized_process() {
    // Cache parameter values (avoid repeated array access)
    float cutoff = params[0];
    float resonance = params[1];
    float mix = params[2];
    
    // Cache LED states for batch update
    static int led_cache[LED_COUNT];
    static int led_update_needed = 0;
    
    // Process audio with cached values
    for (int i = 0; i < BUFFER_SIZE; i++) {
        signal[i] = optimized_filter(signal[i], cutoff, resonance);
    }
    
    // Batch LED updates
    if (++led_update_needed >= 441) {  // ~100Hz update rate
        update_led_batch(led_cache);
        led_update_needed = 0;
    }
}
```

## Error Handling and Debugging

### Safe Array Access

Protecting against array bounds violations.

```impala
// Safe parameter access with bounds checking
float safe_param_read(int index, float default_value) {
    if (index >= 0 && index < PARAM_COUNT) {
        return params[index];
    }
    return default_value;
}

// Safe LED access with range clamping
void safe_led_write(int index, int brightness) {
    if (index >= 0 && index < LED_COUNT) {
        displayLEDs[index] = brightness < 0 ? 0 : (brightness > 255 ? 255 : brightness);
    }
}

// Safe memory access with wraparound
int safe_memory_read(int position) {
    return memory[position % MEMORY_SIZE];
}

void safe_memory_write(int position, int value) {
    memory[position % MEMORY_SIZE] = value;
}
```

### Debugging Variable Access

Using global variables for debugging and monitoring.

```impala
// Debug monitoring through LED display
void debug_display() {
    // Show parameter values on LEDs
    for (int i = 0; i < 4 && i < LED_COUNT; i++) {
        displayLEDs[i] = (int)(params[i] * 255);
    }
    
    // Show signal levels
    static int peak_level = 0;
    int current_level = abs(signal[0]) >> 3;  // Scale to 0-255
    if (current_level > peak_level) {
        peak_level = current_level;
    } else {
        peak_level = peak_level * 0.99;  // Slow decay
    }
    displayLEDs[7] = peak_level;
}

// Performance monitoring
static int max_processing_time = 0;
static int processing_start_clock = 0;

void monitor_performance() {
    processing_start_clock = clock;
    
    // ... do processing ...
    
    int processing_time = clock - processing_start_clock;
    if (processing_time > max_processing_time) {
        max_processing_time = processing_time;
        // Display on LED or use for optimization decisions
        displayLEDs[6] = processing_time > BUFFER_SIZE ? 255 : 0;  // Overrun warning
    }
}
```

## Best Practices Summary

### Memory Efficiency
- Cache frequently accessed global variables in local variables
- Use positions[] array efficiently for circular buffer management
- Initialize static variables to prevent unpredictable startup behavior
- Consider memory layout for cache efficiency in tight loops

### Real-Time Safety
- Avoid dynamic memory allocation in processing functions
- Use fixed-point arithmetic when possible for consistent timing
- Batch LED updates to reduce system overhead
- Validate array indices before access in debug builds

### Parameter Handling
- Implement parameter smoothing for artifact-free real-time changes
- Use appropriate scaling functions (linear, exponential, logarithmic)
- Consider hysteresis for switch parameters to prevent oscillation
- Cache parameter values when used multiple times per buffer

### Visual Feedback
- Update LEDs at appropriate rates (typically 60-100Hz)
- Use meaningful LED patterns that correspond to audio behavior
- Implement smooth LED transitions for professional appearance
- Reserve at least one LED for system status or error indication

### Debugging and Maintenance
- Use LED display for real-time debugging feedback
- Implement safe array access patterns to prevent crashes
- Monitor processing time and memory usage
- Document global variable usage for team development

---

This reference provides the foundation for effective use of Permut8's global variable system. Understanding these variables and their proper usage patterns is essential for creating efficient, stable, and professional firmware implementations.
