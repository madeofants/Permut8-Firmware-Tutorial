# TERMINOLOGY EXTRACT: understanding-impala-fundamentals.md

**Source File**: `/content/user-guides/tutorials/understanding-impala-fundamentals.md`  
**Extraction Date**: January 10, 2025  
**Terms Identified**: 35+ core terms  
**Category**: Tutorial Foundation - Language Mastery

---

## 📚 EXTRACTED TERMINOLOGY

### **CORE LANGUAGE TERMS** (8 terms)

#### **Impala**
- **Definition**: Real-time audio programming language for embedded systems
- **Context**: Domain-specific language designed for Permut8 hardware
- **Usage Example**: "Impala is specifically designed for real-time audio processing"
- **Related Terms**: real-time constraints, DSP, firmware

#### **Real-time constraints**
- **Definition**: Timing requirements for audio processing (no malloc, predictable execution)
- **Context**: Fundamental design principle of Impala language
- **Usage Example**: "Every feature is optimized for predictable timing"
- **Related Terms**: yield(), static allocation, audio processing

#### **Static allocation**
- **Definition**: Memory management using fixed-size arrays (no dynamic allocation)
- **Context**: Impala's approach to predictable memory usage
- **Usage Example**: "Impala uses only static memory allocation"
- **Related Terms**: global array, const int, no malloc

#### **yield()**
- **Definition**: Native function returning control to audio engine every sample
- **Context**: Critical function for real-time processing
- **Usage Example**: "yield() // Return control to host"
- **Related Terms**: extern native, loop construct, real-time

#### **Global variables**
- **Definition**: Persistent variables maintaining state between function calls
- **Context**: Variables that survive across audio processing cycles
- **Usage Example**: "global int oscillatorPhase = 0"
- **Related Terms**: locals, function scope, state persistence

#### **locals clause**
- **Definition**: Function variable declaration section for temporary variables
- **Context**: Impala's explicit function variable declaration
- **Usage Example**: "locals int tempValue, int result"
- **Related Terms**: function declaration, variable scope

#### **loop construct**
- **Definition**: Infinite loop for continuous audio processing
- **Context**: Impala's primary real-time processing pattern
- **Usage Example**: "loop { // Process audio; yield(); }"
- **Related Terms**: yield(), real-time, audio processing

#### **extern native**
- **Definition**: Declaration keyword for system-provided functions
- **Context**: Interface to Permut8 system functions
- **Usage Example**: "extern native yield"
- **Related Terms**: yield(), trace(), abort()

### **DATA TYPES & DECLARATIONS** (6 terms)

#### **const int**
- **Definition**: Compile-time constant declaration
- **Context**: Immutable integer values known at compile time
- **Usage Example**: "const int SAMPLE_RATE = 44100"
- **Related Terms**: constants, compilation, static values

#### **array declaration**
- **Definition**: Fixed-size array syntax with global/local scope
- **Context**: Static memory allocation for data storage
- **Usage Example**: "global array audioBuffer[1024]"
- **Related Terms**: static allocation, fixed-size, memory

#### **returns clause**
- **Definition**: Function output declaration section
- **Context**: Explicit declaration of function return values
- **Usage Example**: "returns int outputGain"
- **Related Terms**: function declaration, multiple returns

#### **to/to< operators**
- **Definition**: Inclusive/exclusive range operators in for loops
- **Context**: Impala's specific loop range syntax
- **Usage Example**: "for (i = 0 to 9)" vs "for (i = 0 to< 10)"
- **Related Terms**: for loops, range iteration

#### **Bit shifting**
- **Definition**: Performance optimization using << and >> operators
- **Context**: Efficient multiplication/division by powers of 2
- **Usage Example**: "int shifted = value << 2 // multiply by 4"
- **Related Terms**: performance, optimization, bitwise operations

#### **Parameter range**
- **Definition**: 0-255 values from hardware knobs and controls
- **Context**: Hardware interface value range
- **Usage Example**: "Knob values (0-255)"
- **Related Terms**: params array, hardware interface

