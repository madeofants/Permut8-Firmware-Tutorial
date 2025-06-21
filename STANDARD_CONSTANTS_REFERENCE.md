# Standard Constants Reference for Permut8 Firmware

**Purpose**: Eliminate magic numbers and improve code clarity across all documentation  
**Usage**: Include this constants section at the top of every code example

---

## 🎯 Standard Constants Header

**Copy this exact section into every code example:**

```impala
// ===== STANDARD PERMUT8 CONSTANTS =====

// Parameter System Constants
const int PARAM_MAX = 255                    // Maximum knob/parameter value (8-bit)
const int PARAM_MIN = 0                      // Minimum knob/parameter value
const int PARAM_MID = 128                    // Parameter midpoint for bipolar controls
const int PARAM_SWITCH_THRESHOLD = 127       // Boolean parameter on/off threshold

// Audio Sample Range Constants (12-bit signed audio)
const int AUDIO_MAX = 2047                   // Maximum audio sample value (+12-bit)
const int AUDIO_MIN = -2047                  // Minimum audio sample value (-12-bit)
const int AUDIO_ZERO = 0                     // Audio silence/center value

// Sample Rate Constants
const int SAMPLE_RATE_44K1 = 44100          // Standard audio sample rate (Hz)
const int SAMPLE_RATE_HALF = 22050          // Half sample rate (0.5 second buffer at 44.1kHz)
const int SAMPLE_RATE_QUARTER = 11025       // Quarter sample rate (0.25 second buffer)

// Audio Scaling Constants (16-bit ranges for phase accumulators)
const int AUDIO_FULL_RANGE = 65536          // 16-bit full scale range (0-65535)
const int AUDIO_HALF_RANGE = 32768          // 16-bit half scale (bipolar center)
const int AUDIO_QUARTER_RANGE = 16384       // 16-bit quarter scale (triangle wave peaks)

// Mathematical Constants
const float PI = 3.14159265                 // Mathematical pi constant
const float TWO_PI = 6.28318531             // 2 * pi (full circle radians)
const float PI_OVER_2 = 1.57079633          // pi/2 (quarter circle radians)

// Buffer Size Constants (powers of 2 for efficiency)
const int SMALL_BUFFER = 128                // Small buffer size
const int MEDIUM_BUFFER = 512               // Medium buffer size  
const int LARGE_BUFFER = 1024               // Large buffer size
const int MAX_BUFFER = 2048                 // Maximum buffer size

// Bit Manipulation Constants
const int BITS_PER_BYTE = 8                 // Standard byte size
const int SHIFT_DIVIDE_BY_2 = 1             // Bit shift for divide by 2
const int SHIFT_DIVIDE_BY_4 = 2             // Bit shift for divide by 4
const int SHIFT_DIVIDE_BY_8 = 3             // Bit shift for divide by 8

// LED Display Constants
const int LED_OFF = 0x00                    // All LEDs off
const int LED_ALL_ON = 0xFF                 // All 8 LEDs on
const int LED_SINGLE = 0x01                 // Single LED pattern
const int LED_DOUBLE = 0x03                 // Two LED pattern
const int LED_QUAD = 0x0F                   // Four LED pattern
const int LED_BRIGHTNESS_FULL = 255         // Full LED brightness
const int LED_BRIGHTNESS_HALF = 127         // Half LED brightness

// Musical/Timing Constants
const int STANDARD_BPM = 120                // Standard tempo reference
const int QUARTER_NOTE_DIVISIONS = 4        // Divisions per quarter note
const int SEMITONES_PER_OCTAVE = 12         // Musical semitones in octave
const float A4_FREQUENCY = 440.0            // A4 reference frequency (Hz)
```

---

## 📋 Magic Number Replacement Guide

### **Critical Replacements (Phase 1)**

| **Old Magic Number** | **New Constant** | **Usage Context** | **Priority** |
|---------------------|------------------|------------------|--------------|
| `255` | `PARAM_MAX` | Parameter scaling, knob maximum | Critical |
| `128` | `PARAM_MID` | Parameter midpoint, switch threshold | Critical |
| `127` | `PARAM_SWITCH_THRESHOLD` | Boolean parameter logic | Critical |
| `2047` | `AUDIO_MAX` | Audio sample clipping, range limits | Critical |
| `-2047` | `AUDIO_MIN` | Audio sample clipping (negative) | Critical |

