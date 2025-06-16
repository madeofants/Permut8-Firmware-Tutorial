# Make a Delay

## What This Does
Creates a simple delay effect with adjustable delay time and feedback amount. The delayed signal is mixed with the original to create echo effects ranging from short slap-back delays to long ambient trails.

### **Approach: Custom Firmware (Manual Memory Management)**

This recipe demonstrates **Approach 2: Custom Firmware** - manually implementing delay using custom memory management instead of using Permut8's built-in SUB operator.

**Why This Approach?**:
- **Educational** - shows how delays work at the memory level
- **Custom control** - full control over delay algorithm and feedback  
- **Learning foundation** - understand delay concepts before using operators
- **Flexibility** - can implement delay variations not possible with standard operators

**How It Works**:
```
Audio Input → [Custom code manages delay buffer] → Audio Output
```
- Custom code manually reads/writes to delay memory using `read()` and `write()`
- Manual circular buffer management with `delayIndex` tracking
- Custom feedback mixing and clipping control

**Recommended Alternative - Original Operators**:
For most delay effects, use **Approach 1: Original Operators**:
- **Instruction 1**: SUB operator with delay time operands (more efficient)
- **Instruction 2**: NOP or additional modulation operators
- **Interface**: Set delay time via switches/LED displays or knob override
- **Benefits**: Hardware-optimized, automatic memory management, can combine with other operators

**When to Use Custom Firmware**:
- Learning how delays work internally
- Need custom delay algorithms (multi-tap, modulated, etc.)
- Want to combine delay with non-delay processing

## Quick Reference
**Parameters**:
- **Control 1 (params[0])**: Delay time (1-1000 samples, timing varies with sample rate)
- **Control 2 (params[1])**: Feedback amount (0-90% to prevent runaway)
- **Control 3 (params[5])**: [Available for expansion]
- **Control 4 (params[6])**: [Available for expansion]

**Key Concepts**: Memory read/write operations, feedback loops, circular buffering

## Complete Code
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine
extern native read              // Read from delay line memory
extern native write             // Write to delay line memory

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Delay processing variables
global array delayBuffer[2]     // Temporary buffer for memory operations
global int delayIndex = 0       // Current position in delay buffer
global int maxDelayTime = 1000  // Maximum delay in samples (timing varies with sample rate)

// Utility function for audio clipping
function clipAudio(int sample) returns int clipped {
    if (sample > 2047) clipped = 2047
    else if (sample < -2047) clipped = -2047
    else clipped = sample
}

function process() {
    loop {
        operate1()  // Process left channel
        operate2()  // Process right channel
    }
}

function operate1() {
    // === PARAMETER READING ===
    int delayTime = ((int)params[0] * maxDelayTime / 255) + 1  // 1-1000 samples
    int feedbackAmount = (int)params[1] * 90 / 255             // 0-90% feedback
    
    // === DELAY PROCESSING ===
    // Read delayed sample from memory (fixed offset from write position)
    int readPos = (delayIndex - delayTime + maxDelayTime) % maxDelayTime
    read(readPos, 1, delayBuffer)
    int delayedSample = delayBuffer[0]
    
    // Mix input with delayed signal for output
    int input = signal[0]
    int output = input + (delayedSample * feedbackAmount / 100)
    output = clipAudio(output)
    
    // Store new sample (input + feedback) for next delay iteration
    delayBuffer[0] = input + (delayedSample * feedbackAmount / 100)
    delayBuffer[0] = clipAudio(delayBuffer[0])
    
    write(delayIndex, 1, delayBuffer)
    
    // Update delay buffer position (fixed circular buffer)
    delayIndex = (delayIndex + 1) % maxDelayTime
    
    // === OUTPUT AND VISUALIZATION ===
    // Show delay activity on LEDs (lights when delayed signal is audible)
    int ledPattern = 0
    if (delayedSample > 100 || delayedSample < -100) {
        ledPattern = (1 << (delayIndex % 8))
    }
    displayLEDs[0] = ledPattern
    
    signal[0] = output
    yield()
}

function operate2() {
    // === RIGHT CHANNEL PROCESSING ===
    // Identical delay processing for right channel using offset memory location
    int delayTime = ((int)params[0] * maxDelayTime / 255) + 1
    int feedbackAmount = (int)params[1] * 90 / 255
    
    // Use offset memory location to avoid interference with left channel
    int readPos = ((delayIndex - delayTime + maxDelayTime) % maxDelayTime) + maxDelayTime
    read(readPos, 1, delayBuffer)
    int delayedSample = delayBuffer[0]
    
    int input = signal[1]
    int output = input + (delayedSample * feedbackAmount / 100)
    output = clipAudio(output)
    
    // Store sample with feedback
    delayBuffer[0] = input + (delayedSample * feedbackAmount / 100)
    delayBuffer[0] = clipAudio(delayBuffer[0])
    
    write(delayIndex + maxDelayTime, 1, delayBuffer)
    
    signal[1] = output
    yield()
}
```

## Try These Changes
- **Longer delays**: Increase `maxDelayTime` to 5000 or 10000 samples for longer echoes
- **Shorter delays**: Set `maxDelayTime` to 100 for tight slap-back echo effects
- **Stereo ping-pong**: Use different delay times for left/right channels to bounce audio
- **Higher feedback**: Carefully increase the 90% limit for more repeats (watch for runaway!)
- **Modulated delay**: Add LFO modulation to `delayTime` for chorus-like effects

## How It Works
The delay effect stores incoming audio samples in memory using the `read()` and `write()` functions, then plays them back after a specified time interval. The core algorithm uses a fixed-size circular buffer approach where `delayIndex` tracks the current write position, wrapping at `maxDelayTime` to maintain consistent memory management.

The read position is calculated as an offset from the write position: `(delayIndex - delayTime + maxDelayTime) % maxDelayTime`. This ensures the delay time can be changed without causing audio artifacts or memory discontinuity.

The feedback control mixes a percentage of the delayed signal back into the delay buffer itself, creating multiple repeats that gradually fade away. This feedback loop is carefully limited to 90% to prevent mathematical runaway that would cause infinite amplification.

The memory addressing uses separate regions for left and right channels (`delayIndex` vs `delayIndex + maxDelayTime`) to prevent interference between stereo channels while maintaining proper circular buffer behavior for both channels.

## Related Techniques
- **[Chorus Effect](#chorus-effect)**: Uses multiple short delays for thickening
- **[Sync to Tempo](#sync-to-tempo)**: Tempo-synchronized delay timing
- **[Memory Basics](#memory-basics)**: Memory read/write fundamentals

---
*Part of the [Permut8 Cookbook](#permut8-cookbook) series*