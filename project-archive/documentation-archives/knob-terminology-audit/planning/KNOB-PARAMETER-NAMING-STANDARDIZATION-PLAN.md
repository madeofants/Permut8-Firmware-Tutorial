# Knob and Parameter Naming Standardization Plan

**Date**: June 16, 2025  
**Objective**: Create consistent, clear naming conventions that distinguish between operator knobs, operand controls, and custom firmware overrides  
**Priority**: Critical - Foundation for all user-facing documentation  

## 🎯 Problem Analysis

### **Current Confusion**
1. **Mixing operator and operand controls**: Documentation calls operand controls "knobs" when they're actually LED displays + switches
2. **Inconsistent terminology**: "Knob 1", "Operator Knob 1" used for different things
3. **Missing distinction**: No clear separation between operation selection vs parameter setting
4. **Custom firmware confusion**: Unclear how custom firmware transforms the interface

## 📋 Actual Permut8 Interface Architecture

### **Physical Controls (Original System)**

#### **A. Operation Selection**
- **Operator Knob 1** (`params[2]`) - Selects Instruction 1 operation type (AND, MUL, OSC, RND)
- **Operator Knob 2** (`params[5]`) - Selects Instruction 2 operation type (OR, XOR, MSK, SUB, NOP)

#### **B. Parameter Setting**  
- **Instruction 1 High Operand** (`params[3]`) - Set via LED display + switches
- **Instruction 1 Low Operand** (`params[4]`) - Set via LED display + switches
- **Instruction 2 High Operand** (`params[6]`) - Set via LED display + switches
- **Instruction 2 Low Operand** (`params[7]`) - Set via LED display + switches

#### **C. System Controls**
- **Clock Frequency Knob** (`params[0]`) - Tempo sync timing
- **Mode Switches** (`params[1]`) - SYNC, REV, Triplet, Dotted, Write Protect

## 🏗️ Standardized Naming Convention

### **A. Original Operator System References**

#### **For Operation Selection**
✅ **"Operator Knob 1"** - Physical knob that selects Instruction 1 operation  
✅ **"Operator Knob 2"** - Physical knob that selects Instruction 2 operation  

#### **For Parameter Setting**
✅ **"Instruction 1 High Operand"** - Parameter set via LED display/switches  
✅ **"Instruction 1 Low Operand"** - Parameter set via LED display/switches  
✅ **"Instruction 2 High Operand"** - Parameter set via LED display/switches  
✅ **"Instruction 2 Low Operand"** - Parameter set via LED display/switches  

#### **For System Controls**
✅ **"Clock Frequency Knob"** - The dedicated timing knob  
✅ **"Mode Switches"** - The 5 system switches (SYNC, REV, etc.)  

### **B. Custom Firmware Override References**

#### **When Custom Firmware Takes Control**
✅ **"Control 1"** - Custom meaning for `params[3]` (was Instruction 1 High Operand)  
✅ **"Control 2"** - Custom meaning for `params[4]` (was Instruction 1 Low Operand)  
✅ **"Control 3"** - Custom meaning for `params[6]` (was Instruction 2 High Operand)  
✅ **"Control 4"** - Custom meaning for `params[7]` (was Instruction 2 Low Operand)  

#### **Parameters Usually Ignored in Custom Firmware**
- **Operator Knob 1** (`params[2]`) - Often ignored, set to NOP in presets
- **Operator Knob 2** (`params[5]`) - Often ignored, set to NOP in presets

### **C. Code Documentation Standard**

```impala
// Original Operator System
int operation1 = (int)params[2];    // Operator Knob 1: Instruction 1 operation type
int operand1H = (int)params[3];     // Instruction 1 High Operand (LED/switches)
int operand1L = (int)params[4];     // Instruction 1 Low Operand (LED/switches)
int operation2 = (int)params[5];    // Operator Knob 2: Instruction 2 operation type  
int operand2H = (int)params[6];     // Instruction 2 High Operand (LED/switches)
int operand2L = (int)params[7];     // Instruction 2 Low Operand (LED/switches)

// Custom Firmware Override
int delayTime = (int)params[3];     // Control 1: Delay time (was Instruction 1 High Operand)
int feedback = (int)params[4];      // Control 2: Feedback amount (was Instruction 1 Low Operand)
int wetMix = (int)params[6];        // Control 3: Dry/wet mix (was Instruction 2 High Operand)
int gain = (int)params[7];          // Control 4: Output gain (was Instruction 2 Low Operand)
// Note: params[2] and params[5] (Operator Knobs) typically ignored
```

## 📊 Documentation Templates

### **Template 1: Original Operator System Description**

```markdown
## Original Operator System Controls

### Operation Selection
- **Operator Knob 1**: Select Instruction 1 operation (AND, MUL, OSC, RND)
- **Operator Knob 2**: Select Instruction 2 operation (OR, XOR, MSK, SUB, NOP)

### Parameter Setting  
- **Instruction 1 High Operand**: Set via LED display and switches (0-255)
- **Instruction 1 Low Operand**: Set via LED display and switches (0-255)
- **Instruction 2 High Operand**: Set via LED display and switches (0-255)
- **Instruction 2 Low Operand**: Set via LED display and switches (0-255)

### System Controls
- **Clock Frequency Knob**: Tempo sync timing
- **Mode Switches**: SYNC, REV, Triplet, Dotted, Write Protect
```

