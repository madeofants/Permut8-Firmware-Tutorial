# Control Flow - Conditional Logic in Permut8 Firmware

Control flow determines how your audio processing code makes decisions and repeats operations. Permut8's real-time constraints require efficient conditional logic that doesn't disrupt audio processing.

## Conditional Statements

### Basic if/else for Audio Logic

Use conditionals to switch between processing modes:

```impala
fn operate1(input: int) -> int {
    let mode: int = params[0];
    
    if mode < 85 {
        // Low-pass mode
        return lowpass_filter(input);
    } else if mode < 170 {
        // High-pass mode
        return highpass_filter(input);
    } else {
        // Band-pass mode
        return bandpass_filter(input);
    }
}
```

### Threshold-Based Processing

Common pattern for gates, compressors, and envelope followers:

```impala
static mut envelope: int = 0;

fn operate1(input: int) -> int {
    let threshold: int = params[1] * 8;  // Scale parameter
    let abs_input: int = if input < 0 { -input } else { input };
    
    if abs_input > threshold {
        // Above threshold: fast attack
        envelope = (envelope * 7 + abs_input) / 8;
    } else {
        // Below threshold: slow release
        envelope = (envelope * 31) / 32;
    }
    
    return input * envelope / 2047;
}
```

## Loop Constructs

### For Loops for Array Processing

Process multiple samples or initialize buffers:

```impala
static mut reverb_buffer: [int; 512] = [0; 512];

fn clear_reverb() {
    for i in 0..512 {
        reverb_buffer[i] = 0;
    }
}

fn process_multi_tap_delay(input: int) -> int {
    let mut output: int = input;
    
    // Process multiple delay taps
    for tap in 0..4 {
        let delay_samples: int = (tap + 1) * 64;
        let delayed: int = reverb_buffer[(read_pos + delay_samples) % 512];
        output += delayed / (tap + 2);  // Decreasing amplitude per tap
    }
    
    return output;
}
```

### While Loops for Sample Processing

Essential for full patches that process continuous audio:

```impala
fn process() {
    while true {
        let input: int = signal[0];
        
        // Your DSP algorithm here
        let processed: int = apply_effects(input);
        
        signal[0] = processed;
        yield();  // CRITICAL: Let system process next sample
    }
}
```

### Conditional Loops for State Machines

Handle complex audio behaviors:

```impala
static mut state: int = 0;  // 0=idle, 1=attack, 2=sustain, 3=release

fn envelope_processor(trigger: bool) -> int {
    while state > 0 {
        if state == 1 && envelope >= target_level {
            state = 2;  // Move to sustain
            break;
        }
        if state == 3 && envelope <= 0 {
            state = 0;  // Return to idle
            break;
        }
        break;  // Process one step per sample
    }
    
    if trigger && state == 0 {
        state = 1;  // Start attack
    }
    
    return envelope;
}
```

## Match Expressions

### Parameter-Based Mode Switching

Clean way to handle multiple processing modes:

```impala
fn operate1(input: int) -> int {
    let effect_mode: int = params[0] / 32;  // 0-7 range
    
    match effect_mode {
        0 => input,                           // Bypass
        1 => apply_chorus(input),            // Chorus
        2 => apply_flanger(input),           // Flanger
        3 => apply_phaser(input),            // Phaser
        4 => apply_reverb(input),            // Reverb
        5 => apply_delay(input),             // Delay
        6 => apply_distortion(input),        // Distortion
        _ => apply_filter(input),            // Default: Filter
    }
}
```

### Waveform Selection

Efficient oscillator waveform switching:

```impala
fn generate_oscillator(phase: int, waveform: int) -> int {
    match waveform {
        0 => sine_table[phase >> 12],                    // Sine wave
        1 => if phase < 0x80000 { 1024 } else { -1024 }, // Square wave
        2 => (phase >> 8) - 1024,                        // Sawtooth
        3 => triangle_wave(phase),                       // Triangle
        _ => 0,                                          // Silence
    }
}
```

## Real-Time Considerations

### Avoid Long Loops

Keep loops short to maintain real-time performance:

```impala
// BAD: This could take too long
fn bad_initialization() {
    for i in 0..10000 {
        large_buffer[i] = complex_calculation(i);
    }
}

// GOOD: Spread work across multiple samples
static mut init_progress: int = 0;

fn good_initialization() {
    if init_progress < 10000 {
        // Do a small amount of work each sample
        for i in 0..10 {
            if init_progress + i < 10000 {
                large_buffer[init_progress + i] = complex_calculation(init_progress + i);
            }
        }
        init_progress += 10;
    }
}
```

### Predictable Branches

Design conditionals with consistent execution time:

```impala
// Consistent execution time regardless of branch
fn balanced_processing(input: int, mode: bool) -> int {
    if mode {
        return expensive_effect_a(input);
    } else {
        return expensive_effect_b(input);  // Similar cost to effect_a
    }
}
```

## Error Handling Patterns

### Graceful Parameter Validation

```impala
fn safe_delay_effect(input: int) -> int {
    let delay_time: int = params[0];
    
    // Clamp parameter to safe range
    let safe_delay: int = if delay_time > 200 { 200 } else { delay_time };
    let final_delay: int = if safe_delay < 1 { 1 } else { safe_delay };
    
    return apply_delay(input, final_delay);
}
```

Effective control flow ensures your DSP algorithms respond correctly to user input while maintaining the precise timing required for professional audio quality.
