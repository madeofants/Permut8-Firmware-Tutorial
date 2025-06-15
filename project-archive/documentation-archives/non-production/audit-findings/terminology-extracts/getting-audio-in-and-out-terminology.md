# TERMINOLOGY EXTRACT: getting-audio-in-and-out.md

**Source File**: `/content/user-guides/tutorials/getting-audio-in-and-out.md`  
**Extraction Date**: January 10, 2025  
**Terms Identified**: 15+ core terms  
**Category**: Tutorial Foundation - I/O fundamentals

---

## 📚 EXTRACTED TERMINOLOGY

### **CORE AUDIO I/O TERMS** (5 terms)

#### **Audio passthrough**
- **Definition**: Default behavior where audio flows unchanged through plugin
- **Context**: Foundation concept where plugin processes but doesn't modify audio
- **Usage Example**: "Audio automatically passes through - we don't need to do anything!"
- **Related Terms**: signal array, audio flow, real-time processing

#### **Signal array**
- **Definition**: Global audio interface arrays for stereo I/O (`signal[0]`, `signal[1]`)
- **Context**: Primary connection between plugin and Permut8 hardware audio
- **Usage Example**: "signal[2] = left and right audio channels"
- **Related Terms**: audio passthrough, stereo channels, hardware interface

#### **Real-time processing**
- **Definition**: Sample-by-sample audio processing at audio rate
- **Context**: Fundamental approach for live audio effect processing
- **Usage Example**: "This runs 44,100 times per second (at 44.1kHz sample rate)"
- **Related Terms**: yield(), sample processing, audio flow

#### **Audio flow**
- **Definition**: Path of audio signal from input through plugin to output
- **Context**: Conceptual model of how audio travels through processing chain
- **Usage Example**: "Audio Input → Your Plugin → Audio Output"
- **Related Terms**: audio passthrough, signal array, real-time processing

#### **Stereo channels**
- **Definition**: Left and right audio channels for stereo processing
- **Context**: Professional audio standard for dual-channel audio handling
- **Usage Example**: "signal[0] = left, signal[1] = right"
- **Related Terms**: signal array, audio flow, professional processing

### **PLUGIN STRUCTURE TERMS** (4 terms)

#### **PRAWN_FIRMWARE_PATCH_FORMAT**
- **Definition**: Required constant identifying firmware version
- **Context**: Essential header declaring plugin compatibility with Permut8
- **Usage Example**: "const int PRAWN_FIRMWARE_PATCH_FORMAT = 2"
- **Related Terms**: global variables, plugin structure, firmware format

#### **Global variables**
- **Definition**: Persistent arrays connecting plugin to Permut8 hardware
- **Context**: Required interface declarations for hardware communication
- **Usage Example**: "global array signal[2]; global array params[8]; global array displayLEDs[4]"
- **Related Terms**: hardware interface, signal array, firmware format

#### **Process function**
- **Definition**: Main processing function running continuously during operation
- **Context**: Core function containing all audio processing logic
- **Usage Example**: "function process() { loop { yield() } }"
- **Related Terms**: yield(), plugin structure, real-time processing

#### **yield()**
- **Definition**: Critical function returning control to audio engine each sample
- **Context**: Essential for cooperative multitasking in real-time audio
- **Usage Example**: "yield() // Give control back so next sample can be processed"
- **Related Terms**: process function, real-time processing, audio engine

### **DEVELOPMENT WORKFLOW TERMS** (4 terms)

#### **Compilation**
- **Definition**: Converting .impala source to .gazl executable
- **Context**: Build process transforming human-readable code to device firmware
- **Usage Example**: "PikaCmd.exe -compile audio_passthrough.impala"
- **Related Terms**: plugin loading, development workflow, PikaCmd

#### **Plugin loading**
- **Definition**: Process of installing compiled firmware into Permut8
- **Context**: Deployment step making plugin active on hardware
- **Usage Example**: "patch audio_passthrough.gazl"
- **Related Terms**: compilation, console command, firmware deployment

