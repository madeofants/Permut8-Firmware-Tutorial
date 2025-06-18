# Memory Management Reference

## What This Is
How to read from and write to Permut8's delay memory system. Essential for creating delays, reverbs, loopers, and any effect that needs to store and recall audio.

## Core Concepts

### Delay Memory System
Permut8 provides a large circular buffer for storing audio samples. Your firmware can read from and write to any position in this memory.

**Key properties:**
- **Circular buffer**: Automatically wraps when you exceed memory size
- **Stereo interleaved**: Left and right samples stored together  
- **12-bit samples**: Range -2047 to 2047
- **Position-based**: Access by memory offset, not time

### Memory Operations
```impala
read(int offset, int frameCount, pointer buffer)
write(int offset, int frameCount, pointer buffer)
```

**Frame**: One stereo pair (left + right sample)  
**Offset**: Position in delay memory (samples, not frames)  
**Buffer**: Array to hold interleaved stereo data

## Basic Read Operations

### Reading Single Frames
```impala
function process() {
    array delayedSamples[2];  // Buffer for one stereo frame
    
    // Read from 1000 samples ago
    read(clock - 1000, 1, delayedSamples);
    
    int delayedLeft = delayedSamples[0];
    int delayedRight = delayedSamples[1];
    
    // Mix with current input
    signal[0] = (signal[0] + delayedLeft) >> 1;
    signal[1] = (signal[1] + delayedRight) >> 1;
    
    yield();
}
```

### Reading Multiple Frames
```impala
function process() {
    array buffer[8];  // 4 stereo frames = 8 samples
    
    // Read 4 consecutive frames
    read(clock - 2000, 4, buffer);
    
    // Process each frame
    int sum = 0;
    int i;
    for (i = 0 to 4) {
        sum = sum + buffer[i * 2];     // Sum left channels
        sum = sum + buffer[i * 2 + 1]; // Sum right channels
    }
    
    // Mix averaged delay with input
    signal[0] = (signal[0] + (sum >> 3)) >> 1;  // Divide by 8
    signal[1] = signal[0];  // Mono output
    
    yield();
}
```

### Reading with Variable Delay
```impala
global int delayTime = 1000;

function update() {
    // Convert knob to delay time (100-10000 samples)
    int knobValue = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    delayTime = 100 + (knobValue * 38);  // Scale to range
    
    // LED feedback shows delay time
    displayLEDs[0] = knobValue;
}

function process() {
    array delayed[2];
    
    read(clock - delayTime, 1, delayed);
    
    // Simple delay effect
    signal[0] = (signal[0] + delayed[0]) >> 1;
    signal[1] = (signal[1] + delayed[1]) >> 1;
    
    yield();
}
```

## Basic Write Operations

### Writing Current Input
```impala
function process() {
    // Always write current input to memory
    array currentFrame[2] = {signal[0], signal[1]};
    write(clock, 1, currentFrame);
    
    // Read delayed version
    array delayed[2];
    read(clock - 5000, 1, delayed);
    
    // Output is delayed signal
    signal[0] = delayed[0];
    signal[1] = delayed[1];
    
    yield();
}
```

### Selective Writing (Write Protection)
```impala
function process() {
    array input[2] = {signal[0], signal[1]};
    
    // Only write if write-protect switch is off
    if (((int)params[SWITCHES_PARAM_INDEX] & SWITCHES_WRITE_PROTECT_MASK) == 0) {
        write(clock, 1, input);
    }
    
    // Always read delayed signal
    array delayed[2];
    read(clock - 2000, 1, delayed);
    signal[0] = delayed[0];
    signal[1] = delayed[1];
    
    yield();
}
```

### Writing Processed Audio
```impala
function process() {
    // Read previous sample
    array previous[2];
    read(clock - 1, 1, previous);
    
    // Create feedback by mixing input with previous
    int processedLeft = signal[0] + (previous[0] >> 2);   // 25% feedback
    int processedRight = signal[1] + (previous[1] >> 2);
    
    // Clip to prevent overflow
    if (processedLeft > 2047) processedLeft = 2047;
    if (processedLeft < -2047) processedLeft = -2047;
    if (processedRight > 2047) processedRight = 2047;
    if (processedRight < -2047) processedRight = -2047;
    
    // Write processed audio back to memory
    array toWrite[2] = {processedLeft, processedRight};
    write(clock, 1, toWrite);
    
    // Output the processed signal
    signal[0] = processedLeft;
    signal[1] = processedRight;
    
    yield();
}
```

