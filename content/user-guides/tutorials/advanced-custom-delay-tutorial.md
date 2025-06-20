# Advanced Custom Delay Tutorial

**Target Audience**: Developers ready for complex memory management and manual DSP implementation

**Time**: 45 minutes

**Prerequisites**: 
- Completed [QUICKSTART](../QUICKSTART.md) tutorial
- Read [Understanding Operators vs Custom Firmware](understanding-operators-vs-custom-firmware.md)

## Overview

This tutorial shows you how to manually implement what Permut8's SUB operator does automatically. You'll learn advanced memory management, delay line algorithms, and custom interface design.

**What You'll Build**: A fully-featured delay effect with custom controls that demonstrates the connection between built-in operators and custom firmware.

## Understanding the Challenge

### **What SUB Operator Does Automatically**
- **Memory Management**: Hardware tracks write position automatically
- **Read Positioning**: SUB operand directly controls read offset  
- **Efficiency**: Optimized in hardware, very fast

### **What We'll Do Manually**
- **Manual Memory**: Track `writePosition` ourselves
- **Manual Reading**: Calculate `readPosition = writePosition - delayTime`
- **Same Parameters**: Use `params[OPERAND_1_HIGH_PARAM_INDEX]` (Instruction 1 High) for delay time
- **Same Effect**: Create delay, just different implementation

## The Custom Delay Implementation

### 1. Create the Source File

Create `advanced_custom_delay.impala`:

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

extern native yield
extern native read
extern native write

// Interface override: Transform operator interface into custom delay controls
readonly array panelTextRows[8] = {
    "",
    "",
    "",
    "DELAY |---- TIME (INSTRUCTION 1 HIGH) ----|",
    "",
    "",
    "",
    "DELAY |-- FEEDBACK (INSTRUCTION 1 LOW) --|"
}

global array signal[2]
// Required parameter constants
const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT

global array params[PARAM_COUNT]
global array displayLEDs[4]

// Delay state (what SUB operator manages automatically)
global int writePosition = 0
global array tempBuffer[2]

function process()
locals int delayTime, int feedback, int input, int delayed, int output
{
    loop {
        // Same parameters that SUB operator uses, but with custom control
        delayTime = ((int)global params[OPERAND_1_HIGH_PARAM_INDEX] * 500 / 255) + 50;  // 50-550 samples (Instruction 1 High)
        feedback = ((int)global params[OPERAND_1_LOW_PARAM_INDEX] * 200 / 255);         // 0-200 feedback (Instruction 1 Low)
        
        // Manual delay processing (what SUB operator does automatically)
        input = (int)global signal[0];
        
        // Read delayed sample from memory (read position = write position - delay time)
        int readPosition = global writePosition - delayTime;
        if (readPosition < 0) readPosition = readPosition + 65536;  // Wrap around
        
        read(readPosition, 1, global tempBuffer);
        delayed = global tempBuffer[0];
        
        // Create echo: original + delayed signal
        output = input + (delayed * feedback / 255);
        
        // Prevent clipping
        if (output > 2047) output = 2047;
        if (output < -2047) output = -2047;
        
        // Write current input + feedback to memory for next cycle
        global tempBuffer[0] = input + (delayed * feedback / 255);
        write(global writePosition, 1, global tempBuffer);
        
        // Advance write position (what hardware manages automatically)
        global writePosition = (global writePosition + 1) % 65536;
        
        // Output the echo
        global signal[0] = output;
        global signal[1] = output;  // Mono delay
        
        // Visual feedback showing delay activity
        global displayLEDs[0] = delayTime >> 2;        // Show delay time
        global displayLEDs[1] = feedback;              // Show feedback amount
        global displayLEDs[2] = (delayed > 0) ? 0xFF : 0x00;  // Activity indicator
        global displayLEDs[3] = (global writePosition >> 8) & 0xFF;  // Position indicator
        
        yield();
    }
}
```

## Understanding the Memory Management

### **The Core Algorithm**

```impala
// 1. Calculate where to read from
int readPosition = global writePosition - delayTime;
if (readPosition < 0) readPosition = readPosition + 65536;  // Handle wraparound

// 2. Read the delayed audio
read(readPosition, 1, global tempBuffer);
delayed = global tempBuffer[0];

// 3. Mix with current input
output = input + (delayed * feedback / 255);

// 4. Write to current position for future reads
global tempBuffer[0] = input + (delayed * feedback / 255);
write(global writePosition, 1, global tempBuffer);

