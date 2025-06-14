# TERMINOLOGY EXTRACT: QUICKSTART.md

**Source File**: `/content/user-guides/QUICKSTART.md`  
**Extraction Date**: January 10, 2025  
**Terms Identified**: 25 core terms  
**Category**: Tutorial Foundation

---

## 📚 EXTRACTED TERMINOLOGY

### **CORE PERMUT8 TERMS** (5 terms)

#### **Permut8**
- **Definition**: Hardware DSP platform and audio plugin
- **Context**: Main product for running custom firmware
- **Usage Example**: "Open Permut8 in your DAW"
- **Related Terms**: firmware, console, patch

#### **Firmware**
- **Definition**: Custom code running on Permut8 hardware (.impala source, .gazl compiled)
- **Context**: User-created audio processing programs
- **Usage Example**: "You just loaded custom firmware!"
- **Related Terms**: .impala, .gazl, patch, compiler

#### **Console**
- **Definition**: Plugin interface for loading firmware and debugging
- **Context**: Command interface within Permut8 plugin
- **Usage Example**: "Click the console button (bottom right)"
- **Related Terms**: patch command, debugging

#### **PikaCmd.exe**
- **Definition**: Impala compiler executable
- **Context**: Tool that compiles .impala files to .gazl
- **Usage Example**: "PikaCmd.exe -compile ringmod_code.impala"
- **Related Terms**: compilation, .impala, .gazl

#### **PRAWN_FIRMWARE_PATCH_FORMAT**
- **Definition**: Required firmware version constant (value: 2)
- **Context**: Compatibility identifier for firmware format
- **Usage Example**: "const int PRAWN_FIRMWARE_PATCH_FORMAT = 2"
- **Related Terms**: const int, firmware compatibility

### **IMPALA LANGUAGE TERMS** (6 terms)

#### **extern native**
- **Definition**: Declaration keyword for system-provided functions
- **Context**: Links to Permut8 system functions
- **Usage Example**: "extern native yield"
- **Related Terms**: yield(), native functions

#### **yield()**
- **Definition**: Native function returning control to audio engine
- **Context**: Required for real-time audio processing
- **Usage Example**: "yield();" at end of processing loop
- **Related Terms**: extern native, processing loop

#### **global**
- **Definition**: Keyword for persistent variables across processing cycles
- **Context**: Variables that maintain state between function calls
- **Usage Example**: "global array signal[2]"
- **Related Terms**: signal, params, displayLEDs

#### **locals**
- **Definition**: Function variable declaration clause
- **Context**: Declares temporary variables for function scope
- **Usage Example**: "locals int bits, int shift, int mask"
- **Related Terms**: function declaration, variable scope

#### **readonly array**
- **Definition**: Immutable array declaration
- **Context**: Arrays that cannot be modified after initialization
- **Usage Example**: "readonly array panelTextRows[8]"
- **Related Terms**: array, const, panel text

#### **const int**
- **Definition**: Constant integer declaration
- **Context**: Immutable integer values
- **Usage Example**: "const int PRAWN_FIRMWARE_PATCH_FORMAT = 2"
- **Related Terms**: constants, firmware format

### **HARDWARE INTERFACE TERMS** (5 terms)

#### **signal[2]**
- **Definition**: Global audio I/O array (left/right channels)
- **Context**: Primary audio input/output interface
- **Usage Example**: "global signal[0] = processed_left; global signal[1] = processed_right;"
- **Related Terms**: audio samples, left/right channels

#### **params[8]**
- **Definition**: Global parameter array (knob values 0-255)
- **Context**: Interface to hardware knob controls
- **Usage Example**: "bits = ((int) global params[3] >> 5) + 1;"
- **Related Terms**: knobs, parameter control, 0-255 range

#### **displayLEDs[4]**
- **Definition**: Global LED control array (8-bit brightness values)
- **Context**: Visual feedback interface
- **Usage Example**: "global displayLEDs[0] = 1 << (bits - 1);"
- **Related Terms**: LED animation, visual feedback

#### **patch command**
- **Definition**: Console command to load firmware
- **Context**: Loading compiled firmware into Permut8
- **Usage Example**: "patch bitcrush.gazl"
- **Related Terms**: console, .gazl files, firmware loading

