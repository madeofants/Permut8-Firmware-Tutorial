# Permut8 Reference Documentation

*Complete API reference and technical specifications for Permut8 firmware development*

## Core API References

### Essential APIs
| Reference | Purpose | Key Functions |
|-----------|---------|---------------|
| [Audio Processing Reference](audio_processing_reference.md) | Core audio I/O and signal processing | `signal[]`, audio ranges, processing patterns |
| [Parameters Reference](parameters_reference.md) | Parameter handling and control mapping | `params[]`, parameter constants, binding |
| [Memory Management](memory_management.md) | Memory allocation and buffer management | Static allocation, buffer patterns |
| [Utilities Reference](utilities_reference.md) | Helper functions and system utilities | Math utilities, conversion functions |

### Language References
| Reference | Purpose | Coverage |
|-----------|---------|----------|
| [Core Language Reference](../language/core_language_reference.md) | Complete Impala language specification | Syntax, control flow, data types |
| [Standard Library Reference](../language/standard-library-reference.md) | Built-in functions and system APIs | Native functions, system calls |
| [Types and Operators](../language/types-and-operators.md) | Data handling and arithmetic operations | Type system, operators, casting |
| [Core Functions](../language/core-functions.md) | Essential built-in functions | Function reference, usage patterns |

---

## Advanced References

### System Programming
| Reference | Purpose | Applications |
|-----------|---------|--------------|
| [Advanced Memory Management](advanced/advanced-memory-management.md) | Complex memory patterns | Large buffers, optimization |
| [Real-time Safety](advanced/real-time-safety.md) | Hard real-time programming | Timing constraints, predictability |
| [Debugging Techniques](advanced/debugging-techniques.md) | Development and troubleshooting | Error detection, profiling |
| [Multi-file Projects](advanced/multi-file-projects.md) | Project organization | Modular development, code reuse |

### Build and Development
| Reference | Purpose | Applications |
|-----------|---------|--------------|
| [Build Directives](advanced/build-directives.md) | Compilation control | Conditional compilation, optimization |
| [Custom Build Tools](advanced/custom-build-tools.md) | Development workflow | Automation, testing |
| [Metaprogramming Constructs](advanced/metaprogramming-constructs.md) | Code generation | Templates, macros |
| [Utility Functions](advanced/utility-functions.md) | Common helper patterns | Reusable components |

### Integration and Optimization
| Reference | Purpose | Applications |
|-----------|---------|--------------|
| [Modulation Ready](advanced/modulation-ready.md) | Parameter modulation systems | LFOs, envelopes, control |

---

## Parameter System References

### Core Parameter Handling
| Reference | Purpose | Coverage |
|-----------|---------|----------|
| [Read Knobs](parameters/read-knobs.md) | Basic parameter input | Control reading, scaling |
| [Parameter Smoothing](parameters/parameter-smoothing.md) | Anti-click parameter changes | Interpolation, filtering |
| [MIDI CC Mapping](parameters/midi-cc-mapping.md) | External control integration | MIDI learn, CC assignment |

### Advanced Parameter Features  
| Reference | Purpose | Applications |
|-----------|---------|--------------|
| [Macro Controls](parameters/macro-controls.md) | Complex parameter relationships | Multi-parameter control |
| [Automation Sequencing](parameters/automation-sequencing.md) | Programmed parameter changes | Sequences, patterns |

---

## Quick Reference Tables

### Audio Processing Constants
```impala
// Audio sample range (12-bit signed)
const int AUDIO_MIN = -2047
const int AUDIO_MAX = 2047

// Parameter range (8-bit unsigned)  
const int PARAM_MIN = 0
const int PARAM_MAX = 255

// Required parameter indices
const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT
```

### Essential Global Variables
```impala
// Core audio I/O
global array signal[2]          // Left/Right audio samples
global array params[PARAM_COUNT] // Parameter values (0-255)
global array displayLEDs[4]     // LED ring displays

// Common utility variables
global int clock                 // Sample counter
global int clockFreqLimit        // Timing control
```