## Position Array (Mod Patches)

### Understanding Positions
For mod patches, the `positions[]` array contains memory read positions instead of audio samples.

```impala
global array positions[2]  // [left_position, right_position]
```

**Position format:** 20-bit fixed point (16.4)
- **Integer part**: Memory offset (16 bits)
- **Fractional part**: For interpolation (4 bits)
- **Range**: 0x00000 to 0xFFFFF

### Basic Position Processing
```impala
function operate1() 
returns int processed {
    // Add delay to both channels
    int delayAmount = 1000 << 4;  // 1000 samples, shift for fixed point
    
    positions[0] = positions[0] + delayAmount;
    positions[1] = positions[1] + delayAmount;
    
    processed = 1;  // Tell Permut8 we handled the positions
}
```

### Parameter-Controlled Position Offset
```impala
global int positionOffset = 0;

function update() {
    // Convert knob to position offset
    int knobValue = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    positionOffset = (knobValue * 100) << 4;  // Scale and convert to fixed point
    
    // LED shows offset amount
    displayLEDs[0] = knobValue;
}

function operate1()
returns int processed {
    // Apply offset to positions
    positions[0] = positions[0] + positionOffset;
    positions[1] = positions[1] + positionOffset;
    
    processed = 1;
}
```

### Stereo Position Effects
```impala
function operate1()
returns int processed {
    // Different delays for left and right
    int leftDelay = ((int)params[OPERAND_1_HIGH_PARAM_INDEX] * 50) << 4;
    int rightDelay = ((int)params[OPERAND_1_LOW_PARAM_INDEX] * 50) << 4;
    
    positions[0] = positions[0] + leftDelay;
    positions[1] = positions[1] + rightDelay;
    
    // LED feedback
    displayLEDs[0] = leftDelay >> 8;   // Show left delay
    displayLEDs[1] = rightDelay >> 8;  // Show right delay
    
    processed = 1;
}
```

### Position Interpolation
```impala
function operate1()
returns int processed {
    // Smooth position changes using fractional part
    int targetOffset = ((int)params[OPERAND_1_HIGH_PARAM_INDEX] * 100) << 4;
    
    // Current positions with fractional interpolation
    int currentLeft = positions[0] & 0xF;   // Get fractional part
    int currentRight = positions[1] & 0xF;
    
    // Smooth interpolation toward target
    positions[0] = (positions[0] & 0xFFFF0) | ((currentLeft + 1) & 0xF);
    positions[1] = (positions[1] & 0xFFFF0) | ((currentRight + 1) & 0xF);
    
    // Add main offset
    positions[0] = positions[0] + targetOffset;
    positions[1] = positions[1] + targetOffset;
    
    processed = 1;
}
```

## Advanced Patterns

### Multi-Tap Delay
```impala
function process() {
    array input[2] = {signal[0], signal[1]};
    array tap1[2], tap2[2], tap3[2];
    
    // Write input to memory
    write(clock, 1, input);
    
    // Read from multiple delay taps
    read(clock - 1000, 1, tap1);    // 1000 samples
    read(clock - 2500, 1, tap2);    // 2500 samples  
    read(clock - 4000, 1, tap3);    // 4000 samples
    
    // Mix all taps
    int leftMix = (tap1[0] + tap2[0] + tap3[0]) / 3;
    int rightMix = (tap1[1] + tap2[1] + tap3[1]) / 3;
    
    // Combine with input
    signal[0] = (signal[0] + leftMix) >> 1;
    signal[1] = (signal[1] + rightMix) >> 1;
    
    yield();
}
```