### **HARDWARE INTERFACE TERMS** (6 terms)

#### **signal[2]**
- **Definition**: Global audio I/O array for stereo processing
- **Context**: Primary audio input/output interface
- **Usage Example**: "global array signal[2] // [left, right] audio samples"
- **Related Terms**: audio samples, stereo, I/O

#### **params[PARAM_COUNT]**
- **Definition**: Global parameter array for knob/control access
- **Context**: Interface to hardware parameter controls
- **Usage Example**: "global array params[PARAM_COUNT] // Knob values (0-255)"
- **Related Terms**: parameter range, hardware controls

#### **displayLEDs[4]**
- **Definition**: Global LED control array for visual feedback
- **Context**: Hardware LED display interface
- **Usage Example**: "global array displayLEDs[4] // LED control arrays"
- **Related Terms**: LED masking, visual feedback

#### **PRAWN_FIRMWARE_PATCH_FORMAT**
- **Definition**: Required firmware version constant (value: 2)
- **Context**: Firmware compatibility identifier
- **Usage Example**: "const int PRAWN_FIRMWARE_PATCH_FORMAT = 2"
- **Related Terms**: firmware format, compatibility

#### **Audio samples**
- **Definition**: 12-bit signed integers (-2047 to 2047) representing audio data
- **Context**: Digital audio representation in Permut8
- **Usage Example**: "Audio samples range from -2047 to 2047"
- **Related Terms**: signal array, audio range, 12-bit

#### **LED masking**
- **Definition**: Bit manipulation for LED display patterns
- **Context**: Creating visual patterns using bitwise operations
- **Usage Example**: "ledMask = ledMask | (1 << i) // Turn on LED i"
- **Related Terms**: displayLEDs, bitwise operations

### **AUDIO PROCESSING CONCEPTS** (8 terms)

#### **Audio range management**
- **Definition**: Preventing overflow beyond ±2047 limits
- **Context**: Essential practice for preventing audio distortion
- **Usage Example**: "Always clamp results to prevent overflow"
- **Related Terms**: clipping, audio samples, range limits

#### **Clipping**
- **Definition**: Limiting audio values to prevent distortion
- **Context**: Audio safety technique for range management
- **Usage Example**: "if (result > 2047) result = 2047"
- **Related Terms**: audio range, overflow prevention

#### **Phase accumulator**
- **Definition**: Counter for oscillator and modulation generation
- **Context**: Common pattern for audio synthesis
- **Usage Example**: "global int oscillatorPhase = 0"
- **Related Terms**: oscillators, synthesis, counters

#### **Filter history**
- **Definition**: Memory for IIR filter implementations
- **Context**: State storage for recursive filters
- **Usage Example**: "global array filterHistory[4] // Persistent filter memory"
- **Related Terms**: IIR filters, state storage, DSP

#### **Scaling**
- **Definition**: Mathematical technique for range conversion
- **Context**: Converting between different value ranges
- **Usage Example**: "int scaledValue = (input * 1000) / 255"
- **Related Terms**: range conversion, fixed-point math

#### **Cooperative multitasking**
- **Definition**: Processing model where functions voluntarily yield control
- **Context**: Real-time processing approach using yield()
- **Usage Example**: "Return control to host with yield()"
- **Related Terms**: yield(), real-time, processing model

#### **Frame-based processing**
- **Definition**: Processing audio one sample (or frame) at a time
- **Context**: Real-time audio processing approach
- **Usage Example**: "Process one audio sample per iteration"
- **Related Terms**: real-time, sample-based, audio processing

#### **Fixed-point arithmetic**
- **Definition**: Integer math techniques for fractional calculations
- **Context**: Performance optimization for audio calculations
- **Usage Example**: "Use integer math with scaling instead of float"
- **Related Terms**: integer math, performance, scaling

### **DEVELOPMENT CONCEPTS** (7 terms)

