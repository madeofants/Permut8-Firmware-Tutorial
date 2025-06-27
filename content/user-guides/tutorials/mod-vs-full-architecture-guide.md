# Mod vs Full Patch Architecture Decision Guide

**Choose the right firmware architecture for your project**

One of the most important decisions in Permut8 firmware development is choosing between **Mod patches** and **Full patches**. This choice affects everything from development complexity to performance characteristics. This guide will help you make the right architectural decision for your specific project.

## What You'll Learn

By the end of this guide, you'll understand:
- The fundamental differences between Mod and Full patches
- When to choose each architecture type
- Trade-offs and limitations of each approach
- How to implement each type correctly
- Migration strategies between architectures

**Prerequisites**: [Understanding Impala Language Fundamentals](understanding-impala-fundamentals.md)  
**Time Required**: 30-45 minutes  
**Difficulty**: Beginner to Intermediate

## Chapter 1: Understanding the Two Architectures

### Full Patches: Complete Audio Processing Chain

**Full patches** replace Permut8's entire audio processing chain with your custom code.

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2


global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

function process()
{
    loop {

        int inputLeft = global signal[0]
        int inputRight = global signal[1]
        

        int outputLeft = processMyEffect(inputLeft)
        int outputRight = processMyEffect(inputRight)
        

        global signal[0] = outputLeft
        global signal[1] = outputRight
        
        yield()
    }
}
```

**Key Characteristics**:
- **Complete control** over audio processing
- **Direct hardware access** to audio inputs/outputs
- **No Permut8 built-in effects** - you implement everything
- **Higher complexity** but maximum flexibility

### Mod Patches: Operator Replacement

**Mod patches** replace one or both of Permut8's built-in operators while keeping the rest of the processing chain intact.

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2


global array positions[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]


function operate1()
returns int processed
locals array inputSamples[2], array outputSamples[2]
{

    read(global positions[0], 1, inputSamples)
    

    outputSamples[0] = processMyOperator(inputSamples[0])
    outputSamples[1] = inputSamples[1]
    

    write(global positions[0], 1, outputSamples)
    
    return 1
}


function operate2()
returns int processed
{

    return 1
}
```

**Key Characteristics**:
- **Integrates with Permut8's chain** - delay, feedback, etc. still work
- **Memory-based I/O** instead of direct audio
- **Lower complexity** - focus on your specific operator
- **Limited scope** but easier development

## Chapter 2: Decision Matrix

### Choose Full Patch When:

#### ✅ **Complete Effect Replacement**
```impala

function process()
{
    loop {

        int wet = calculateReverb(global signal[0])
        int dry = global signal[0] * dryLevel / 1000
        global signal[0] = wet + dry
        yield()
    }
}
```

**Use Cases**:
- Reverbs, delays, and time-based effects
- Multi-band processors (EQ, compressor)
- Synthesizers and tone generators
- Complex routing and mixing
- Spectral processing (FFT-based effects)

#### ✅ **Performance-Critical Applications**
```impala

function process()
{
    loop {

        global signal[0] = fastProcessing(global signal[0])
        yield()
    }
}
```

#### ✅ **Hardware Integration Focus**
```impala

function process()
{
    loop {



        yield()
    }
}
```

### Choose Mod Patch When:

#### ✅ **Operator-Style Effects**
```impala

function operate1()
returns int processed
locals array samples[2], int crushed
{
    read(global positions[0], 1, samples)
    

    crushed = samples[0] & crushMask
    samples[0] = crushed
    
    write(global positions[0], 1, samples)
    return 1
}
```

**Use Cases**:
- Distortion and waveshaping
- Bit manipulation effects
- Simple filters and EQ
- Amplitude modulation
- Ring modulation

#### ✅ **Integration with Permut8 Features**
```impala

function operate1()
returns int processed
{





    return 1
}
```

#### ✅ **Rapid Prototyping**
```impala

function operate1()
returns int processed
locals array samples[2]
{
    read(global positions[0], 1, samples)
    samples[0] = experimentalProcess(samples[0])
    write(global positions[0], 1, samples)
    return 1
}
```

