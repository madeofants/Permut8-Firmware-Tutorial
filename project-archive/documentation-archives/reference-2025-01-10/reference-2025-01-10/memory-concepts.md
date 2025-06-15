# Memory Concepts

*Fundamental memory management principles for Permut8 firmware development*

## What This Covers

This reference explains the core memory management concepts essential for Permut8 firmware development. Understanding these principles is crucial for creating efficient, stable patches that perform reliably under real-time constraints.

## Memory Architecture Overview

### Memory Regions

The Permut8 provides several distinct memory areas, each optimized for specific purposes:

**Parameter Arrays**
- `params[8]`: Real-time parameter inputs (0-255 range)
- Direct hardware mapping for immediate knob/automation access
- No caching or buffering - values change in real-time

**Audio Buffers**
- `signal[2]`: Audio input/output buffers (-2047 to 2047, stereo pair)
- 12-bit signed audio samples
- Updated every processing cycle

**Display Arrays**
- `displayLEDs[4]`: Visual feedback array (0-255 range)
- Controls hardware LED brightness/patterns
- Updated once per processing cycle

**Global Arrays**
- Custom data storage for lookup tables, delay lines, and state
- Static allocation only - sizes must be known at compile time
- Most flexible memory region for custom algorithms

**Delay-Line Memory**
- Accessed via `read()`/`write()` native functions
- Hardware-optimized for audio delay effects
- Separate from global array space

## Static vs Dynamic Allocation

### Static Allocation (Recommended)

All memory should be allocated statically at compile time:

```impala
global array delay_buffer[128]   // Fixed size, allocated at compile time
global array sine_table[256]     // Lookup table, size known in advance
global int buffer_index = 0      // Simple variables, stack allocated
```

**Advantages:**
- Predictable memory usage
- No allocation failures during real-time operation
- Optimal performance - no allocation overhead
- Memory layout known at compile time

**Requirements:**
- Array sizes must be compile-time constants
- Cannot resize arrays during execution
- Total memory usage must fit within device limits

### Dynamic Allocation (Advanced)

Dynamic allocation is possible through memory pools but should be used sparingly:

```impala
// Memory pool management (see memory-pool-management.md)
global array memory_pool[256]
global int pool_allocation_pointer = 0
```

**Use Cases:**
- User-configurable buffer sizes
- Temporary scratch space during initialization
- Complex algorithms requiring variable memory

**Constraints:**
- Only allocate during initialization or non-real-time phases
- Implement careful error handling for allocation failures
- Consider fragmentation and pool exhaustion

## Memory Safety Patterns

### Bounds Checking

Always validate array access to prevent memory corruption:

```impala
// Explicit bounds checking
if (index >= 0 && index < ARRAY_SIZE) {
    value = array[index]  // Safe access
} else {
    value = 0  // Safe fallback
}

// Clamping for parameter conversion
if (index < 0) index = 0
if (index >= SIZE) index = SIZE - 1
value = array[index]  // Now guaranteed safe
```

### Circular Buffer Safety

Use modulo arithmetic for automatic wraparound:

```impala
// Safe circular advancement
write_pos = (write_pos + 1) % BUFFER_SIZE
read_pos = (read_pos + offset) % BUFFER_SIZE

// Handle negative offsets correctly
read_pos = write_pos - delay_samples
if (read_pos < 0) read_pos = read_pos + BUFFER_SIZE
```

### Initialization Patterns

Always initialize arrays to known values:

```impala
function init() {
    // Initialize delay buffer to silence
    for (int i = 0; i < DELAY_SIZE; i++) {
        delay_buffer[i] = 0
    }
    
    // Initialize lookup table
    for (int i = 0; i < TABLE_SIZE; i++) {
        sine_table[i] = compute_sine_value(i)
    }
    
    // Initialize position counters
    write_pos = 0
    read_pos = 0
}
```

## Performance Considerations

### Cache-Friendly Access Patterns

Sequential memory access maximizes cache efficiency:

