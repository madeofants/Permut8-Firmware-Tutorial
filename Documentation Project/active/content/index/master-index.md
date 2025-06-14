# Permut8 Firmware Development - Master Index

*Complete reference index for all production documentation*

## Quick Start Guides

### Essential Learning Path
- **[QUICKSTART](../user-guides/QUICKSTART.md)** - 30-minute introduction to Permut8 firmware development
- **[Mod vs Full Architecture Guide](../user-guides/tutorials/mod-vs-full-architecture-guide.md)** - Choose the right firmware type
- **[Getting Audio In and Out](../user-guides/tutorials/getting-audio-in-and-out.md)** - Foundation I/O tutorial (10 minutes)
- **[Complete Development Workflow](../user-guides/tutorials/complete-development-workflow.md)** - Professional workflow methodology
- **[Debug Your Plugin](../user-guides/tutorials/debug-your-plugin.md)** - Systematic troubleshooting guide
- **[Understanding Impala Fundamentals](../user-guides/tutorials/understanding-impala-fundamentals.md)** - Core language concepts [*Archived*]

### Architecture Decisions
- **[Mod vs Full Architecture Guide](../user-guides/tutorials/mod-vs-full-architecture-guide.md)** - Essential architectural foundation

## Language Reference

### Core Language
- **[Core Language Reference](../language/core_language_reference.md)** - Complete Impala language specification
- **[Language Syntax Reference](../language/language-syntax-reference.md)** - Syntax rules and patterns
- **[Types and Operators](../language/types-and-operators.md)** - Data types and operations
- **[Core Functions](../language/core-functions.md)** - Built-in function reference
- **[Standard Library Reference](../language/standard-library-reference.md)** - Standard library functions

### Glossary and Terms
- **[Glossary](glossary.md)** - Complete terminology reference (100+ terms)
- **[Language Foundation](language-foundation.md)** - Language ecosystem navigation
- **[Themes](themes.md)** - Professional theme organization

## Cookbook Recipes

### Fundamentals
Essential building blocks for all firmware development:

- **[Basic Filter](../user-guides/cookbook/fundamentals/basic-filter.md)** - Digital filter implementation
- **[Envelope Basics](../user-guides/cookbook/fundamentals/envelope-basics.md)** - ADSR envelope control
- **[Gain and Volume](../user-guides/cookbook/fundamentals/gain-and-volume.md)** - Volume control with smoothing
- **[Switches and Modes](../user-guides/cookbook/fundamentals/switches-and-modes.md)** - Discrete control patterns
- **[Stereo Processing](../user-guides/cookbook/fundamentals/stereo-processing.md)** - Mid-side and stereo effects
- **[Parameter Mapping](../user-guides/cookbook/fundamentals/parameter-mapping.md)** - Parameter scaling and curves

### Audio Effects
Complete working effects with full source code:

- **[Bitcrusher](../user-guides/cookbook/audio-effects/bitcrusher.md)** - Digital distortion effect
- **[Chorus Effect](../user-guides/cookbook/audio-effects/chorus-effect.md)** - Modulated delay chorus
- **[Basic Compressor](../user-guides/cookbook/audio-effects/compressor-basic.md)** - Dynamic range compression
- **[Granular Synthesis](../user-guides/cookbook/audio-effects/granular-synthesis.md)** - Particle-based synthesis
- **[Make a Delay](../user-guides/cookbook/audio-effects/make-a-delay.md)** - Digital delay with feedback
- **[Phaser Effect](../user-guides/cookbook/audio-effects/phaser-effect.md)** - All-pass filter phasing
- **[Pitch Shifter](../user-guides/cookbook/audio-effects/pitch-shifter.md)** - Real-time pitch manipulation
- **[Waveshaper Distortion](../user-guides/cookbook/audio-effects/waveshaper-distortion.md)** - Nonlinear distortion
- **[Multi-band Compressor](../user-guides/cookbook/audio-effects/multi-band-compressor.md)** - Frequency-split compression
- **[Simple Reverb](../user-guides/cookbook/audio-effects/reverb-simple.md)** - Basic reverberation

## Integration Systems

### Working Implementations
- **[Preset System](../integration/preset-system.md)** - Complete preset management (Impala syntax)
- **[State Recall - Simplified](../integration/state-recall-simplified.md)** - Essential state management
- **[MIDI Learn - Simplified](../integration/midi-learn-simplified.md)** - Dynamic CC assignment  
- **[MIDI Sync - Simplified](../integration/midi-sync-simplified.md)** - Clock synchronization

### Reference Implementations
- **[State Recall](../integration/state-recall.md)** - Advanced state management concepts
- **[MIDI Learn](../integration/midi-learn.md)** - Advanced MIDI learn concepts
- **[MIDI Sync](../integration/midi-sync.md)** - Advanced synchronization concepts
- **[Parameter Morphing](../integration/parameter-morphing.md)** - Dynamic parameter control
- **[Preset Friendly](../integration/preset-friendly.md)** - Preset design patterns