#### **Firmware structure**
- **Definition**: Required organization and components of Permut8 programs
- **Context**: Template for creating valid firmware
- **Usage Example**: "Every Permut8 firmware patch needs these elements"
- **Related Terms**: PRAWN_FIRMWARE_PATCH_FORMAT, required components

#### **Function signature**
- **Definition**: Complete function declaration including locals and returns
- **Context**: Impala's explicit function interface specification
- **Usage Example**: "function calculateGain(...) returns ... locals ..."
- **Related Terms**: locals clause, returns clause, function declaration

#### **Variable scope**
- **Definition**: Visibility and lifetime rules for variables (global vs local)
- **Context**: Understanding data persistence in real-time processing
- **Usage Example**: "Global variables persist between function calls"
- **Related Terms**: global variables, locals, state persistence

#### **Compilation target**
- **Definition**: GAZL assembly output from Impala source compilation
- **Context**: Final executable format for Permut8 hardware
- **Usage Example**: "Impala compiles to GAZL assembly"
- **Related Terms**: .gazl files, compilation process

#### **Debug output**
- **Definition**: Using trace() function for development diagnostics
- **Context**: Development tool for troubleshooting firmware
- **Usage Example**: "trace('Debug message') // Use sparingly"
- **Related Terms**: trace(), debugging, development

#### **Emergency stop**
- **Definition**: Using abort() function to halt firmware execution
- **Context**: Safety mechanism for development debugging
- **Usage Example**: "abort() // Stops firmware execution"
- **Related Terms**: abort(), debugging, safety

#### **Performance optimization**
- **Definition**: Techniques for efficient real-time audio processing
- **Context**: Methods for maintaining audio quality and timing
- **Usage Example**: "Use bit shifting for fast multiplication"
- **Related Terms**: bit shifting, real-time constraints, efficiency

---

## 🔍 TERMINOLOGY ANALYSIS

### **FREQUENCY ANALYSIS**
- **High Frequency**: audio (15x), function (12x), global (10x)
- **Medium Frequency**: real-time (8x), array (7x), processing (6x)
- **Technical Depth**: Comprehensive language coverage with audio focus

### **CONCEPT RELATIONSHIPS**
```
Impala Language Foundation
├── Core Language Features
│   ├── Static allocation (arrays, const)
│   ├── Function system (locals, returns, calls)
│   ├── Control flow (loop, for, while, if)
│   └── Real-time model (yield(), cooperative)
├── Hardware Interface
│   ├── Audio I/O (signal[2], ±2047 range)
│   ├── Parameter Input (params[], 0-255 range)
│   └── Visual Output (displayLEDs[4], masking)
├── Audio Processing
│   ├── Range Management (clipping, overflow)
│   ├── Performance (bit shifting, scaling)
│   └── Common Patterns (oscillators, filters)
└── Development Workflow
    ├── Firmware Structure (required components)
    ├── Debugging (trace, abort)
    └── Optimization (performance techniques)
```

### **LEARNING PROGRESSION**
- **Foundation**: Language basics, syntax, types
- **Structure**: Functions, control flow, memory model
- **Application**: Hardware interface, audio processing
- **Practice**: Complete firmware, common patterns
- **Mastery**: Optimization, debugging, professional techniques

---

## 📊 GLOSSARY CONTRIBUTION

**Total Terms for Master Glossary**: 35+  
**Core Language Concepts**: 14  
**Hardware Interface Terms**: 6  
**Audio Processing Terms**: 8  
**Development Concepts**: 7  

**Quality Assessment**: **Exceptional** - Comprehensive language foundation with clear definitions, practical examples, and progressive complexity

**Educational Value**: **Maximum** - Provides complete conceptual framework for all subsequent Permut8 development

---

**EXTRACTION COMPLETED**: January 10, 2025  
**NEXT FILE**: make-your-first-sound.md  
**GLOSSARY STATUS**: Comprehensive language foundation established