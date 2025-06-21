# Phase 3: Systematic Tutorial and Cookbook Update Plan

**Date**: 2025-06-20  
**Status**: Phase 3 Planning Complete  
**Target**: 79 files identified with raw parameter indices

## 🎯 PRIORITIZED UPDATE STRATEGY

### Tier 1: Core Learning Path (Priority: CRITICAL)
**Files that new users encounter first - must be error-free**

1. **getting-audio-in-and-out.md** - Fundamental audio processing
2. **make-your-first-sound.md** - First synthesis experience  
3. **process-incoming-audio.md** - Basic audio processing
4. **light-up-leds.md** - Hardware interaction basics
5. **control-something-with-knobs.md** - Parameter control introduction

### Tier 2: Building Complexity (Priority: HIGH)
**Tutorials that build on core concepts**

6. **add-controls-to-effects.md** - Control integration
7. **build-your-first-filter.md** - DSP fundamentals
8. **simple-delay-explained.md** - Time-based effects
9. **understanding-impala-fundamentals.md** - Language deep dive
10. **test-your-plugin.md** - Development workflow

### Tier 3: Advanced Tutorials (Priority: MEDIUM)
**Complex multi-concept tutorials**

11. **complete-ui-control-with-delay.md** - Complex UI patterns
12. **advanced-custom-delay-tutorial.md** - Advanced DSP
13. **custom-interface-bypass-tutorial.md** - Interface customization
14. **complete-development-workflow.md** - Full development cycle
15. **build-complete-firmware.md** - Complete projects

### Tier 4: Cookbook Fundamentals (Priority: HIGH)
**Core cookbook patterns used throughout**

16. **fundamentals/gain-and-volume.md** - Volume control patterns
17. **fundamentals/parameter-mapping.md** - Parameter access patterns
18. **fundamentals/switches-and-modes.md** - Control logic
19. **fundamentals/basic-oscillator.md** - Signal generation
20. **fundamentals/basic-filter.md** - Signal processing

### Tier 5: Advanced Cookbook (Priority: MEDIUM)
**Complex effects and patterns**

21-79. **Remaining 59 files** - Audio effects, spectral processing, utilities, etc.

## 🔧 STANDARD UPDATE PATTERN FOR EACH FILE

### 1. Parameter Access Updates
```impala
// ❌ BEFORE (causes compilation errors)
volume = params[3] * 2;
cutoff = params[1] * 1000 + 20;
resonance = (int)params[2] * 10;

// ✅ AFTER (verified working pattern)
volume = (int)global params[OPERAND_2_HIGH_PARAM_INDEX] * 2;
cutoff = (int)global params[OPERAND_1_LOW_PARAM_INDEX] * 1000 + 20;
resonance = (int)global params[OPERAND_1_HIGH_PARAM_INDEX] * 10;
```

### 2. Function Signature Updates
```impala
// ❌ BEFORE (incomplete signatures)
function process()
{
    loop {
        // processing
    }
}

// ✅ AFTER (proper locals and yield)
function process()
locals int volume, int inputL, int inputR, int outputL, int outputR
{
    loop {
        // processing
        yield(); // REQUIRED
    }
}
```

### 3. Required Constants Section
```impala
// Add to each file that uses parameters:
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

### 4. Standard Global Variables
```impala
global int clock = 0
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clockFreqLimit = 132300
```

## 📋 SYSTEMATIC EXECUTION PLAN

### Phase 3A: Core Learning Path (Files 1-5)
- **Time Estimate**: 2-3 hours
- **Strategy**: Perfect these first - they're most critical for user success
- **Testing**: Verify each example compiles after update

### Phase 3B: Building Complexity (Files 6-10)  
- **Time Estimate**: 2-3 hours
- **Strategy**: Apply patterns learned from Tier 1
- **Focus**: Maintain learning progression flow

### Phase 3C: Advanced Tutorials (Files 11-15)
- **Time Estimate**: 3-4 hours  
- **Strategy**: Complex multi-step updates
- **Focus**: Preserve advanced concept explanations

### Phase 3D: Cookbook Fundamentals (Files 16-20)
- **Time Estimate**: 2-3 hours
- **Strategy**: Create template patterns for other cookbooks
- **Focus**: Standardize parameter access patterns

### Phase 3E: Advanced Cookbook (Files 21-79)
- **Time Estimate**: 8-10 hours
- **Strategy**: Batch processing with standardized patterns
- **Focus**: Efficiency and consistency

## ✅ SUCCESS CRITERIA FOR EACH FILE

### Technical Requirements:
- [ ] All `params[0-7]` changed to `params[CONSTANT_NAME]`
- [ ] Function signatures include proper `locals` declarations  
- [ ] Process loops include `yield()` calls
- [ ] Required constants section added
- [ ] Global variables standardized

### Quality Requirements:
- [ ] Learning progression maintained
- [ ] Explanations updated to match new patterns
- [ ] Code comments reflect proper parameter access
- [ ] Examples demonstrate best practices

## 🚀 EXECUTION STRATEGY

### "Foundation First, Scale Outward" Approach:
1. **Perfect Tier 1** (most critical for user success)
2. **Apply patterns to Tier 2** (building on solid foundation)
3. **Scale to remaining tiers** (systematic pattern application)
4. **Validate compilation** (ensure all examples work)
5. **Update HTML documentation** (reflect all changes)

### Quality Assurance:
- Update files in learning order (preserve progression)
- Test compilation of updated examples  
- Cross-reference with updated foundation files
- Maintain consistent parameter access patterns

## 📁 REFERENCE FILES FOR PATTERN APPLICATION

### Template Files (UPDATED, USE THESE PATTERNS):
- `content/language/core-functions.md` - Function signature patterns
- `content/reference/parameters_reference.md` - Parameter access patterns
- `content/language/types-and-operators.md` - Casting and syntax patterns
- `content/user-guides/QUICKSTART.md` - Simple example patterns

### Pattern Source (VERIFIED):
- `IMPALA_LANGUAGE_REFERENCE_UPDATES.md` - Complete verified patterns
- `extracted_gazl/*_decompiled.impala` - 13 official firmware examples

## 🎯 ESTIMATED COMPLETION

### Total Files: 79
### Total Time Estimate: 17-23 hours
### Critical Path: Tier 1 files (5 files, 2-3 hours)
### Success Metric: 100% compilation success rate

---

**READY TO EXECUTE**: Phase 3A - Core Learning Path (Files 1-5)  
**FOUNDATION**: Solid reference files with verified patterns  
**APPROACH**: Systematic, prioritized, quality-focused updates