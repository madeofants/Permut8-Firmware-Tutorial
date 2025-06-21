# Complete UI Control with Delay
*Master all Permut8 interface elements using a comprehensive delay effect*

## What This Tutorial Teaches

This tutorial demonstrates how to use **every aspect** of Permut8's original interface system by building a delay effect that utilizes all UI elements:

- **All 8 parameters** (`params[PARAM_COUNT]`) - Clock frequency, switches, operators, and operands
- **All 4 LED displays** - Parameter feedback and activity indication
- **Both instructions** - Instruction 1 and Instruction 2 processing
- **All switch states** - SYNC, REV, triplet, dotted timing modes
- **Original operator interface** - Working with hex displays and bit switches

### **Approach: Operator Modification (Hybrid)**

This demonstrates **Approach 3: Operator Modification** - replacing built-in operators with custom code while maintaining the standard interface and parameter meanings.

**Why This Approach?**:
- **Maximum UI integration** - Uses every interface element as intended
- **Familiar interface** - Users get expected operator system behavior
- **Enhanced functionality** - Adds custom features while keeping standard controls
- **Learning foundation** - Shows how to work within the operator framework

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

extern native yield
extern native read
extern native write

// Audio and parameter constants
const int AUDIO_MAX = 2047
const int AUDIO_MIN = -2047
const int PARAM_MAX = 255
const int MEMORY_SIZE = 65536
const int STEREO_OFFSET = 32768
const int LED_MAX = 255

// Required parameter constants
const int OPERAND_1_HIGH_PARAM_INDEX = 0
const int OPERAND_1_LOW_PARAM_INDEX = 1
const int OPERAND_2_LOW_PARAM_INDEX = 2
const int OPERAND_2_HIGH_PARAM_INDEX = 3
const int OPERATOR_1_PARAM_INDEX = 4
const int OPERATOR_2_PARAM_INDEX = 5
const int SWITCHES_PARAM_INDEX = 6
const int CLOCK_FREQ_PARAM_INDEX = 7
const int PARAM_COUNT = 8

// Global variables that connect to Permut8 hardware
global array signal[2]          // Audio input/output
global array params[PARAM_COUNT]          // All hardware parameters
global array displayLEDs[4]     // All 4 LED displays
global array positions[2]       // Memory positions for operators
global clock
global clockFreqLimit

// Enhanced delay state
global masterClock = 0
global syncMode = 0
global reverseMode = 0
global tripletMode = 0
global dottedMode = 0
global writeProtectMode = 0

// Delay processing state
global array delayBuffer[2]
global int baseDelayTime = 1000
global int modulatedDelayTime = 1000
global int feedbackAmount = 100
global int crossFeedback = 50