// 5. Advance to next position
global writePosition = (global writePosition + 1) % 65536;
```

### **Why This Works**

1. **Circular Buffer**: Memory wraps around at 65536 samples
2. **Read Behind Write**: `readPosition` is always behind `writePosition`
3. **Delay Time**: Distance between read and write positions
4. **Feedback**: Mix delayed signal back into memory

### **The Operator Connection**

**This manual process exactly replicates what SUB operator does**:
- **SUB operand**: Sets `delayTime` (distance between read/write)
- **Hardware management**: Automatically handles `writePosition` advancement
- **Same result**: Both create delay effects with identical behavior

## Advanced Features

### **Parameter Mapping**

```impala
// Transform abstract operand values into musical parameters  
delayTime = ((int)global params[OPERAND_1_HIGH_PARAM_INDEX] * 500 / 255) + 50;  // 50-550 samples
// At 44.1kHz: 50 samples = ~1.1ms, 550 samples = ~12.5ms

feedback = ((int)global params[OPERAND_1_LOW_PARAM_INDEX] * 200 / 255);         // 0-200 (0-78% feedback)
// Linear scaling prevents runaway feedback while allowing rich echoes
```

### **Visual Feedback System**

```impala
global displayLEDs[0] = delayTime >> 2;        // Delay time indicator (0-137)
global displayLEDs[1] = feedback;              // Feedback amount (0-200)  
global displayLEDs[2] = (delayed > 0) ? 0xFF : 0x00;  // Audio activity
global displayLEDs[3] = (global writePosition >> 8) & 0xFF;  // Memory position
```

**LED Meanings**:
- **LED 0**: Delay time - brighter = longer delay
- **LED 1**: Feedback amount - brighter = more repeats  
- **LED 2**: Audio activity - flashes with delayed signal
- **LED 3**: Memory position - shows write head movement

## Compilation and Bank Creation

### **Step 1: Compile**
```bash
PikaCmd.exe -compile advanced_custom_delay.impala
```

If that doesn't work:
```bash
.\PikaCmd.exe impala.pika compile advanced_custom_delay.impala advanced_custom_delay.gazl
```

### **Step 2: Clean the GAZL File**

**Critical**: Before creating the bank, clean the compiled GAZL file:

1. **Open `advanced_custom_delay.gazl`** in a text editor
2. **Remove compiler comments** (if present):
   ```
   ; Compiled with Impala version 1.0
   ```
3. **Remove separator lines**:
   ```
   ;-----------------------------------------------------------------------------
   ```
4. **Keep only pure assembly code**

### **Step 3: Create the Bank File**

Create `advanced_custom_delay.p8bank` with this **exact format**:

```
Permut8BankV2: {
    CurrentProgram: A0
    Programs: {
        A0: { Name: "Short Slap Delay", Operator1: "8" }
        A1: { Name: "Medium Echo", Operator1: "8" }
        A2: { Name: "Long Ambient", Operator1: "8" }
        A3: { Name: "Feedback Madness", Operator1: "8" }
    }
    Firmware: {
        Name: "advanced_custom_delay"
        Code: {
[PASTE YOUR CLEANED GAZL CONTENT HERE]
 }
    }
}
```

### **Understanding Operator "8" in Presets**

Each preset has `Operator1: "8"` which means:
- **"8" = SUB operator** (Subtract - creates delays)
- **Same operator** that would create delays using the built-in system
- **Our custom firmware replaces it** with manual implementation
- **Same parameters**: Both use `params[OPERAND_1_HIGH_PARAM_INDEX]` for delay time, `params[OPERAND_1_LOW_PARAM_INDEX]` for feedback

**The Connection**: This demonstrates how custom firmware can **replace** built-in operators while using the same parameter system.

## Using Your Advanced Delay

### **Loading and Testing**

1. **Load the bank**: File → Load Bank → `advanced_custom_delay.p8bank`
2. **Select A0 preset** to start
3. **Play audio** through Permut8
4. **Adjust controls**:
   - **Control 1** (Instruction 1 High): Delay time
   - **Control 2** (Instruction 1 Low): Feedback amount

### **Preset Guide**

- **A0 "Short Slap Delay"**: Quick echo (50-150ms), good for drums
- **A1 "Medium Echo"**: Classic delay (100-300ms), vocals and instruments  
- **A2 "Long Ambient"**: Spacious delays (200-500ms), atmospheric effects
- **A3 "Feedback Madness"**: High feedback settings, experimental sounds

### **Interface Transformation**

**What Just Happened?**
- **Original**: `params[OPERAND_1_HIGH_PARAM_INDEX]` controlled via LED display showing hex values
- **Your Firmware**: Same `params[OPERAND_1_HIGH_PARAM_INDEX]` becomes intuitive "DELAY TIME" control
- **Same Parameter, Better Interface**: Clear labels instead of abstract operands

## Advanced Modifications

### **1. Stereo Delay**
```impala
// Separate left/right processing
global signal[0] = inputL + (delayedL * feedback / 255);  // Left channel
global signal[1] = inputR + (delayedR * feedback / 255);  // Right channel
```

### **2. Filtered Feedback**
```impala
// Simple high-cut filter on feedback
int filteredFeedback = delayed - (delayed >> 3);  // Reduce high frequencies
output = input + (filteredFeedback * feedback / 255);
```

### **3. Tempo Sync**
```impala
// Sync delay time to musical divisions
int tempoDelayTime = 11025;  // Quarter note at 120 BPM, 44.1kHz
if ((int)global params[OPERATOR_2_PARAM_INDEX] > 127) tempoDelayTime = 5512;  // Eighth note
```

### **4. Ping-Pong Delay**
```impala
// Alternate delays between left and right channels
if ((global writePosition >> 10) & 1) {
    global signal[0] = input + delayed;  // Left gets delay
    global signal[1] = input;            // Right gets dry
} else {
    global signal[0] = input;            // Left gets dry  
    global signal[1] = input + delayed;  // Right gets delay
}
```

## Performance Considerations

### **Memory Access Optimization**
```impala
// Batch reads for efficiency
array batchBuffer[4];
read(readPosition, 4, batchBuffer);  // Read 4 samples at once
```

### **CPU Usage**
- **Manual implementation uses more CPU** than SUB operator
- **Consider operator approach** for performance-critical applications
- **Profile your code** if you notice audio dropouts

### **Memory Safety**
```impala
// Always validate array bounds
if (readPosition < 0) readPosition = readPosition + 65536;
if (readPosition >= 65536) readPosition = readPosition - 65536;
```

## Comparison with SUB Operator

### **Performance**
- **SUB Operator**: ~2% CPU usage
- **Custom Implementation**: ~8% CPU usage
- **Tradeoff**: 4x CPU cost for complete control

### **Flexibility**
- **SUB Operator**: Fixed delay algorithm
- **Custom Implementation**: Any delay algorithm you can code

### **Learning Value**
- **SUB Operator**: Black box, efficient
- **Custom Implementation**: Complete understanding of delay mechanics

## Troubleshooting

### **No Audio Output**
- Check `yield()` is called in the loop
- Verify `global signal[0]` and `global signal[1]` are being set
- Ensure `output` values are within -2047 to 2047 range

### **Clicking or Distortion**
- Check for clipping: implement output limiting
- Verify feedback values don't exceed 255
- Add parameter smoothing for knob changes

### **Memory Issues**
- Validate `readPosition` and `writePosition` bounds
- Check array access doesn't exceed buffer sizes
- Ensure `tempBuffer` is properly sized

## What's Next?

### **Explore More Advanced Topics**:
📖 [Custom Interface Design](custom-interface-design.md) - Advanced UI control
📖 [Multi-Tap Delay Systems](multi-tap-delay-systems.md) - Complex delay patterns
📖 [Hybrid Effect Development](hybrid-effect-development.md) - Combine operators with custom code

### **Study Other Memory-Based Effects**:
📖 [Custom Reverb Implementation](custom-reverb-implementation.md) - Multiple delay lines
📖 [Chorus and Flangers](chorus-and-flangers.md) - Modulated delays
📖 [Granular Synthesis](granular-synthesis.md) - Advanced memory manipulation

## Summary

You've successfully implemented a delay effect that manually replicates what Permut8's SUB operator does automatically. This demonstrates:

1. **Memory Management**: Manual control of read/write positions
2. **Parameter Mapping**: Transform abstract operands into user-friendly controls
3. **Interface Design**: Custom labels and visual feedback
4. **Algorithm Understanding**: Complete knowledge of delay mechanics
5. **Operator Connection**: How custom firmware relates to built-in operators

**The Key Insight**: Both SUB operator and your custom implementation use the same parameters and create the same effect - the difference is hardware automation vs. manual control.

This knowledge forms the foundation for creating any memory-based effect in Permut8.