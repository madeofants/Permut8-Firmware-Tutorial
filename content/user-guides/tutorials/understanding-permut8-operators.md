# Understanding Permut8 Operators
*Master the core instruction system that powers all Permut8 effects*

## What This Is

This tutorial explains how Permut8's **operator system** actually works - the fundamental instruction architecture that manipulates read/write heads in the 128-kiloword delay memory to create all audio effects. Understanding this is essential for both using the original interface and building custom firmware.

## The Core Concept: Read/Write Head Manipulation

### **The Heart of Permut8**
- **128 kilowords of 12-bit delay memory** - The core audio buffer
- **Write position (red dot)** - Where incoming audio is stored
- **Read positions (green dots)** - Where audio is played back from (left/right channels)
- **Two instructions** - Process in order to manipulate read positions

### **How Effects Are Created**
All Permut8 effects come from **manipulating where and how audio is read** from the delay memory:
- **Delays**: Read from positions behind the write head
- **Pitch effects**: Read at different rates than writing
- **Modulation**: Constantly move read positions
- **Granular effects**: Jump read positions around
- **Bit manipulation**: Alter the read position data itself

## The Instruction System

### **Instruction Architecture**
```
Instruction 1: [OPERATOR] + [High Operand] + [Low Operand]
                    ↓
Instruction 2: [OPERATOR] + [High Operand] + [Low Operand]
                    ↓
            Final Read Positions
```

**Processing Order**: Instruction 1 executes first, Instruction 2 processes the result of Instruction 1.

### **Operand Format**
- **Each operand**: 8-bit value (00-FF hex) = 256 possible values
- **Combined operands**: Can create 16-bit values (0000-FFFF) for wider parameter ranges
- **Bit manipulation**: Individual bits control specific aspects of the operation

## Operator Reference Guide

### **AND - Sudden Jumps & Beat Repeating**
**Function**: Clears selected bits in read position data  
**Effect**: Creates sudden jumps and rhythmic patterns  

**Common Uses**:
- **Higher bits (leftmost)**: Beat-repeating effects in SYNC mode
- **Middle bits**: Granular "buffer underrun" effects  
- **Lower bits**: Aliasing/bit-crusher effects

**Example**: `AND` with operand `F0F0` clears lower 4 bits, creating 16-step quantized read positions

### **MUL - Pitch & Speed Control**
**Function**: Changes read rate relative to write rate  
**Effect**: Pitch shifting and speed changes  

**Operand Values**:
- `0200` = Double rate (1 octave up)
- `0100` = Normal rate (no change)  
- `0080` = Half rate (1 octave down)
- `0000` = Stop (freeze)
- `8100` = Reverse (leftmost bit = sign bit)

**Key Point**: No crossfading - creates clicks when read/write positions meet

### **OSC - Modulation & Flanging**
**Function**: Makes read position swing back and forth in triangular motion  
**Effect**: Vibrato, flanging, frequency modulation  

**Operand Structure**:
- **High operand**: Oscillation rate (exponential scale)
- **Low operand**: Magnitude/depth (exponential scale)
- **Leftmost bit**: Stereo effect (inverts right channel modulation)

**Special Case**: Rate `00` freezes oscillation = fixed delay

### **RND - Random Modulation & Chorus**
**Function**: Adds random sweeping motion to read position  
**Effect**: Chorus, random pitch modulation, noise effects  

**Operand Structure**:
- **High operand**: Rate (exponential scale)
- **Low operand**: Depth (exponential scale)  
- **Leftmost bit**: Stereo effect (separate left/right randomization)

**Behaviors**:
- **Moderate settings**: Chorus-style pitch modulation
- **Extreme settings**: White noise following input level
- **Rate 0**: Sample-and-hold style (jumps once per memory cycle)

### **OR - Forward Pushing Effects**
**Function**: Sets selected bits in read position data  
**Effect**: Pushes read position ahead of write position  

**Use Case**: Repeat the last section of a beat (read ahead of current input)

### **XOR - Complex Bit Manipulation**
**Function**: Inverts operand bits in read position  
**Effect**: Complex playback order changes  

**Operand Patterns**:
- **All bits 1 (FFFF)**: Read position moves backward
- **Higher bits cleared**: Reverse short slices
- **Only higher bits set**: Slices play forward but in reversed order
- **Lowest bits**: Ultra-nasty aliasing effects
- **Leftmost bit**: Stereo offset effect

### **MSK - Selective Masking (Instruction 2 Only)**
**Function**: Selectively masks out result of Instruction 1  
**Effect**: Rhythmic gating and delay patterns  