#### **Audio modification**
- **Definition**: Mathematical operations on audio samples
- **Context**: Core technique for creating effects and processing
- **Usage Example**: "signal[0] = signal[0] / 2 // Left channel half volume"
- **Related Terms**: signal array, real-time processing, audio effects

#### **LED feedback**
- **Definition**: Visual confirmation using displayLEDs array
- **Context**: User interface technique showing plugin state visually
- **Usage Example**: "displayLEDs[0] = 0xFF // All LEDs on in first display"
- **Related Terms**: visual feedback, user interface, hardware interface

### **TECHNICAL INTERFACE TERMS** (2 terms)

#### **Console command**
- **Definition**: Text interface for loading and controlling Permut8 firmware
- **Context**: Command-line interface within DAW plugin for development
- **Usage Example**: "Click the console button (bottom-right of Permut8 interface)"
- **Related Terms**: plugin loading, patch command, development interface

#### **Hardware interface**
- **Definition**: Connection points between plugin software and Permut8 hardware
- **Context**: Abstract layer managing communication with physical device
- **Usage Example**: "These connect your plugin to Permut8 hardware"
- **Related Terms**: global variables, signal array, params array, displayLEDs

---

## 🔍 TERMINOLOGY ANALYSIS

### **FREQUENCY ANALYSIS**
- **High Frequency**: audio (45x), plugin (25x), signal (20x)
- **Medium Frequency**: yield (8x), process (12x), hardware (6x)
- **Technical Depth**: Foundation-level with complete workflow coverage

### **CONCEPT RELATIONSHIPS**
```
Audio I/O Foundation
├── Core Concepts
│   ├── Audio passthrough (default behavior)
│   ├── Signal array (hardware interface)
│   ├── Real-time processing (sample-by-sample)
│   └── Audio flow (input → plugin → output)
├── Plugin Structure
│   ├── PRAWN_FIRMWARE_PATCH_FORMAT (version declaration)
│   ├── Global variables (hardware connection)
│   ├── Process function (main processing loop)
│   └── yield() (control return mechanism)
├── Development Workflow
│   ├── Compilation (source to executable)
│   ├── Plugin loading (firmware deployment)
│   ├── Audio modification (effects creation)
│   └── LED feedback (visual confirmation)
└── Hardware Interface
    ├── Console command (development interface)
    └── Hardware interface (software-hardware bridge)
```

### **LEARNING PROGRESSION**
- **Foundation**: Basic audio flow and plugin structure
- **Implementation**: Step-by-step plugin creation
- **Testing**: Compilation and loading workflow
- **Modification**: Basic audio effects techniques
- **Validation**: Visual and audio feedback systems

---

## 📊 GLOSSARY CONTRIBUTION

**Total Terms for Master Glossary**: 15+  
**Core Audio I/O**: 5  
**Plugin Structure**: 4  
**Development Workflow**: 4  
**Technical Interface**: 2  

**Quality Assessment**: **Excellent** - Essential I/O foundation with complete workflow

**Educational Value**: **Maximum** - Critical terminology for all Permut8 development

**Professional Relevance**: **High** - Industry-standard audio I/O concepts

---

## 🎯 I/O TERMINOLOGY SIGNIFICANCE

### **Foundation for All Audio Development**:
- **Audio Effects**: Signal modification and processing
- **Sound Generation**: Output through signal arrays
- **Parameter Control**: Hardware interface understanding
- **Visual Feedback**: User interface development

### **Development Workflow Mastery**:
- **Code-to-Hardware Pipeline**: Complete understanding of compilation and deployment
- **Real-time Constraints**: yield() and processing loop concepts
- **Hardware Abstraction**: Interface between software and device
- **Testing Methodology**: Audio and visual validation techniques

---

**EXTRACTION COMPLETED**: January 10, 2025  
**NEXT FILE**: control-something-with-knobs.md  
**GLOSSARY STATUS**: I/O foundation terminology established