## Chapter 3: Detailed Comparison

### Development Complexity

| Aspect | Full Patch | Mod Patch |
|--------|------------|-----------|
| **Boilerplate Code** | Moderate | Minimal |
| **Audio I/O** | Direct `signal[]` access | Memory `read()`/`write()` |
| **Parameter Handling** | Manual mapping | Automatic integration |
| **LED Control** | Manual implementation | Automatic integration |
| **Clock/Timing** | Manual management | Automatic synchronization |
| **Error Handling** | Your responsibility | Permut8 handles framework |

### Performance Characteristics

| Aspect | Full Patch | Mod Patch |
|--------|------------|-----------|
| **Latency** | Lowest (direct audio) | Slightly higher (memory access) |
| **CPU Usage** | Your algorithm only | Your algorithm + framework |
| **Memory Access** | Direct signal arrays | Memory read/write operations |
| **Real-time Safety** | Your responsibility | Framework assistance |

### Feature Integration

| Feature | Full Patch | Mod Patch |
|---------|------------|-----------|
| **Delay Lines** | Manual implementation | Automatic integration |
| **Feedback** | Manual routing | Built-in feedback paths |
| **Parameter Smoothing** | Manual implementation | Framework handles |
| **Preset System** | Manual state management | Automatic state handling |
| **MIDI Integration** | Manual implementation | Framework integration |

## Chapter 4: Implementation Patterns

### Full Patch Implementation Pattern

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2


global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clock


global int effectState = 0
global array effectMemory[1024]


function init()
{
    global effectState = 0

}


function update()
{



}


function reset()
{
    global effectState = 0

}


function process()
locals int inputL, int inputR, int outputL, int outputR
{
    loop {

        inputL = global signal[0]
        inputR = global signal[1]
        

        outputL = processEffect(inputL, 0)
        outputR = processEffect(inputR, 1)
        

        global signal[0] = outputL
        global signal[1] = outputR
        
        yield()
    }
}


function processEffect(int input, int channel)
returns int output
{

    output = input
}
```

### Mod Patch Implementation Pattern

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2


global array positions[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]


global int operatorState = 0


function init()
{
    global operatorState = 0
}


function update()
{


}


function operate1()
returns int processed
locals array samples[2], int position
{

    position = global positions[0]
    

    read(position, 1, samples)
    

    samples[0] = processOperator(samples[0])
    samples[1] = processOperator(samples[1])
    

    write(position, 1, samples)
    
    return 1
}


function operate2()
returns int processed
{


    return 1
}


function processOperator(int input)
returns int output
{

    output = input
}
```

## Chapter 5: Migration Strategies

### From Mod Patch to Full Patch

When your Mod patch outgrows the operator model:

```impala

function operate1()
returns int processed
locals array samples[2]
{
    read(global positions[0], 1, samples)
    samples[0] = complexEffect(samples[0])
    write(global positions[0], 1, samples)
    return 1
}


function process()
{
    loop {

        global signal[0] = complexEffect(global signal[0])
        global signal[1] = complexEffect(global signal[1])
        yield()
    }
}
```

**Migration Checklist**:
- ✅ Change `global array positions[2]` to `global array signal[2]`
- ✅ Replace `operate1()` with `process()` + `loop` + `yield()`
- ✅ Replace `read()`/`write()` with direct `signal[]` access
- ✅ Implement parameter handling in `update()`
- ✅ Implement LED control manually
- ✅ Add initialization in `init()` if needed

### From Full Patch to Mod Patch

When you want to integrate with Permut8's features:

```impala

function process()
{
    loop {
        global signal[0] = simpleEffect(global signal[0])
        yield()
    }
}


function operate1()
returns int processed
locals array samples[2]
{
    read(global positions[0], 1, samples)
    samples[0] = simpleEffect(samples[0])
    write(global positions[0], 1, samples)
    return 1
}
```