// Operator 1: Enhanced SUB with modulation
function operate1() returns processed {
    locals clockFreq, switches, operator1Type, delayHigh, delayLow, combinedOperand, tempoFactor, currentPosition, readPosition, delayedSample
    
    // === PARAMETER READING (Using Original Interface) ===
    clockFreq = params[CLOCK_FREQ_PARAM_INDEX]           // Clock frequency knob
    switches = params[SWITCHES_PARAM_INDEX]            // Switch states bit mask
    operator1Type = params[OPERATOR_1_PARAM_INDEX]       // Should be SUB (8) for delay
    delayHigh = params[OPERAND_1_HIGH_PARAM_INDEX]          // Instruction 1 High Operand
    delayLow = params[OPERAND_1_LOW_PARAM_INDEX]           // Instruction 1 Low Operand
    
    // === SWITCH PROCESSING (All 5 Switch States) ===
    syncMode = (switches & 0x01) != 0;           // Bit 0: SYNC switch
    reverseMode = (switches & 0x02) != 0;        // Bit 1: REV switch  
    tripletMode = (switches & 0x04) != 0;        // Bit 2: Triplet timing
    dottedMode = (switches & 0x08) != 0;         // Bit 3: Dotted timing
    writeProtectMode = (switches & 0x10) != 0;   // Bit 4: Write protect
    
    // === CLOCK FREQUENCY PROCESSING ===
    masterClock = masterClock + 1;
    
    // Calculate base delay time from operands (16-bit value)
    combinedOperand = (delayHigh << 8) | delayLow  // 0-65535 range
    baseDelayTime = (combinedOperand >> 4) + 100;       // 100-4195 samples
    
    // === TIMING MODE PROCESSING ===
    if (syncMode) {
        // Tempo-synchronized delay based on clock frequency
        tempoFactor = (clockFreq >> 3) + 1  // 1-32 tempo divisions
        
        if (tripletMode) {
            // Triplet timing: 2/3 of normal timing
            baseDelayTime = (baseDelayTime * 2) / 3;
        }
        
        if (dottedMode) {
            // Dotted timing: 1.5x normal timing  
            baseDelayTime = (baseDelayTime * 3) / 2;
        }
        
        // Quantize to tempo
        baseDelayTime = (baseDelayTime / tempoFactor) * tempoFactor;
    }
    
    // === REVERSE MODE PROCESSING ===
    if (reverseMode) {
        // Read from future position for reverse delay effect
        modulatedDelayTime = -baseDelayTime;
    } else {
        modulatedDelayTime = baseDelayTime;
    }
    
    // === MEMORY OPERATION (Enhanced SUB behavior) ===
    currentPosition = positions[0]
    readPosition = currentPosition - modulatedDelayTime
    
    // Handle memory wrapping
    if (readPosition < 0) readPosition = readPosition + 65536;
    if (readPosition >= 65536) readPosition = readPosition - 65536;
    
    // Read delayed audio
    read(readPosition, 1, delayBuffer)
    delayedSample = delayBuffer[0]
    
    // Apply write protection
    if (!writeProtectMode) {
        // Normal operation: write input to memory
        delayBuffer[0] = signal[0];
        write(currentPosition, 1, delayBuffer);
    }
    // If write protect is on, memory is frozen
    
    // Store delayed sample for mixing
    signal[0] = delayedSample;
    
    return 1  // Signal successful processing
}

// Operator 2: Cross-channel and feedback processing
function operate2() returns processed {
    locals operator2Type, feedbackHigh, feedbackLow, currentPosition, readPosition, rightDelayed, leftInput, rightInput, leftDelayed, leftOutput, rightOutput
    
    // === PARAMETER READING (Instruction 2) ===
    operator2Type = params[OPERATOR_2_PARAM_INDEX]       // Instruction 2 operator type
    feedbackHigh = params[OPERAND_2_HIGH_PARAM_INDEX]        // Instruction 2 High Operand  
    feedbackLow = params[OPERAND_2_LOW_PARAM_INDEX]         // Instruction 2 Low Operand
    
    // Calculate feedback parameters
    feedbackAmount = (feedbackHigh * 3) / 4;     // 0-191 feedback (75% max)
    crossFeedback = feedbackLow / 4;             // 0-63 cross-channel feedback
    
    // === STEREO PROCESSING ===
    currentPosition = positions[1]
    readPosition = currentPosition - modulatedDelayTime
    
    // Handle wrapping for right channel
    if (readPosition < 0) readPosition = readPosition + 65536;
    if (readPosition >= 65536) readPosition = readPosition - 65536;
    
    // Read right channel delayed audio
    read(readPosition + 32768, 1, delayBuffer)  // Offset for stereo separation
    rightDelayed = delayBuffer[0]
    
    // === FEEDBACK PROCESSING ===
    leftInput = signal[0]
    rightInput = signal[1]
    leftDelayed = signal[0]  // From operate1
    
    // Apply feedback with cross-channel mixing
    leftOutput = leftInput + (leftDelayed * feedbackAmount / 255) + (rightDelayed * crossFeedback / 255)
    rightOutput = rightInput + (rightDelayed * feedbackAmount / 255) + (leftDelayed * crossFeedback / 255)
    
    // Prevent clipping
    if (leftOutput > 2047) leftOutput = 2047;
    if (leftOutput < -2047) leftOutput = -2047;
    if (rightOutput > 2047) rightOutput = 2047;
    if (rightOutput < -2047) rightOutput = -2047;
    
    // Write feedback to memory for next iteration
    if (!writeProtectMode) {
        delayBuffer[0] = leftOutput;
        write(currentPosition, 1, delayBuffer);
        
        delayBuffer[0] = rightOutput;
        write(currentPosition + 32768, 1, delayBuffer);
    }
    
    // Final output
    signal[0] = leftOutput;
    signal[1] = rightOutput;
    
    return 1
}

