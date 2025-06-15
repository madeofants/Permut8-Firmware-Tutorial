# Session 2025-01-06: Phase 1 - Critical Fixes Detailed Plan

## Phase 1 Objective
**Fix all blocking syntax issues that prevent HTML conversion**
- Convert wrong programming languages (C/Rust) to correct Impala syntax
- Standardize language usage across all documentation
- Ensure 100% compilation readiness

## Critical Issues Identified (From Meta-Analysis)

### 🚨 **BLOCKING - Reference Directory (4/8 files)**
**Status**: Complete rewrites required - wrong programming languages

1. **`audio_processing_reference.md`**
   - **Issue**: Uses C syntax instead of Impala
   - **Problems**: `#include <math.h>`, `void` functions, C data structures
   - **Action**: Complete rewrite with Impala audio processing patterns
   - **Est. Time**: 1.5 sessions

2. **`standard-library-reference.md`**
   - **Issue**: Complete C standard library documentation
   - **Problems**: Extensive C functions, `malloc/free`, C headers
   - **Action**: Rewrite as Impala utilities and native functions reference
   - **Est. Time**: 1.5 sessions

3. **`metaprogramming-constructs.md`**
   - **Issue**: Advanced C preprocessor techniques
   - **Problems**: `#define` macros, C build systems, preprocessor patterns
   - **Action**: Rewrite with Impala patterns and compile-time techniques
   - **Est. Time**: 1 session

4. **`types-and-operators.md`**
   - **Issue**: Uses Rust-style syntax
   - **Problems**: `let` keyword, `[int; 1024]` arrays, `fn` functions
   - **Action**: Convert to proper Impala syntax patterns
   - **Est. Time**: 0.5 sessions

### ⚠️ **IMPORTANT - Architecture Directory (1/5 files)**
**Status**: Good content, minor syntax fix needed

1. **`memory-layout.md`**
   - **Issue**: Uses C++ syntax instead of Impala
   - **Problems**: C++ classes, C++ memory management
   - **Action**: Convert to Impala memory patterns
   - **Est. Time**: 0.5 sessions

### ⚠️ **MEDIUM - Assembly Directory (8 files)**
**Status**: Correct content, standardization needed

1. **GAZL Syntax Inconsistencies**
   - **Issue**: Mixed assembly dialects and comment styles
   - **Problems**: `;` vs `//` comments, ARM64 vs Cortex-M4 mixing
   - **Action**: Standardize to GAZL-specific syntax
   - **Est. Time**: 0.5 sessions

## Detailed Execution Plan

### **Task 1: Reference Directory Critical Fixes**

#### 1.1 `standard-library-reference.md` (Priority: Highest)
**Current Issues**:
- 1120+ lines of C standard library documentation
- Functions like `malloc()`, `printf()`, `#include` statements
- Complete mismatch with Impala capabilities

**Rewrite Strategy**:
```impala
// Replace C standard library content with Impala equivalents
// OLD (C):
#include <math.h>
float sin(float x);
void* malloc(size_t size);

// NEW (Impala):
// Native math functions available in Impala
extern native yield
// Memory management via static allocation
global array buffer[1024]
```

**Content Structure**:
- Native Functions (yield, trace, read, write)
- Math Operations (trigonometric, arithmetic)
- String Utilities (if available in Impala)
- Memory Management (static allocation patterns)
- Debugging Functions (trace, error handling)

#### 1.2 `audio_processing_reference.md` (Priority: Highest)
**Current Issues**:
- 683+ lines of C audio processing code
- C function signatures, C data structures
- Complex C algorithms not applicable to Impala

**Rewrite Strategy**:
```impala
// Replace C audio processing with Impala patterns
// OLD (C):
void process_audio(float* input, float* output, int samples) {
    for (int i = 0; i < samples; i++) {
        output[i] = apply_filter(input[i]);
    }
}

// NEW (Impala):
function process() {
    loop {
        // Process global signal[0] and signal[1]
        signal[0] = apply_filter(signal[0])
        signal[1] = apply_filter(signal[1])
        yield()
    }
}
```

**Content Structure**:
- Signal Flow Fundamentals (12-bit audio range)
- Basic Filters (low-pass, high-pass, state variable)
- Audio Effects (distortion, modulation, dynamics)
- Performance Optimization (fixed-point, lookup tables)
- Common Patterns (parameter scaling, clipping)