**Migration Checklist**:
- ✅ Change `global array signal[2]` to `global array positions[2]`
- ✅ Replace `process()` with `operate1()` and/or `operate2()`
- ✅ Replace direct `signal[]` access with `read()`/`write()`
- ✅ Remove manual parameter handling (framework handles it)
- ✅ Remove manual LED control (framework handles it)
- ✅ Simplify to focus on core algorithm

## Chapter 6: Real-World Examples

### Example 1: Bitcrusher (Perfect for Mod Patch)

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array positions[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

global int bitDepth = 8
global int sampleRateReduction = 1

function update()
{

    global bitDepth = 1 + global params[OPERAND_1_HIGH_PARAM_INDEX] / 32
    global sampleRateReduction = 1 + global params[OPERAND_1_LOW_PARAM_INDEX] / 64
}

function operate1()
returns int processed
locals array samples[2], int crushedSample, int mask
{
    read(global positions[0], 1, samples)
    

    mask = 0xFFFF << (16 - global bitDepth)
    

    crushedSample = samples[0] & mask
    

    if ((global clock % global sampleRateReduction) == 0) {
        samples[0] = crushedSample
    }

    
    write(global positions[0], 1, samples)
    return 1
}
```

**Why Mod Patch?**:
- ✅ Simple operator-style processing
- ✅ Benefits from Permut8's delay/feedback
- ✅ Automatic parameter and LED integration
- ✅ Can be combined with other operators

### Example 2: Custom Reverb (Requires Full Patch)

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]


global array reverbBuffer[32768]
global int writePos = 0
global array tapDelays[8] = {100, 200, 400, 600, 1200, 1800, 2400, 3200}
global int reverbTime = 500
global int wetLevel = 128

function update()
{
    global reverbTime = global params[OPERAND_1_HIGH_PARAM_INDEX] * 4
    global wetLevel = global params[OPERAND_1_LOW_PARAM_INDEX]
}

function process()
locals int input, int wet, int dry, int output, int i, int tapSample, int readPos
{
    loop {
        input = global signal[0]
        

        global reverbBuffer[global writePos] = input
        

        wet = 0
        for (i = 0 to 7) {
            readPos = global writePos - global tapDelays[i]
            if (readPos < 0) readPos = readPos + 32768
            
            tapSample = global reverbBuffer[readPos]
            wet = wet + tapSample / 8
        }
        

        wet = wet * global reverbTime / 1000
        

        dry = input * (255 - global wetLevel) / 255
        wet = wet * global wetLevel / 255
        output = dry + wet
        
        global signal[0] = output
        global signal[1] = output
        

        global writePos = (global writePos + 1) % 32768
        
        yield()
    }
}
```

**Why Full Patch?**:
- ✅ Complex buffer management needs total control
- ✅ Multi-tap delay requires custom memory allocation
- ✅ Timing-critical for reverb algorithm
- ✅ Custom wet/dry mixing

## Chapter 7: Performance Considerations

### CPU Usage Comparison

```impala

function operate1()
returns int processed
{
    read(position, 1, samples)
    samples[0] = process(samples[0])
    write(position, 1, samples)
    return 1
}


function process()
{
    loop {
        global signal[0] = process(global signal[0])
        yield()
    }
}
```

**Performance Guidelines**:
- **Full patches**: 5-10% lower CPU usage for simple algorithms
- **Mod patches**: Easier to optimize due to framework assistance
- **Complex algorithms**: Performance difference becomes negligible
- **Memory access**: Mod patches have slight overhead

### Memory Usage Patterns

```impala

global array positions[2]



global array signal[2]
global array delayBuffer[44100]
global array workingMemory[1024]

```

## Chapter 8: Testing and Debugging

### Testing Mod Patches

```impala

function operate1()
returns int processed
locals array samples[2]
{
    read(global positions[0], 1, samples)
    

    if ((global clock % 1000) == 0) {
        trace("Input: " + intToString(samples[0]))
    }
    
    samples[0] = processOperator(samples[0])
    

    if ((global clock % 1000) == 0) {
        trace("Output: " + intToString(samples[0]))
    }
    
    write(global positions[0], 1, samples)
    return 1
}
```

### Testing Full Patches

```impala

function process()
locals int input, int output
{
    loop {
        input = global signal[0]
        

        if ((global clock % 1000) == 0) {
            trace("Level: " + intToString(abs(input)))
        }
        
        output = processEffect(input)
        

        if (output > 2047) output = 2047
        if (output < -2047) output = -2047
        
        global signal[0] = output
        global signal[1] = output
        
        yield()
    }
}
```

## Chapter 9: Common Pitfalls and Solutions

### Pitfall 1: Wrong Architecture Choice

**Problem**: Chose Mod patch for complex reverb
```impala

function operate1()
returns int processed
{


    return 1
}
```

**Solution**: Use Full patch for complex effects
```impala

function process()
{
    loop {

        yield()
    }
}
```

### Pitfall 2: Inefficient Memory Access

**Problem**: Unnecessary memory operations in Mod patch
```impala

function operate1()
returns int processed
{
    read(global positions[0], 1, samples1)
    read(global positions[0], 1, samples2)

    write(global positions[0], 1, result1)
    write(global positions[0], 1, result2)
    return 1
}
```

**Solution**: Minimize memory operations
```impala

function operate1()
returns int processed
{
    read(global positions[0], 1, samples)

    write(global positions[0], 1, samples)
    return 1
}
```

### Pitfall 3: Not Returning from Operators

**Problem**: Forgetting to return from operator functions
```impala

function operate1()
{
    read(global positions[0], 1, samples)

    write(global positions[0], 1, samples)

}
```

**Solution**: Always return 1 for processed audio
```impala

function operate1()
returns int processed
{
    read(global positions[0], 1, samples)

    write(global positions[0], 1, samples)
    return 1
}
```

## Chapter 10: Decision Flowchart

Use this flowchart to choose your architecture:

```
START: What type of effect are you building?

├─ Simple operator-style effect (distortion, filter, etc.)
│  ├─ Want integration with Permut8 features? → MOD PATCH
│  └─ Need maximum performance? → FULL PATCH
│
├─ Complex time-based effect (reverb, delay, etc.)
│  └─ → FULL PATCH
│
├─ Multi-band or spectral processing
│  └─ → FULL PATCH
│
├─ Synthesizer or tone generator
│  └─ → FULL PATCH
│
├─ Learning/prototyping
│  └─ → MOD PATCH (easier to start)
│
└─ Production/commercial use
   ├─ Simple effect → MOD PATCH
   └─ Complex effect → FULL PATCH
```

## Summary and Next Steps

### Quick Decision Reference

**Choose Mod Patch for**:
- Simple effects (distortion, basic filters)
- Rapid prototyping
- Integration with Permut8 features
- Learning firmware development

**Choose Full Patch for**:
- Complex effects (reverb, delay, spectral)
- Maximum performance requirements
- Complete control over audio path
- Synthesizers and generators

### Next Steps

1. **Practice Implementation**: [Complete Development Workflow Tutorial](complete-development-workflow.md)
   - Learn the end-to-end development process
   - Practice compiling and testing both architectures

2. **Study Examples**: Explore cookbook recipes
   - **Mod Patch Examples**: [Bitcrusher](../cookbook/audio-effects/bitcrusher.md), [Basic Filter](../cookbook/fundamentals/basic-filter.md)
   - **Full Patch Examples**: [Make a Delay](../cookbook/audio-effects/make-a-delay.md), [Reverb](../cookbook/audio-effects/reverb-simple.md)

3. **Advanced Techniques**: [Assembly Integration Guide](../../assembly/gazl-assembly-introduction.md)
   - Learn optimization techniques for both architectures

### Architecture Decision Template

```
Project: _______________
Effect Type: ___________
Complexity: ____________
Performance Requirements: _______
Integration Needs: _____________

Decision: [ ] Mod Patch  [ ] Full Patch
Reasoning: ________________________
```

---

You now have the knowledge to make informed architectural decisions for your Permut8 firmware projects. This foundational understanding will guide every aspect of your development process.

*Part of the Permut8 Foundation Tutorial Series*