// Update function: Handle parameter changes and LED feedback
function update() {
    locals tempoDiv, switchDisplay, delayPattern, activityLevel, feedbackDisplay
    
    // === LED DISPLAY 1: Clock and Sync Status ===
    if (syncMode) {
        // Show tempo divisions when synced
        tempoDiv = (params[CLOCK_FREQ_PARAM_INDEX] >> 3) + 1
        displayLEDs[0] = (1 << (tempoDiv - 1)) & 0xFF  // Light LEDs for tempo
    } else {
        // Show clock frequency when not synced
        displayLEDs[0] = params[CLOCK_FREQ_PARAM_INDEX]
    }
    
    // === LED DISPLAY 2: Switch States ===
    switchDisplay = 0
    if (syncMode) switchDisplay |= 0x01        // LED 1: SYNC
    if (reverseMode) switchDisplay |= 0x02     // LED 2: REV
    if (tripletMode) switchDisplay |= 0x04     // LED 3: Triplet
    if (dottedMode) switchDisplay |= 0x08      // LED 4: Dotted
    if (writeProtectMode) switchDisplay |= 0x10 // LED 5: Write Protect
    displayLEDs[1] = switchDisplay
    
    // === LED DISPLAY 3: Delay Time Indication ===
    // Show delay time as LED pattern
    delayPattern = (baseDelayTime >> 8) & 0xFF  // Scale to 0-255
    displayLEDs[2] = delayPattern
    
    // === LED DISPLAY 4: Feedback and Activity ===
    // Combine feedback amount with audio activity
    activityLevel = (abs(signal[0]) + abs(signal[1])) >> 4  // Scale audio level
    feedbackDisplay = (feedbackAmount >> 1) | (activityLevel << 4)
    displayLEDs[3] = feedbackDisplay & 0xFF
}

