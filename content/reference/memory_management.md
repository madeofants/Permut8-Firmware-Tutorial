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
    array delayedSamples[2];
    

    read(clock - 1000, 1, delayedSamples);
    
    int delayedLeft = delayedSamples[0];
    int delayedRight = delayedSamples[1];
    

    signal[0] = (signal[0] + delayedLeft) >> 1;
    signal[1] = (signal[1] + delayedRight) >> 1;
    
    yield();
}
```

### Reading Multiple Frames
```impala
function process() {
    array buffer[8];
    

    read(clock - 2000, 4, buffer);
    

    int sum = 0;
    int i;
    for (i = 0 to 4) {
        sum = sum + buffer[i * 2];
        sum = sum + buffer[i * 2 + 1];
    }
    

    signal[0] = (signal[0] + (sum >> 3)) >> 1;
    signal[1] = signal[0];
    
    yield();
}
```

### Reading with Variable Delay
```impala
global int delayTime = 1000;

function update() {

    int knobValue = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    delayTime = 100 + (knobValue * 38);
    

    displayLEDs[0] = knobValue;
}

function process() {
    array delayed[2];
    
    read(clock - delayTime, 1, delayed);
    

    signal[0] = (signal[0] + delayed[0]) >> 1;
    signal[1] = (signal[1] + delayed[1]) >> 1;
    
    yield();
}
```

## Basic Write Operations

### Writing Current Input
```impala
function process() {

    array currentFrame[2] = {signal[0], signal[1]};
    write(clock, 1, currentFrame);
    

    array delayed[2];
    read(clock - 5000, 1, delayed);
    

    signal[0] = delayed[0];
    signal[1] = delayed[1];
    
    yield();
}
```

### Selective Writing (Write Protection)
```impala
function process() {
    array input[2] = {signal[0], signal[1]};
    

    if (((int)params[SWITCHES_PARAM_INDEX] & SWITCHES_WRITE_PROTECT_MASK) == 0) {
        write(clock, 1, input);
    }
    

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

    array previous[2];
    read(clock - 1, 1, previous);
    

    int processedLeft = signal[0] + (previous[0] >> 2);
    int processedRight = signal[1] + (previous[1] >> 2);
    

    if (processedLeft > 2047) processedLeft = 2047;
    if (processedLeft < -2047) processedLeft = -2047;
    if (processedRight > 2047) processedRight = 2047;
    if (processedRight < -2047) processedRight = -2047;
    

    array toWrite[2] = {processedLeft, processedRight};
    write(clock, 1, toWrite);
    

    signal[0] = processedLeft;
    signal[1] = processedRight;
    
    yield();
}
```

## Position Array (Mod Patches)

### Understanding Positions
For mod patches, the `positions[]` array contains memory read positions instead of audio samples.

```impala
global array positions[2]
```

**Position format:** 20-bit fixed point (16.4)
- **Integer part**: Memory offset (16 bits)
- **Fractional part**: For interpolation (4 bits)
- **Range**: 0x00000 to 0xFFFFF

### Basic Position Processing
```impala
function operate1() 
returns int processed {

    int delayAmount = 1000 << 4;
    
    positions[0] = positions[0] + delayAmount;
    positions[1] = positions[1] + delayAmount;
    
    processed = 1;
}
```

### Parameter-Controlled Position Offset
```impala
global int positionOffset = 0;

function update() {

    int knobValue = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    positionOffset = (knobValue * 100) << 4;
    

    displayLEDs[0] = knobValue;
}

function operate1()
returns int processed {

    positions[0] = positions[0] + positionOffset;
    positions[1] = positions[1] + positionOffset;
    
    processed = 1;
}
```

### Stereo Position Effects
```impala
function operate1()
returns int processed {

    int leftDelay = ((int)params[OPERAND_1_HIGH_PARAM_INDEX] * 50) << 4;
    int rightDelay = ((int)params[OPERAND_1_LOW_PARAM_INDEX] * 50) << 4;
    
    positions[0] = positions[0] + leftDelay;
    positions[1] = positions[1] + rightDelay;
    

    displayLEDs[0] = leftDelay >> 8;
    displayLEDs[1] = rightDelay >> 8;
    
    processed = 1;
}
```

### Position Interpolation
```impala
function operate1()
returns int processed {

    int targetOffset = ((int)params[OPERAND_1_HIGH_PARAM_INDEX] * 100) << 4;
    

    int currentLeft = positions[0] & 0xF;
    int currentRight = positions[1] & 0xF;
    

    positions[0] = (positions[0] & 0xFFFF0) | ((currentLeft + 1) & 0xF);
    positions[1] = (positions[1] & 0xFFFF0) | ((currentRight + 1) & 0xF);
    

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
    

    write(clock, 1, input);
    

    read(clock - 1000, 1, tap1);
    read(clock - 2500, 1, tap2);
    read(clock - 4000, 1, tap3);
    

    int leftMix = (tap1[0] + tap2[0] + tap3[0]) / 3;
    int rightMix = (tap1[1] + tap2[1] + tap3[1]) / 3;
    

    signal[0] = (signal[0] + leftMix) >> 1;
    signal[1] = (signal[1] + rightMix) >> 1;
    
    yield();
}
```

### Feedback Loop with Processing
```impala
global float feedbackGain = 0.5;

function update() {

    int knobValue = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    feedbackGain = itof(knobValue) * 0.9 / 255.0;
}

function process() {
    array input[2] = {signal[0], signal[1]};
    array feedback[2];
    

    read(clock - 2000, 1, feedback);
    

    int fbLeft = ftoi(itof(feedback[0]) * feedbackGain);
    int fbRight = ftoi(itof(feedback[1]) * feedbackGain);
    
    int processedLeft = input[0] + fbLeft;
    int processedRight = input[1] + fbRight;
    

    if (processedLeft > 2047) processedLeft = 2047;
    else if (processedLeft < -2047) processedLeft = -2047;
    if (processedRight > 2047) processedRight = 2047;
    else if (processedRight < -2047) processedRight = -2047;
    

    array toWrite[2] = {processedLeft, processedRight};
    write(clock, 1, toWrite);
    

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
    

    write(writePos, 1, input);
    

    int readPos = writePos - bufferSize;
    if (readPos < 0) readPos = readPos + bufferSize;
    
    read(readPos, 1, output);
    

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

    int knobValue = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    grainSize = 100 + (knobValue * 19);
}

function process() {
    array input[2] = {signal[0], signal[1]};
    array grain[2];
    

    write(clock, 1, input);
    

    read(clock - 5000 - grainPos, 1, grain);
    

    grainPos = grainPos + grainDir;
    

    if (grainPos >= grainSize || grainPos <= 0) {
        grainDir = -grainDir;
    }
    

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

const int BATCH_SIZE = 32;

function process() {
    array inputBatch[BATCH_SIZE * 2];
    array outputBatch[BATCH_SIZE * 2];
    

    int i;
    for (i = 0 to BATCH_SIZE) {
        inputBatch[i * 2] = signal[0];
        inputBatch[i * 2 + 1] = signal[1];
    }
    

    write(clock, BATCH_SIZE, inputBatch);
    

    read(clock - 1000, BATCH_SIZE, outputBatch);
    

}
```

### Memory Access Patterns
```impala

read(baseOffset, 10, buffer);


for (i = 0 to 10) {
    read(baseOffset + i * 100, 1, temp);
}
```

### Buffer Size Planning
```impala

const int SAMPLE_RATE = 48000;
const int MAX_DELAY_MS = 1000;
const int MAX_DELAY_SAMPLES = SAMPLE_RATE * MAX_DELAY_MS / 1000;


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