```impala
// Good: Sequential access
for (int i = 0; i < BUFFER_SIZE; i++) {
    buffer[i] = process_sample(buffer[i])
}

// Avoid: Random access patterns
for (int i = 0; i < BUFFER_SIZE; i++) {
    int random_index = some_calculation(i)
    buffer[random_index] = value  // Poor cache behavior
}
```

### Data Locality

Group related data together in memory:

```impala
// Good: Related data grouped together
global array delay_buffer[128]
global int delay_write_pos = 0
global int delay_read_pos = 0
global int delay_feedback = 128

// Avoid: Scattered related data
global array delay_buffer[128]
global array some_other_data[64]
global int delay_write_pos = 0
global array more_unrelated_data[32]
global int delay_read_pos = 0
```

### Memory Usage Optimization

Minimize memory usage through efficient data structures:

```impala
// Use appropriate data types
global int small_counter = 0      // Full int for counters
global array large_buffer[1024]   // Arrays for bulk data

// Pack multiple flags into single integers
global int status_flags = 0
const int FLAG_RECORDING = 1
const int FLAG_PLAYING = 2
const int FLAG_OVERDUB = 4

// Check flags using bit operations
if ((status_flags & FLAG_RECORDING) != 0) {
    // Recording is active
}
```

## Common Memory Patterns

### Lookup Tables

Precomputed values for fast mathematical operations:

```impala
global array sine_table[256]
global array exp_table[128]

function init() {
    // Precompute expensive calculations
    for (int i = 0; i < 256; i++) {
        sine_table[i] = compute_sine(i * 2 * PI / 256)
    }
}

function fast_sine(int phase) {
    int index = (phase * 256) / PHASE_MAX
    if (index >= 256) index = 255
    return sine_table[index]
}
```

### Ring Buffers

Efficient FIFO data structures for audio processing:

```impala
global array ring_buffer[64]
global int write_head = 0
global int read_head = 0

function write_sample(int sample) {
    ring_buffer[write_head] = sample
    write_head = (write_head + 1) % 64
}

function read_sample() {
    int sample = ring_buffer[read_head]
    read_head = (read_head + 1) % 64
    return sample
}
```

### State Storage

Persistent state for complex algorithms:

```impala
// Oscillator state
global int osc_phase = 0
global int osc_frequency = 440

// Filter state  
global int filter_delay1 = 0
global int filter_delay2 = 0

// Envelope state
global int env_phase = 0
global int env_level = 0
```

## Memory Debugging

### Initialization Tracking

Track initialization to prevent use of uninitialized memory:

```impala
global int init_completed = 0

function init() {
    // Initialize all data structures
    initialize_buffers()
    initialize_tables()
    initialize_state()
    
    init_completed = 1  // Mark initialization complete
}

function process() {
    if (init_completed == 0) {
        return  // Skip processing until initialization complete
    }
    
    // Normal processing
    loop {
        // Process audio
        yield()
    }
}
```

### Buffer Overflow Detection

Monitor buffer usage during development:

```impala
global int max_buffer_used = 0

function track_buffer_usage(int current_usage) {
    if (current_usage > max_buffer_used) {
        max_buffer_used = current_usage
        // Display on LED for debugging
        displayLEDs[3] = (max_buffer_used * 255) / BUFFER_SIZE
    }
}
```

## Related Topics

- [Circular Buffer Guide](../cookbook/fundamentals/circular-buffer-guide.md) - Practical delay line implementation
- [Wavetable Synthesis](../cookbook/fundamentals/wavetable-synthesis.md) - Lookup table audio generation
- [State Machine Memory](../cookbook/fundamentals/state-machine-memory.md) - Complex state management
- [Memory Pool Management](../cookbook/fundamentals/memory-pool-management.md) - Dynamic allocation techniques
- [Memory Access Patterns](../performance/memory-access.md) - Performance optimization

---

*Master these fundamental memory concepts before advancing to specialized memory management techniques.*