#### 1.3 `metaprogramming-constructs.md` (Priority: Medium)
**Current Issues**:
- 1154+ lines of C preprocessor techniques
- Complex `#define` macros not available in Impala
- Build system integration for C projects

**Rewrite Strategy**:
```impala
// Replace C metaprogramming with Impala patterns
// OLD (C preprocessor):
#define DECLARE_FILTER(TYPE, NAME) \
    struct NAME##Filter { TYPE data; };

// NEW (Impala patterns):
// Use function patterns and static arrays
function create_lowpass_filter() {
    // Implementation using Impala syntax
}
```

**Content Structure**:
- Impala Pattern Libraries (function templates)
- Code Reuse Strategies (without preprocessor)
- Build Configuration (compilation flags)
- Template-like Patterns (parameter-driven code)

#### 1.4 `types-and-operators.md` (Priority: Medium)
**Current Issues**:
- 183 lines mixing Rust syntax with Impala concepts
- `let` keyword, Rust array syntax, Rust function syntax

**Rewrite Strategy**:
```impala
// Replace Rust syntax with proper Impala
// OLD (Rust-style):
let sample: int = -1024;
let delay_line: [int; 1024] = [0; 1024];
fn interpolate_lookup(table: [int; 256], position: int) -> int

// NEW (Impala):
int sample = -1024
global array delay_line[1024]
function interpolate_lookup(array table[256], int position) returns int result
```

### **Task 2: Architecture Directory Fix**

#### 2.1 `memory-layout.md`
**Current Issues**:
- C++ classes and syntax patterns
- C++ memory management concepts

**Fix Strategy**:
- Convert C++ examples to Impala equivalents
- Focus on static allocation patterns
- Maintain architectural concepts, fix syntax

### **Task 3: Assembly Directory Standardization**

#### 3.1 GAZL Syntax Consistency
**Issues to Fix**:
- Standardize comment style to `//` (GAZL standard)
- Separate ARM64 and Cortex-M4 specific content
- Use consistent assembly instruction formatting

**Standardization Pattern**:
```gazl
// GAZL standard syntax
.text
.global _start

_start:
    // Load immediate value
    mov r0, #0x1000
    // Function call
    bl audio_process
    // Return
    bx lr
```

## Success Criteria for Phase 1

### Technical Requirements
- [ ] 100% Impala syntax in all reference documents
- [ ] No C/Rust/C++ syntax remaining in any file
- [ ] All code examples follow Impala language standards
- [ ] Consistent GAZL syntax in assembly documents

### Functional Requirements
- [ ] All examples related to actual Permut8 capabilities
- [ ] Native functions properly documented
- [ ] Memory management reflects static allocation model
- [ ] Audio processing uses correct 12-bit range

### Quality Requirements
- [ ] Maintained technical depth while fixing syntax
- [ ] Preserved valuable content during rewrites
- [ ] Clear, educational examples throughout
- [ ] Ready for HTML conversion without syntax blockers

## Estimated Timeline

### Session 1 (Current): Standard Library + Audio Processing
- Complete `standard-library-reference.md` rewrite
- Begin `audio_processing_reference.md` rewrite

### Session 2: Finish Audio Processing + Metaprogramming
- Complete `audio_processing_reference.md` rewrite
- Complete `metaprogramming-constructs.md` rewrite

### Session 3: Types, Architecture, Assembly
- Complete `types-and-operators.md` fixes
- Fix `memory-layout.md` C++ syntax
- Standardize assembly directory syntax

### Session 4: Verification and Integration
- Compile-test all rewritten examples
- Verify cross-references work
- Final quality check before Phase 2

## Risk Mitigation

### Major Risks
1. **Content Loss**: Rewriting might eliminate useful information
2. **Scope Creep**: Rewrites reveal additional issues
3. **Syntax Errors**: New Impala code introduces compilation problems

### Mitigation Strategies
1. **Preserve Concepts**: Focus on syntax fixes, maintain technical depth
2. **Time-Box Work**: Limit rewrites to essential syntax corrections
3. **Test Examples**: Verify all code examples compile correctly

---

## Next Immediate Action
**Start with `standard-library-reference.md`** - this is the largest blocker with complete C standard library documentation that needs full Impala rewrite.

**Success Definition**: Phase 1 complete when all code examples use correct Impala syntax and documentation is HTML-ready.