#### **Audio samples**
- **Definition**: 12-bit signed values (-2047 to 2047)
- **Context**: Digital audio representation in Permut8
- **Usage Example**: "Audio samples range from -2047 to 2047"
- **Related Terms**: signal array, bit depth, digital audio

### **AUDIO PROCESSING TERMS** (5 terms)

#### **Bit crusher**
- **Definition**: Effect reducing audio bit depth for lo-fi sound
- **Context**: Example effect demonstrating audio processing
- **Usage Example**: "Let's create a simple bit crusher from scratch"
- **Related Terms**: bit depth, lo-fi, digital distortion

#### **Bit depth**
- **Definition**: Number of bits representing audio sample precision
- **Context**: Audio quality parameter in bit crushing
- **Usage Example**: "Read bit depth from first knob (0-255 mapped to 1-12 bits)"
- **Related Terms**: bit crusher, audio quality, digital audio

#### **Ring modulator**
- **Definition**: Effect multiplying input by oscillator
- **Context**: Example firmware for modification exercises
- **Usage Example**: "The ring modulator is now running"
- **Related Terms**: modulation, oscillator, multiplication

#### **Left/right channels**
- **Definition**: Stereo audio signal components
- **Context**: Stereo audio processing in signal array
- **Usage Example**: "signal[0] = left channel, signal[1] = right channel"
- **Related Terms**: signal[2], stereo, audio channels

#### **DSP**
- **Definition**: Digital Signal Processing
- **Context**: Audio processing domain of Permut8 firmware
- **Usage Example**: "Replace entire DSP engine"
- **Related Terms**: audio processing, digital audio, firmware

### **DEVELOPMENT TERMS** (4 terms)

#### **Full patches**
- **Definition**: Firmware replacing entire DSP engine
- **Context**: One of two main firmware types
- **Usage Example**: "Full Patches (like our bit crusher): Replace entire DSP engine"
- **Related Terms**: mod patches, firmware types, DSP engine

#### **Mod patches**
- **Definition**: Firmware modifying built-in operators
- **Context**: Alternative firmware type for operator modification
- **Usage Example**: "Mod Patches (like linsub): Modify built-in operators"
- **Related Terms**: full patches, operators, built-in functions

#### **Compilation**
- **Definition**: Process converting .impala source to .gazl executable
- **Context**: Build process for firmware development
- **Usage Example**: "PikaCmd.exe -compile bitcrush.impala"
- **Related Terms**: PikaCmd.exe, .impala, .gazl

#### **LED animation**
- **Definition**: Visual feedback programming using displayLEDs array
- **Context**: User interface enhancement technique
- **Usage Example**: "Add Rainbow LED animation synced to modulation"
- **Related Terms**: displayLEDs, visual feedback, user interface

---

## 🔍 TERMINOLOGY ANALYSIS

### **FREQUENCY ANALYSIS**
- **High Frequency**: firmware (8x), audio (6x), Permut8 (5x)
- **Medium Frequency**: LED (4x), parameters (4x), signal (3x)
- **Technical Depth**: Balanced beginner-friendly with technical accuracy

### **CONCEPT RELATIONSHIPS**
```
Permut8 Platform
├── Hardware Interface
│   ├── signal[2] (audio I/O)
│   ├── params[8] (knob inputs)
│   └── displayLEDs[4] (visual output)
├── Development Workflow
│   ├── .impala (source code)
│   ├── PikaCmd.exe (compiler)
│   ├── .gazl (compiled firmware)
│   └── patch command (loading)
└── Firmware Types
    ├── Full patches (complete DSP replacement)
    └── Mod patches (operator modification)
```

### **BEGINNER ACCESSIBILITY**
- **Clear Definitions**: All terms explained in context
- **Progressive Complexity**: Simple concepts first, advanced later
- **Practical Examples**: Every term shown in working code
- **Consistent Usage**: Terminology used consistently throughout

---

## 📊 GLOSSARY CONTRIBUTION

**Total Terms for Master Glossary**: 25  
**Unique Permut8 Concepts**: 5  
**Core Technical Terms**: 15  
**Development Workflow Terms**: 5  

**Quality Assessment**: **Excellent** - Clear, consistent, beginner-appropriate definitions with practical examples

---

**EXTRACTION COMPLETED**: January 10, 2025  
**NEXT FILE**: understanding-impala-fundamentals.md  
**GLOSSARY STATUS**: Foundation terminology established