### **Audio Scaling Replacements (Phase 2)**

| **Old Magic Number** | **New Constant** | **Usage Context** | **Priority** |
|---------------------|------------------|------------------|--------------|
| `65536` | `AUDIO_FULL_RANGE` | Phase accumulator maximum, 16-bit range | High |
| `32768` | `AUDIO_HALF_RANGE` | Bipolar signal center, triangle wave | High |
| `16384` | `AUDIO_QUARTER_RANGE` | Triangle wave peaks, quarter phase | High |

### **Sample Rate Replacements (Phase 3)**

| **Old Magic Number** | **New Constant** | **Usage Context** | **Priority** |
|---------------------|------------------|------------------|--------------|
| `22050` | `SAMPLE_RATE_HALF` | Delay buffer sizing (0.5 sec) | Medium |
| `44100` | `SAMPLE_RATE_44K1` | Sample rate references | Medium |
| `11025` | `SAMPLE_RATE_QUARTER` | Small delay buffers (0.25 sec) | Medium |

---

## 🔧 Implementation Examples

### **Before: Magic Numbers (Confusing)**
```impala
function process()
{
    loop {
        // What do these numbers mean?!
        int param = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]  // 0-255
        int scaled = (param * 1000) / 255
        
        if (scaled > 2047) scaled = 2047
        if (scaled < -2047) scaled = -2047
        
        phase = (phase + rate) % 65536
        
        if (param > 127) {
            // Switch mode
        }
        
        yield()
    }
}
```

### **After: Named Constants (Self-Documenting)**
```impala
function process()
{
    loop {
        // Crystal clear purpose!
        int param = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]  // 0-PARAM_MAX
        int scaled = (param * 1000) / PARAM_MAX
        
        // Clamp to audio sample range
        if (scaled > AUDIO_MAX) scaled = AUDIO_MAX
        if (scaled < AUDIO_MIN) scaled = AUDIO_MIN
        
        // Phase accumulator wraparound
        phase = (phase + rate) % AUDIO_FULL_RANGE
        
        // Boolean parameter logic
        if (param > PARAM_SWITCH_THRESHOLD) {
            // Switch mode enabled
        }
        
        yield()
    }
}
```

---

## 📚 Educational Benefits

### **Improved Code Clarity**
- **Purpose immediately obvious** from constant names
- **Relationships clear** - PARAM_MAX vs AUDIO_MAX vs AUDIO_FULL_RANGE
- **Context preserved** - Constants explain why values chosen

### **Better Learning Experience**
- **Students understand rationale** behind numeric choices
- **Professional practices** taught from day 1
- **Easier debugging** - obvious when wrong constant used

### **Maintainability**
- **System-wide changes easy** - modify constants in one place
- **Less error-prone** - harder to use wrong values
- **Self-documenting** - code explains itself

---

## 🎯 Implementation Priorities

### **Phase 1: Critical Audio Constants (Immediate)**
Focus on the most frequent, highest-impact magic numbers:
- Parameter range constants (463 instances)
- Audio clipping constants (215 instances)

### **Phase 2: Audio Scaling Constants (High)**
Phase accumulator and bit depth constants:
- 16-bit range constants (98 instances)

### **Phase 3: Sample Rate Constants (Medium)**
Timing and buffer size constants:
- Sample rate constants (45 instances)

### **Phase 4: Utility Constants (Low)**
Mathematical and utility constants:
- Buffer sizes, bit shifts, LED patterns

---

## ✅ Quality Checklist

**For each file updated:**
- [ ] Constants header included at top
- [ ] All parameter scaling uses PARAM_MAX/PARAM_MID
- [ ] All audio clipping uses AUDIO_MAX/AUDIO_MIN  
- [ ] All phase math uses AUDIO_FULL_RANGE family
- [ ] Explanatory text updated to reference constants
- [ ] Mathematical relationships preserved
- [ ] Code compiles without errors
- [ ] Educational value enhanced

---

**This constants reference will transform cryptic magic numbers into self-documenting, professional-quality code that enhances both functionality and educational value.**