### **Template 2: Custom Firmware Override Description**

```markdown
## Custom Firmware Controls

This custom firmware transforms the operand controls into direct effect parameters:

### Direct Effect Controls
- **Control 1**: [Custom effect parameter] (overrides Instruction 1 High Operand)
- **Control 2**: [Custom effect parameter] (overrides Instruction 1 Low Operand)  
- **Control 3**: [Custom effect parameter] (overrides Instruction 2 High Operand)
- **Control 4**: [Custom effect parameter] (overrides Instruction 2 Low Operand)

### Unchanged Controls
- **Clock Frequency Knob**: Still controls tempo sync timing
- **Mode Switches**: May have custom meanings or be ignored

### Operator Knobs
- **Operator Knob 1 & 2**: Typically ignored (set to NOP in presets)
```

### **Template 3: User Instructions**

```markdown
## Using This Effect

### Setting Parameters
1. **Adjust Control 1** (Instruction 1 High Operand position) for [effect parameter]
2. **Set Control 2** (Instruction 1 Low Operand position) for [effect parameter]
3. **Use Control 3** (Instruction 2 High Operand position) for [effect parameter]
4. **Turn Control 4** (Instruction 2 Low Operand position) for [effect parameter]

### System Settings
- **Clock Frequency Knob**: Set tempo sync rate
- **Mode Switches**: [Custom meanings or standard SYNC/REV functions]

### Note About Operator Knobs
The **Operator Knob 1** and **Operator Knob 2** settings are ignored by this custom firmware.
```

## 🚫 What NOT to Use (Avoid These Patterns)

### **Confusing/Incorrect Terms**
❌ **"Knob 1", "Knob 2", "Knob 3", "Knob 4"** - Ambiguous numbering  
❌ **"Operator Knob 1" for operand controls** - These are different things  
❌ **"Parameter knobs"** - Too vague  
❌ **"Top-left knob", "Bottom-right knob"** - Assumes physical layout knowledge  
❌ **"The delay knob"** - Not specific enough  

### **Technically Incorrect**
❌ **"Four operator knobs"** - There are only 2 operator knobs  
❌ **"Knob controls operand"** - Operands are set via LED displays + switches  
❌ **"Turn the operand"** - Operands aren't turned, they're set via interface  

## 📋 Implementation Strategy

### **Phase 1: Master Reference Creation**
1. **Update parameters_reference.md** with definitive naming standard
2. **Create visual diagram** showing operator knobs vs operand controls
3. **Document interface transformation** from original to custom firmware

### **Phase 2: Core Documentation Updates**
1. **QUICKSTART.md** - Apply correct terminology to introductory content
2. **Complete UI tutorials** - Fix all control references
3. **Interface tutorials** - Use proper distinction throughout

### **Phase 3: Systematic Documentation Audit**
1. **All cookbook recipes** - Update control descriptions
2. **All tutorials** - Fix knob/operand terminology  
3. **Reference docs** - Ensure technical accuracy
4. **Architecture guides** - Proper interface design patterns

### **Phase 4: Validation**
1. **Cross-reference check** - Ensure consistency
2. **Technical accuracy review** - Verify against actual interface
3. **User clarity test** - Confirm instructions are clear

## 🎯 Specific Correction Examples

### **QUICKSTART Fixes Needed**

#### **Current (Incorrect)**
```markdown
### Control Guide
- **Operator Knob 1 (Delay Time)**: Left = short delay, Right = long delay
- **Operator Knob 2 (Feedback)**: Left = single echo, Right = multiple repeats
```

#### **Corrected**
```markdown
### Control Guide  
- **Control 1 (Delay Time)**: Adjust Instruction 1 High Operand position for delay time
- **Control 2 (Feedback)**: Adjust Instruction 1 Low Operand position for feedback amount

### Note
This custom firmware transforms the operand controls (normally set via LED displays and switches) into direct effect controls. The **Operator Knob 1** and **Operator Knob 2** are not used.
```

### **Tutorial Fixes Needed**

#### **Current (Confusing)**
```markdown
Turn Knob 3 to adjust the filter cutoff frequency
```

#### **Corrected**
```markdown
Adjust **Control 3** (Instruction 2 High Operand position) to change the filter cutoff frequency
```

## ✅ Success Criteria

### **Clear Distinctions**
- **Operation vs Parameter**: Clear difference between selecting operations and setting parameters
- **Original vs Custom**: Clear transformation explanation when custom firmware overrides
- **Physical vs Logical**: Accurate description of actual interface elements

### **Consistent Terminology**
- **Operator Knobs**: Always refers to the 2 operation selection knobs
- **Controls 1-4**: Always refers to custom firmware parameter overrides
- **Operand positions**: Clear reference to LED display/switch interface

### **User Understanding**
- **No ambiguity** about which control to use
- **Clear context** for original vs custom firmware behavior
- **Accurate instructions** that match the actual interface

This standardization will eliminate the confusion between operator knobs (for operation selection) and operand controls (for parameter setting), while clearly explaining how custom firmware transforms the interface.