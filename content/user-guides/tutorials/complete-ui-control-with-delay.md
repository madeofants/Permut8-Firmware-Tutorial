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


const int AUDIO_MAX = 2047
const int AUDIO_MIN = -2047
const int PARAM_MAX = 255
const int MEMORY_SIZE = 65536
const int STEREO_OFFSET = 32768
const int LED_MAX = 255


const int OPERAND_1_HIGH_PARAM_INDEX = 0
const int OPERAND_1_LOW_PARAM_INDEX = 1
const int OPERAND_2_LOW_PARAM_INDEX = 2
const int OPERAND_2_HIGH_PARAM_INDEX = 3
const int OPERATOR_1_PARAM_INDEX = 4
const int OPERATOR_2_PARAM_INDEX = 5
const int SWITCHES_PARAM_INDEX = 6
const int CLOCK_FREQ_PARAM_INDEX = 7
const int PARAM_COUNT = 8


global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global array positions[2]
global clock
global clockFreqLimit


global masterClock = 0
global syncMode = 0
global reverseMode = 0
global tripletMode = 0
global dottedMode = 0
global writeProtectMode = 0


global array delayBuffer[2]
global int baseDelayTime = 1000
global int modulatedDelayTime = 1000
global int feedbackAmount = 100
global int crossFeedback = 50


function operate1() returns processed {
    locals clockFreq, switches, operator1Type, delayHigh, delayLow, combinedOperand, tempoFactor, currentPosition, readPosition, delayedSample
    

    clockFreq = params[CLOCK_FREQ_PARAM_INDEX]
    switches = params[SWITCHES_PARAM_INDEX]
    operator1Type = params[OPERATOR_1_PARAM_INDEX]
    delayHigh = params[OPERAND_1_HIGH_PARAM_INDEX]
    delayLow = params[OPERAND_1_LOW_PARAM_INDEX]
    

    syncMode = (switches & 0x01) != 0;
    reverseMode = (switches & 0x02) != 0;
    tripletMode = (switches & 0x04) != 0;
    dottedMode = (switches & 0x08) != 0;
    writeProtectMode = (switches & 0x10) != 0;
    

    masterClock = masterClock + 1;
    

    combinedOperand = (delayHigh << 8) | delayLow
    baseDelayTime = (combinedOperand >> 4) + 100;
    

    if (syncMode) {

        tempoFactor = (clockFreq >> 3) + 1
        
        if (tripletMode) {

            baseDelayTime = (baseDelayTime * 2) / 3;
        }
        
        if (dottedMode) {

            baseDelayTime = (baseDelayTime * 3) / 2;
        }
        

        baseDelayTime = (baseDelayTime / tempoFactor) * tempoFactor;
    }
    

    if (reverseMode) {

        modulatedDelayTime = -baseDelayTime;
    } else {
        modulatedDelayTime = baseDelayTime;
    }
    

    currentPosition = positions[0]
    readPosition = currentPosition - modulatedDelayTime
    

    if (readPosition < 0) readPosition = readPosition + 65536;
    if (readPosition >= 65536) readPosition = readPosition - 65536;
    

    read(readPosition, 1, delayBuffer)
    delayedSample = delayBuffer[0]
    

    if (!writeProtectMode) {

        delayBuffer[0] = signal[0];
        write(currentPosition, 1, delayBuffer);
    }

    

    signal[0] = delayedSample;
    
    return 1
}


function operate2() returns processed {
    locals operator2Type, feedbackHigh, feedbackLow, currentPosition, readPosition, rightDelayed, leftInput, rightInput, leftDelayed, leftOutput, rightOutput
    

    operator2Type = params[OPERATOR_2_PARAM_INDEX]
    feedbackHigh = params[OPERAND_2_HIGH_PARAM_INDEX]
    feedbackLow = params[OPERAND_2_LOW_PARAM_INDEX]
    

    feedbackAmount = (feedbackHigh * 3) / 4;
    crossFeedback = feedbackLow / 4;
    

    currentPosition = positions[1]
    readPosition = currentPosition - modulatedDelayTime
    

    if (readPosition < 0) readPosition = readPosition + 65536;
    if (readPosition >= 65536) readPosition = readPosition - 65536;
    

    read(readPosition + 32768, 1, delayBuffer)
    rightDelayed = delayBuffer[0]
    

    leftInput = signal[0]
    rightInput = signal[1]
    leftDelayed = signal[0]
    

    leftOutput = leftInput + (leftDelayed * feedbackAmount / 255) + (rightDelayed * crossFeedback / 255)
    rightOutput = rightInput + (rightDelayed * feedbackAmount / 255) + (leftDelayed * crossFeedback / 255)
    

    if (leftOutput > 2047) leftOutput = 2047;
    if (leftOutput < -2047) leftOutput = -2047;
    if (rightOutput > 2047) rightOutput = 2047;
    if (rightOutput < -2047) rightOutput = -2047;
    

    if (!writeProtectMode) {
        delayBuffer[0] = leftOutput;
        write(currentPosition, 1, delayBuffer);
        
        delayBuffer[0] = rightOutput;
        write(currentPosition + 32768, 1, delayBuffer);
    }
    

    signal[0] = leftOutput;
    signal[1] = rightOutput;
    
    return 1
}


function update() {
    locals tempoDiv, switchDisplay, delayPattern, activityLevel, feedbackDisplay
    

    if (syncMode) {

        tempoDiv = (params[CLOCK_FREQ_PARAM_INDEX] >> 3) + 1
        displayLEDs[0] = (1 << (tempoDiv - 1)) & 0xFF
    } else {

        displayLEDs[0] = params[CLOCK_FREQ_PARAM_INDEX]
    }
    

    switchDisplay = 0
    if (syncMode) switchDisplay |= 0x01
    if (reverseMode) switchDisplay |= 0x02
    if (tripletMode) switchDisplay |= 0x04
    if (dottedMode) switchDisplay |= 0x08
    if (writeProtectMode) switchDisplay |= 0x10
    displayLEDs[1] = switchDisplay
    


    delayPattern = (baseDelayTime >> 8) & 0xFF
    displayLEDs[2] = delayPattern
    


    activityLevel = (abs(signal[0]) + abs(signal[1])) >> 4
    feedbackDisplay = (feedbackAmount >> 1) | (activityLevel << 4)
    displayLEDs[3] = feedbackDisplay & 0xFF
}


function process() {
    loop {
        operate1()
        operate2()
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

switches = params[SWITCHES_PARAM_INDEX]
syncMode = (switches & 0x01) != 0
reverseMode = (switches & 0x02) != 0
tripletMode = (switches & 0x04) != 0
dottedMode = (switches & 0x08) != 0
writeProtectMode = (switches & 0x10) != 0
```

**Switch Effects**:
- **SYNC**: Quantizes delay time to tempo based on clock frequency
- **REV**: Reverses delay direction (reads from future)
- **Triplet**: 2/3 timing ratio for triplet delays
- **Dotted**: 1.5x timing ratio for dotted delays  
- **Write Protect**: Freezes delay memory content

### **LED Display Usage (All 4 Displays)**

```impala
displayLEDs[0] =
displayLEDs[1] =
displayLEDs[2] =
displayLEDs[3] =
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