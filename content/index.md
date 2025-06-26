# Permut8 Firmware Documentation

*Complete guide to developing custom firmware for the Permut8 audio processing hardware*

## Welcome to Permut8 Development

Permut8 enables you to create custom audio effects and synthesizers that run directly on dedicated hardware, delivering ultra-low latency performance impossible with traditional computer-based plugins.

**New to firmware development?** Start with our [30-minute Quickstart Guide](user-guides/QUICKSTART.md) to get your first custom effect running immediately.

**Ready to explore?** Browse our comprehensive [Cookbook](user-guides/cookbook/) with 36+ complete, tested recipes for building professional audio effects.

---

## Documentation Structure

### 🚀 **Getting Started**
- **[QUICKSTART](user-guides/QUICKSTART.md)** - Your first firmware in 30 minutes
- **[How to Use This Documentation](user-guides/how-to-use-this-documentation.md)** - Navigation guide
- **[Understanding Permut8 Operators](user-guides/tutorials/understanding-permut8-operators.md)** - Built-in effects system

### 👨‍💻 **User Guides**
- **[Tutorials](user-guides/tutorials/)** - Step-by-step learning progression (21 tutorials)
- **[Cookbook](user-guides/cookbook/)** - Complete effect recipes (36+ examples)
  - Audio Effects, DSP Fundamentals, Spectral Processing
  - Timing & Sync, Utilities, Visual Feedback

### 📚 **Reference Documentation**
- **[API Reference](reference/)** - Complete function and system documentation
- **[Language Reference](language/)** - Impala programming language guide
- **[Architecture](architecture/)** - System design and memory management
- **[Performance](performance/)** - Optimization techniques and best practices

### 🔧 **Integration & Deployment**
- **[Integration](integration/)** - MIDI, presets, and external system connectivity
- **[Assembly Programming](assembly/)** - Low-level GAZL assembly language

---

## Learning Pathways

### **For Audio Programmers New to Firmware**
1. [QUICKSTART](user-guides/QUICKSTART.md) → [Make Your First Sound](user-guides/tutorials/make-your-first-sound.md)
2. [Audio Engineering for Programmers](fundamentals/audio-engineering-for-programmers.md)
3. [Basic Oscillator](user-guides/cookbook/fundamentals/basic-oscillator.md) cookbook recipe
4. [Complete Development Workflow](user-guides/tutorials/complete-development-workflow.md)

### **For DSP Engineers**
1. [Understanding Impala Fundamentals](user-guides/tutorials/understanding-impala-fundamentals.md)
2. [Memory Management](reference/memory_management.md) and [Real-time Safety](reference/advanced/real-time-safety.md)
3. [Performance Optimization](performance/) techniques
4. [Advanced effects](user-guides/cookbook/audio-effects/) in the cookbook

### **For Experienced Firmware Developers**
1. [Architecture Patterns](architecture/architecture_patterns.md)
2. [GAZL Assembly](assembly/) programming
3. [Advanced Memory Management](reference/advanced/advanced-memory-management.md)
4. [Multi-file Projects](reference/advanced/multi-file-projects.md)

---

## Quick Reference

### **Essential APIs**
- **[Audio Processing](reference/audio_processing_reference.md)** - Core audio I/O and signal processing
- **[Parameters](reference/parameters_reference.md)** - Control handling and parameter mapping
- **[Memory Management](reference/memory_management.md)** - Buffer allocation and memory patterns
- **[Core Functions](language/core-functions.md)** - Built-in function reference

### **Common Patterns**
```impala
// Basic firmware structure
function process()
locals /* declare variables */
{
    loop {
        // Read parameters: params[PARAM_INDEX]
        // Process audio: signal[0] (left), signal[1] (right)
        // Update LEDs: displayLEDs[0-3]
        yield();  // REQUIRED: Return control to system
    }
}
```

### **Key Concepts**
- **Real-time Constraints**: No dynamic allocation, predictable execution
- **Audio Range**: 12-bit signed samples (-2047 to +2047)
- **Parameter Range**: 8-bit unsigned values (0-255)
- **Memory Model**: Static allocation with circular buffers

---

## Navigation and Search

### **By Content Type**
- **[Cross-references](index/cross-references.md)** - Topic relationships and connections
- **[Master Index](index/master-index.md)** - Comprehensive A-Z reference
- **[Glossary](index/glossary.md)** - Technical terms and definitions
- **[Navigation Guide](index/navigation.md)** - How to find information efficiently

### **By Use Case**
- **Learning DSP**: [Fundamentals](fundamentals/) → [Cookbook](user-guides/cookbook/fundamentals/)
- **Building Effects**: [Tutorials](user-guides/tutorials/) → [Audio Effects Cookbook](user-guides/cookbook/audio-effects/)
- **Optimization**: [Performance](performance/) → [Advanced Reference](reference/advanced/)
- **Integration**: [MIDI](integration/midi-learn.md) → [Presets](integration/preset-system.md)

---

## Community and Support

### **Getting Help**
- **Compilation Issues**: [Compiler Troubleshooting Guide](user-guides/tutorials/compiler-troubleshooting-guide.md)
- **Runtime Problems**: [Debug Your Plugin](user-guides/tutorials/debug-your-plugin.md)
- **Performance Questions**: [Optimization Basics](performance/optimization-basics.md)

### **Contributing**
This documentation is designed to grow with the community. The [Cookbook](user-guides/cookbook/) especially benefits from real-world examples and creative applications.

---

## What Makes Permut8 Special

**Hardware-Level Performance**: Your code runs directly on dedicated audio hardware, eliminating the latency and unpredictability of computer-based processing.

**Professional Results**: Create effects and instruments that respond instantly to user input with sample-accurate timing.

**Creative Freedom**: Build audio processors that don't exist anywhere else, with complete control over every aspect of the sound.

**Production Ready**: From quick experiments to professional products, Permut8 provides the tools for any scale of audio development.

---

*Start your firmware development journey with the [QUICKSTART guide](user-guides/QUICKSTART.md) and discover what's possible when you have complete control over audio processing hardware.*

---

**Documentation Version**: Current  
**Last Updated**: 2025  
**Firmware Compatibility**: Permut8 Firmware Format v2