# Permut8 Interface Architecture Reference
**Date**: June 15, 2025  
**Purpose**: Complete technical reference for audit duration  

## Detailed Permut8 Interface Architecture

### **Original Permut8 Hardware Interface**

#### **Physical Controls**
1. **Clock Frequency Knob** - Single physical knob
2. **Bit Switch Banks** - Multiple physical switches (8 switches per operand)
3. **Scrollable LED Displays** - Show hex values, clickable/draggable
4. **Operator Selectors** - Choose operation type (AND, MUL, OSC, etc.)

#### **How Users Set Operand Values (Original)**
```
User wants operand value 0xB4 (180 decimal):

Method 1 - Bit Switches:
Switch 8: [ON ]  = 1  = 128
Switch 7: [OFF]  = 0  = 0  
Switch 6: [ON ]  = 1  = 32
Switch 5: [ON ]  = 1  = 16
Switch 4: [OFF]  = 0  = 0
Switch 3: [ON ]  = 1  = 4
Switch 2: [OFF]  = 0  = 0
Switch 1: [OFF]  = 0  = 0
                       ___
Total: 128+32+16+4 = 180 = 0xB4

Method 2 - LED Display:
User clicks/drags hex display showing "B4"
Or clicks up/down arrows to increment/decrement
```

### **Parameter Array Mapping in Code**

```impala
global array params[8] = {
    [0] CLOCK_FREQ_PARAM_INDEX,      // Clock knob position (0-255)
    [1] SWITCHES_PARAM_INDEX,        // Switch states bitmask
    [2] OPERATOR_1_PARAM_INDEX,      // Instruction 1 operation type (0-4)
    [3] OPERAND_1_HIGH_PARAM_INDEX,  // Instruction 1 High Operand (0-255)
    [4] OPERAND_1_LOW_PARAM_INDEX,   // Instruction 1 Low Operand (0-255)
    [5] OPERATOR_2_PARAM_INDEX,      // Instruction 2 operation type (0-4)
    [6] OPERAND_2_HIGH_PARAM_INDEX,  // Instruction 2 High Operand (0-255)
    [7] OPERAND_2_LOW_PARAM_INDEX    // Instruction 2 Low Operand (0-255)
};
```

### **LED Display System (4 Displays)**

```impala
global array displayLEDs[4] = {
    [0] // LED Display 1 - 8 segments, controlled by firmware
    [1] // LED Display 2 - 8 segments, controlled by firmware  
    [2] // LED Display 3 - 8 segments, controlled by firmware
    [3] // LED Display 4 - 8 segments, controlled by firmware
};

// Each display shows 8-bit pattern:
displayLEDs[0] = 0b10110100;  // Lights segments: ■□■■□■□□
```

### **Data Flow: UI → Code → LEDs**

#### **Original Permut8 Flow:**
```
1. User Action:
   - Flips bit switches OR drags hex display
   
2. Hardware Updates:
   - params[3] = new operand value (0-255)
   
3. Firmware Reads:
   int operand = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
   
4. Firmware Controls LEDs:
   displayLEDs[0] = operand;  // Show operand value on LED display
```

### **Custom Firmware Override System**

#### **Interface Transformation:**
```impala
// Original Interface Panel:
// [Switches: 10110100] [LED Display: B4] [Operation: MUL]

readonly array panelTextRows[8] = {
    "",
    "",  
    "",
    "EFFECT |------ BIT DEPTH CONTROL ------|",  // Line 3 = params[3]
    "",
    "",
    "",
    ""
};

// Becomes Custom Interface:
// [Knob: Bit Depth] [LED Display: "BIT DEPTH CONTROL"] [Hidden: MUL]
```

#### **Code Connection in Custom Firmware:**
```impala
function process() {
    // This line connects the UI element to the algorithm:
    bits = ((int) global params[3] >> 5) + 1;
    //              ↑
    //              This value comes from:
    //              - Original: User's switch/LED input (0-255)
    //              - Custom: Direct knob control (0-255)
    
    // Math conversion:
    // params[3] = 255 → 255 >> 5 = 7 → 7 + 1 = 8 bits
    // params[3] = 0   → 0 >> 5   = 0 → 0 + 1 = 1 bit
    
    // LED feedback shows the result:
    displayLEDs[0] = 1 << (bits - 1);  // Light LED to show bit depth
}
```

### **panelTextRows Layout System**

```impala
readonly array panelTextRows[8] = {
    "",                                           // Row 0
    "",                                           // Row 1  
    "",                                           // Row 2
    "INST1 |---- HIGH ----| |---- HIGH ----|",   // Row 3: params[3] & params[6]
    "",                                           // Row 4
    "",                                           // Row 5
    "",                                           // Row 6  
    "INST1 |---- LOW -----| |---- LOW -----|"    // Row 7: params[4] & params[7]
};

// Visual Layout:
//        LEFT SIDE          RIGHT SIDE
// Row 3: params[3]          params[6]     (Instruction High Operands)
// Row 7: params[4]          params[7]     (Instruction Low Operands)
```

### **Complete Data Flow Example (Bitcrusher)**

#### **1. User Interaction:**
```
Custom Firmware Interface:
┌─────────────────────────────────────┐
│ BIT |------ CRUSH AMOUNT ---------|  │ ← panelTextRows[3]
│                                     │
│ [●●●○○○○○] LED Display              │ ← displayLEDs[0] 
│                                     │
│ User turns knob → params[3] = 96    │
└─────────────────────────────────────┘
```

#### **2. Code Processing:**
```impala
function process() {
    // Read knob value (0-255)
    bits = ((int) global params[3] >> 5) + 1;
    // 96 >> 5 = 3, 3 + 1 = 4 bits
    
    // Create bit mask for 4-bit crushing
    shift = 12 - bits;          // 12 - 4 = 8
    mask = 0xFFF0 << shift;     // 0xFFF0 << 8 = 0xFF00
    
    // Apply to audio
    signal[0] = signal[0] & mask;  // Keep only top 4 bits
    
    // Update LED display  
    displayLEDs[0] = 1 << (bits - 1);  // 1 << 3 = 0b00001000 = 4th LED lit
}
```

#### **3. LED Visual Feedback:**
```
LED Display Pattern:
displayLEDs[0] = 0b00001000

Physical LEDs: [○][○][○][●][○][○][○][○]
Meaning: "4-bit crushing active"
```

### **Key Understanding Points**

1. **params[3-7] are data containers** - they hold 0-255 values regardless of source
2. **Original UI**: Values set by switches/hex displays 
3. **Custom firmware**: Values set by direct knob control
4. **panelTextRows**: Changes what user sees, not how code works
5. **displayLEDs**: Always controlled by firmware code for feedback
6. **Same parameter, different interface** - params[3] works identically whether from switches or knobs

### **Critical Documentation Principle**

The confusion in documentation comes from mixing the **interface description** (how users control it) with the **code reference** (how firmware reads it). They're the same data, accessed differently.

**Always distinguish:**
- **Original Interface**: "Instruction 1 High Operand (set via switches/LED display)"
- **Custom Firmware**: "Instruction 1 High Operand (overridden as knob control)"
- **Code Access**: "`params[3]` contains the operand value (0-255)"

---
**Reference Status**: Active for audit duration ✅