// Main processing function
function process() {
    loop {
        operate1()  // Process Instruction 1 (delay with modulation)
        operate2()  // Process Instruction 2 (feedback and stereo)
        yield()
    }
}
```

## Understanding Every Interface Element

### **Parameter Usage (All 8 Parameters)**

| Parameter | Original Meaning | Our Enhancement |
|-----------|------------------|-----------------|
| `params[CLOCK_FREQ_PARAM_INDEX]` | Clock Frequency | Tempo sync and delay quantization |
| `params[SWITCHES_PARAM_INDEX]` | Switch States | All 5 switch modes processed |
| `params[OPERATOR_1_PARAM_INDEX]` | Operator 1 Type | Should be SUB (8) for delay |
| `params[OPERAND_1_HIGH_PARAM_INDEX]` | Instruction 1 High | Delay time high byte |
| `params[OPERAND_1_LOW_PARAM_INDEX]` | Instruction 1 Low | Delay time low byte |
| `params[OPERATOR_2_PARAM_INDEX]` | Operator 2 Type | Feedback processing type |
| `params[OPERAND_2_HIGH_PARAM_INDEX]` | Instruction 2 High | Feedback amount |
| `params[OPERAND_2_LOW_PARAM_INDEX]` | Instruction 2 Low | Cross-channel feedback |

### **Switch Processing (All 5 Switches)**

```impala
// How to decode switch states from params[SWITCHES_PARAM_INDEX]
switches = params[SWITCHES_PARAM_INDEX]
syncMode = (switches & 0x01) != 0       // Bit 0: SYNC switch
reverseMode = (switches & 0x02) != 0    // Bit 1: REV switch  
tripletMode = (switches & 0x04) != 0    // Bit 2: Triplet timing
dottedMode = (switches & 0x08) != 0     // Bit 3: Dotted timing
writeProtectMode = (switches & 0x10) != 0 // Bit 4: Write protect
```

**Switch Effects**:
- **SYNC**: Quantizes delay time to tempo based on clock frequency
- **REV**: Reverses delay direction (reads from future)
- **Triplet**: 2/3 timing ratio for triplet delays
- **Dotted**: 1.5x timing ratio for dotted delays  
- **Write Protect**: Freezes delay memory content

### **LED Display Usage (All 4 Displays)**

```impala
displayLEDs[0] = // Clock frequency or tempo divisions
displayLEDs[1] = // Switch states as bit pattern
displayLEDs[2] = // Delay time visualization  
displayLEDs[3] = // Feedback amount + audio activity
```

**LED Meanings**:
- **Display 1**: Shows tempo sync or raw clock frequency
- **Display 2**: Visual representation of all 5 switch states
- **Display 3**: Current delay time as LED pattern
- **Display 4**: Feedback level combined with audio activity

### **Operator Integration (Both Instructions)**

**Instruction 1 (operate1)**:
- Implements enhanced SUB operator behavior
- Processes delay time from high/low operands  
- Handles timing modes and sync
- Applies reverse mode and write protection

**Instruction 2 (operate2)**:
- Processes feedback and cross-channel effects
- Uses Instruction 2 operands for feedback control
- Manages stereo separation and mixing
- Applies final output limiting

## Using the Interface

### **Setting Up Delay Time**
1. **Set Operator 1 to SUB (8)** via preset or interface
2. **Adjust Instruction 1 operands** via switches/LED displays:
   - High operand: Coarse delay time
   - Low operand: Fine delay time
3. **Combined range**: 100-4195 samples delay time

### **Controlling Timing**
1. **Clock Frequency**: Sets base tempo for sync mode
2. **SYNC switch**: Enable/disable tempo synchronization
3. **Triplet switch**: Apply 2/3 timing ratio
4. **Dotted switch**: Apply 1.5x timing ratio

### **Setting Feedback**
1. **Set Operator 2** to desired feedback type
2. **Instruction 2 High**: Main feedback amount (0-191)
3. **Instruction 2 Low**: Cross-channel feedback (0-63)

### **Special Modes**
- **REV switch**: Reverse delay direction
- **Write Protect**: Freeze delay memory content
- **LED monitoring**: Watch all displays for real-time feedback

## Bank Configuration

```
Permut8BankV2: {
    CurrentProgram: A0
    Programs: {
        A0: { Name: "Basic Delay", Operator1: "8", Operator2: "0" }
        A1: { Name: "Sync Delay", Operator1: "8", Operator2: "0" }  
        A2: { Name: "Feedback Delay", Operator1: "8", Operator2: "4" }
        A3: { Name: "Stereo Delay", Operator1: "8", Operator2: "1" }
    }
    Firmware: {
        Name: "complete_ui_delay"
        Code: { [YOUR GAZL CODE] }
    }
}
```

## Key Learning Points

### **Complete Interface Mastery**
- **All 8 parameters** have specific roles and functions
- **Every switch** affects delay behavior meaningfully
- **All 4 LED displays** provide real-time parameter feedback
- **Both instructions** work together for complex effects

### **Operator System Integration**
- **Maintains standard interface** - users get expected behavior
- **Enhances built-in operators** - adds features while keeping compatibility
- **Uses original parameter meanings** - familiar to experienced users
- **Preserves preset system** - works with standard bank format

### **Real-World Application**
This tutorial shows how to:
- Build complex effects within the operator framework
- Utilize every aspect of Permut8's interface system
- Create professional-quality delays with full UI integration
- Maintain compatibility with existing Permut8 workflows

**Result**: A delay effect that feels like a built-in operator but with enhanced capabilities and complete interface integration.

---

*Next: [Custom Interface Tutorial](custom-interface-bypass-tutorial.md) - Learn to completely bypass UI elements*