## Architecture Reference

### Memory and Processing
- **[Memory Model](../architecture/memory-model.md)** - Static memory allocation patterns
- **[Memory Layout](../architecture/memory-layout.md)** - Memory organization and optimization
- **[Processing Order](../architecture/processing-order.md)** - Audio pipeline architecture
- **[State Management](../architecture/state-management.md)** - Persistent state patterns
- **[Architecture Patterns](../architecture/architecture_patterns.md)** - Design pattern collection

## Performance Optimization

### Memory and Speed
- **[Optimization Basics](../performance/optimization-basics.md)** - Essential optimization techniques
- **[Memory Patterns](../performance/memory-patterns.md)** - Efficient memory usage
- **[Efficient Math](../performance/efficient-math.md)** - Mathematical optimizations
- **[Fixed Point](../performance/fixed-point.md)** - Fixed-point arithmetic
- **[Lookup Tables](../performance/lookup-tables.md)** - Precomputed value tables
- **[Memory Access](../performance/memory-access.md)** - Cache-friendly access patterns
- **[Batch Processing](../performance/batch-processing.md)** - Block-based processing

## Assembly Integration

### GAZL Assembly
- **[GAZL Assembly Introduction](../assembly/gazl-assembly-introduction.md)** - Assembly language basics
- **[GAZL Debugging and Profiling](../assembly/gazl-debugging-profiling.md)** - Debug assembly code
- **[GAZL Integration Production](../assembly/gazl-integration-production.md)** - Production deployment
- **[GAZL Optimization](../assembly/gazl-optimization.md)** - Assembly optimization techniques

## API Reference

### Complete API Documentation
- **[Parameters Reference](../reference/parameters_reference.md)** - Parameter system API
- **[Audio Processing Reference](../reference/audio_processing_reference.md)** - Audio API functions
- **[Memory Management](../reference/memory_management.md)** - Memory API reference
- **[Utilities Reference](../reference/utilities_reference.md)** - Utility function API

## Navigation Tools

### Finding Information
- **[Navigation](navigation.md)** - Master navigation hub
- **[Cross References](cross-references.md)** - Troubleshooting and cross-links
- **[Master Index](master-index.md)** - This complete index

---

## By Development Stage

### Beginner (Start Here)
1. **[QUICKSTART](../user-guides/QUICKSTART.md)** - Essential first steps
2. **[Mod vs Full Architecture Guide](../user-guides/tutorials/mod-vs-full-architecture-guide.md)** - Choose architecture type
3. **[Getting Audio In and Out](../user-guides/tutorials/getting-audio-in-and-out.md)** - Foundation I/O tutorial
4. **[Basic Filter](../user-guides/cookbook/fundamentals/basic-filter.md)** - First real effect
5. **[Gain and Volume](../user-guides/cookbook/fundamentals/gain-and-volume.md)** - Parameter control
6. **[Make a Delay](../user-guides/cookbook/audio-effects/make-a-delay.md)** - First complex effect

### Intermediate
1. **[Complete Development Workflow](../user-guides/tutorials/complete-development-workflow.md)** - Professional methodology
2. **[Debug Your Plugin](../user-guides/tutorials/debug-your-plugin.md)** - Essential troubleshooting skills
3. **[Envelope Basics](../user-guides/cookbook/fundamentals/envelope-basics.md)** - Time-based control
4. **[Stereo Processing](../user-guides/cookbook/fundamentals/stereo-processing.md)** - Multi-channel audio
5. **[Parameter Mapping](../user-guides/cookbook/fundamentals/parameter-mapping.md)** - Advanced control
6. **[Preset System](../integration/preset-system.md)** - State management

### Advanced
1. **[Memory Patterns](../performance/memory-patterns.md)** - Optimization techniques
2. **[GAZL Assembly](../assembly/gazl-assembly-introduction.md)** - Low-level programming
3. **[MIDI Sync](../integration/midi-sync-simplified.md)** - External synchronization
4. **[Architecture Patterns](../architecture/architecture_patterns.md)** - System design

## By Use Case

### Audio Effects Development
- Start with **[Cookbook Fundamentals](#fundamentals)**
- Progress to **[Audio Effects](#audio-effects)**
- Optimize with **[Performance](#performance-optimization)**

### System Integration
- Begin with **[Integration Systems](#integration-systems)**
- Study **[Architecture Reference](#architecture-reference)**
- Implement with **[API Reference](#api-reference)**

### Performance Critical Applications
- Master **[Memory Model](../architecture/memory-model.md)**
- Apply **[Performance Optimization](#performance-optimization)**
- Consider **[Assembly Integration](#assembly-integration)**

---

## File Status Legend

- **No marker** - Production ready (A/A+ grade)
- **[*Archived*]** - High-quality content in archive (not production)
- **[*Missing*]** - Critical gap identified in analysis

**Total Production Files**: 64 documents  
**Quality Standard**: A/A+ grades (90%+ quality scores)  
**Last Updated**: January 11, 2025