### Feedback Loop with Processing
```impala
global float feedbackGain = 0.5;

function update() {
    // Convert knob to feedback amount (0.0 - 0.9)
    int knobValue = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    feedbackGain = itof(knobValue) * 0.9 / 255.0;
}

function process() {
    array input[2] = {signal[0], signal[1]};
    array feedback[2];
    
    // Read feedback from delay line
    read(clock - 2000, 1, feedback);
    
    // Apply feedback gain and mix with input
    int fbLeft = ftoi(itof(feedback[0]) * feedbackGain);
    int fbRight = ftoi(itof(feedback[1]) * feedbackGain);
    
    int processedLeft = input[0] + fbLeft;
    int processedRight = input[1] + fbRight;
    
    // Soft clipping to prevent runaway feedback
    if (processedLeft > 2047) processedLeft = 2047;
    else if (processedLeft < -2047) processedLeft = -2047;
    if (processedRight > 2047) processedRight = 2047;
    else if (processedRight < -2047) processedRight = -2047;
    
    // Write processed signal back
    array toWrite[2] = {processedLeft, processedRight};
    write(clock, 1, toWrite);
    
    // Output processed signal
    signal[0] = processedLeft;
    signal[1] = processedRight;
    
    yield();
}
```

### Reverse Buffer
```impala
global int bufferSize = 10000;
global int writePos = 0;

function process() {
    array input[2] = {signal[0], signal[1]};
    array output[2];
    
    // Write to current position
    write(writePos, 1, input);
    
    // Read from reverse position
    int readPos = writePos - bufferSize;
    if (readPos < 0) readPos = readPos + bufferSize;
    
    read(readPos, 1, output);
    
    // Move write position
    writePos = writePos + 1;
    if (writePos >= bufferSize) writePos = 0;
    
    signal[0] = output[0];
    signal[1] = output[1];
    
    yield();
}
```

### Granular Buffer
```impala
global int grainSize = 1000;
global int grainPos = 0;
global int grainDir = 1;

function update() {
    // Grain size from knob (100-5000 samples)
    int knobValue = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    grainSize = 100 + (knobValue * 19);  // Scale to range
}

function process() {
    array input[2] = {signal[0], signal[1]};
    array grain[2];
    
    // Always write input
    write(clock, 1, input);
    
    // Read from grain position
    read(clock - 5000 - grainPos, 1, grain);
    
    // Move grain position
    grainPos = grainPos + grainDir;
    
    // Reverse direction at grain boundaries
    if (grainPos >= grainSize || grainPos <= 0) {
        grainDir = -grainDir;
    }
    
    // Apply simple envelope to avoid clicks
    int envelope = 255;
    if (grainPos < 100) envelope = grainPos * 255 / 100;
    if (grainPos > grainSize - 100) envelope = (grainSize - grainPos) * 255 / 100;
    
    signal[0] = (grain[0] * envelope) >> 8;
    signal[1] = (grain[1] * envelope) >> 8;
    
    yield();
}
```

## Performance Considerations

### Batch Operations
```impala
// More efficient: read/write multiple frames at once
const int BATCH_SIZE = 32;

function process() {
    array inputBatch[BATCH_SIZE * 2];   // 32 stereo frames
    array outputBatch[BATCH_SIZE * 2];
    
    // Fill input batch
    int i;
    for (i = 0 to BATCH_SIZE) {
        inputBatch[i * 2] = signal[0];     // Would need to collect over time
        inputBatch[i * 2 + 1] = signal[1]; // This is simplified example
    }
    
    // Single write operation
    write(clock, BATCH_SIZE, inputBatch);
    
    // Single read operation  
    read(clock - 1000, BATCH_SIZE, outputBatch);
    
    // Process batch...
}
```

### Memory Access Patterns
```impala
// Efficient: sequential access
read(baseOffset, 10, buffer);        // Good: reads 10 consecutive frames

// Less efficient: scattered access  
for (i = 0 to 10) {
    read(baseOffset + i * 100, 1, temp); // Bad: 10 separate read calls
}
```

### Buffer Size Planning
```impala
// Calculate buffer needs
const int SAMPLE_RATE = 48000;
const int MAX_DELAY_MS = 1000;        // 1 second max delay
const int MAX_DELAY_SAMPLES = SAMPLE_RATE * MAX_DELAY_MS / 1000;

// Always account for stereo
array workingBuffer[MAX_DELAY_SAMPLES * 2];
```

## Key Points

- **Always write**: Most effects should write input to memory each sample
- **Circular buffer**: Memory access automatically wraps - no bounds checking needed
- **Stereo interleaved**: Buffer format is [L, R, L, R...] for frames
- **Fixed point positions**: Mod patches use 16.4 fixed point for interpolation
- **Clipping essential**: Prevent overflow in feedback loops with proper limiting
- **Batch when possible**: Multiple frame operations are more efficient than single-frame loops
- **Plan memory usage**: Consider maximum delay times and buffer sizes in design