### Common Function Patterns
```impala
// Required function structure
function process()
locals /* declare local variables */
{
    loop {
        // Read parameters
        // Process audio
        // Update displays
        yield();  // REQUIRED: Return control to system
    }
}

// Required native function
extern native yield
```

---

## Reference by Category

### Audio & DSP
- **Signal Processing**: [Audio Processing Reference](audio_processing_reference.md)
- **Memory Patterns**: [Memory Management](memory_management.md)
- **Real-time Constraints**: [Real-time Safety](advanced/real-time-safety.md)

### Control & Parameters
- **Parameter System**: [Parameters Reference](parameters_reference.md)
- **Control Mapping**: [MIDI CC Mapping](parameters/midi-cc-mapping.md)
- **Smoothing**: [Parameter Smoothing](parameters/parameter-smoothing.md)

### Development & Debugging
- **Project Structure**: [Multi-file Projects](advanced/multi-file-projects.md)
- **Build Process**: [Build Directives](advanced/build-directives.md)
- **Troubleshooting**: [Debugging Techniques](advanced/debugging-techniques.md)

### Language & Syntax
- **Core Language**: [Core Language Reference](../language/core_language_reference.md)
- **Built-in Functions**: [Standard Library Reference](../language/standard-library-reference.md)
- **Data Types**: [Types and Operators](../language/types-and-operators.md)

---

## Cross-References

### From Tutorial to Reference
- **[Make Your First Sound](../user-guides/tutorials/make-your-first-sound.md)** → [Audio Processing Reference](audio_processing_reference.md)
- **[Control Something with Knobs](../user-guides/tutorials/control-something-with-knobs.md)** → [Parameters Reference](parameters_reference.md)
- **[Process Incoming Audio](../user-guides/tutorials/process-incoming-audio.md)** → [Memory Management](memory_management.md)

### From Cookbook to Reference
- **[Basic Oscillator](../user-guides/cookbook/fundamentals/basic-oscillator.md)** → [Core Functions](../language/core-functions.md)
- **[Make a Delay](../user-guides/cookbook/audio-effects/make-a-delay.md)** → [Memory Management](memory_management.md)
- **[Parameter Mapping](../user-guides/cookbook/fundamentals/parameter-mapping.md)** → [Parameters Reference](parameters_reference.md)

---

## API Quick Search

### By Function Type
- **Audio I/O**: `signal[]`, audio ranges, processing loops
- **Parameter Access**: `params[]`, parameter constants, control reading
- **Memory**: Buffer allocation, circular buffers, memory patterns
- **Control Flow**: `yield()`, loops, conditionals
- **Math**: Arithmetic, fixed-point, approximations
- **Display**: `displayLEDs[]`, visualization patterns

### By Use Case
- **Reading Controls**: [Parameters Reference](parameters_reference.md)
- **Processing Audio**: [Audio Processing Reference](audio_processing_reference.md)
- **Managing Memory**: [Memory Management](memory_management.md)
- **Debugging Code**: [Debugging Techniques](advanced/debugging-techniques.md)
- **Optimizing Performance**: [Real-time Safety](advanced/real-time-safety.md)

---

## Getting Help

**Can't find what you need?** 
- Check the [Master Index](../index/master-index.md) for comprehensive cross-references
- See [Navigation](../index/navigation.md) for alternative ways to find information
- Review [Cross-references](../index/cross-references.md) for related topics

**Need examples?**
- Browse the [Cookbook](../user-guides/cookbook/) for practical implementations
- Follow [Tutorials](../user-guides/tutorials/) for step-by-step guidance
- Study [Architecture Patterns](../architecture/) for design approaches

---

*Complete API documentation for professional Permut8 firmware development*

---

*Part of the [Permut8 Documentation](../index.md) • [User Guides](../user-guides/) • [Language Reference](../language/) • [Architecture](../architecture/)*