**Operand Structure**:
- **STEP MASK operand**: Each bit = 1/8 of memory cycle (eighth notes in SYNC mode)
- **SUBTRACT operand**: Delay offset (exponential scale like SUB)

**Usage**: Most useful in SYNC mode for rhythmic effects

### **SUB - Fixed Delays**
**Function**: Subtracts fixed amounts from read positions  
**Effect**: Traditional delay effects  

**Operand Values** (exponential scale):
- **Under 80**: Comb filter effects
- **Higher values**: Longer delays
- **In REV mode**: Delay lengths become inverted

**Example**: In SYNC mode with CLOCK FREQ 1/1, `F0F0` = 1/2 bar delay

### **NOP - No Operation**
**Function**: Does nothing  
**Effect**: Bypass (pass audio through unchanged)

## Building Effects with Operators

### **Simple Delay**
```
Instruction 1: SUB + [delay time operands]
Instruction 2: NOP (bypass)
Result: Clean delay effect
```

### **Pitch-Shifted Delay**
```
Instruction 1: SUB + [delay time operands]  
Instruction 2: MUL + [pitch ratio operands]
Result: Delay with pitch shift
```

### **Chorus Effect**
```
Instruction 1: RND + [moderate rate] + [small depth]
Instruction 2: SUB + [short delay operands]
Result: Chorused delay
```

### **Beat Repeater**
```
SYNC mode + AND + [rhythmic pattern bits]
Result: Rhythmic audio repeating
```

### **Complex Granular**
```
Instruction 1: AND + [jump pattern]
Instruction 2: RND + [chaos rate] + [position spread]
Result: Granular texture
```

## Relationship to Custom Firmware

### **Original vs Custom**
**Original Permut8**: Users set operators via presets, operands via switches  
**Custom Firmware**: Same parameter system, but direct code control

### **Parameter Mapping in Code**
```impala
// Original operator system:
int operator1 = (int)params[OPERATOR_1_PARAM_INDEX];     // Instruction 1 type
int op1_high = (int)params[OPERAND_1_HIGH_PARAM_INDEX];  // Instruction 1 high operand  
int op1_low = (int)params[OPERAND_1_LOW_PARAM_INDEX];    // Instruction 1 low operand

int operator2 = (int)params[OPERATOR_2_PARAM_INDEX];     // Instruction 2 type
int op2_high = (int)params[OPERAND_2_HIGH_PARAM_INDEX];  // Instruction 2 high operand
int op2_low = (int)params[OPERAND_2_LOW_PARAM_INDEX];    // Instruction 2 low operand

// Custom firmware can:
// 1. Override operand parameters as direct effect controls
// 2. Implement completely different algorithms
// 3. Mix original operator concepts with custom processing
```

### **Why This Matters for Custom Firmware**
Understanding the operator system helps you:
1. **Design better interfaces** - Know what parameters feel natural to users
2. **Create familiar effects** - Understand how classic effects are built
3. **Optimize performance** - Learn from the efficient bit manipulation techniques
4. **Bridge concepts** - Help users transition from original to custom firmware

## Key Insights

### **Everything is Memory Manipulation**
- **Delays**: Read behind write position
- **Pitch**: Read at different rates  
- **Modulation**: Move read positions continuously
- **Rhythmic**: Jump read positions in patterns
- **Granular**: Chaotic read position movement

### **Bit-Level Control**
- **Individual bits** control specific effect aspects
- **Higher bits**: Usually control broader/slower changes
- **Lower bits**: Usually control finer/faster changes  
- **Leftmost bit**: Often controls stereo behavior or sign

### **Exponential Scales**
Many operands use **exponential scaling** - small changes at low values, large changes at high values. This matches musical perception better than linear scaling.

### **Order Matters**
Instructions process in order - Instruction 2 operates on the result of Instruction 1. This allows complex effect chains.

## Next Steps

1. **Experiment with Original Interface** - Use switches to understand each operator
2. **Study Effect Combinations** - Try chaining different operators  
3. **Apply to Custom Firmware** - Use these concepts in your own algorithms
4. **Read Advanced Topics** - Explore SYNC modes, memory cycles, and timing

Understanding this operator foundation will make you a much more effective Permut8 firmware developer and user.

---

**💡 Remember**: Every Permut8 effect - from simple delays to complex granular textures - comes down to creatively manipulating where and how audio is read from the delay memory buffer. Master this concept, and you master Permut8.