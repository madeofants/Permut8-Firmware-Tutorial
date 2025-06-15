# Permut8 Knob Interface Analysis - Session Progress Save

**Date**: June 15, 2025  
**Session Focus**: Foundational fix of knob naming and interface documentation  
**Status**: In Progress - Critical findings established  

## 🔍 Key Discoveries

### **Original Permut8 Interface vs Custom Firmware**

**CRITICAL FINDING**: The original Permut8 uses **switches** for operand control, NOT knobs. Custom firmware overrides this with knob controls via `panelTextRows`.

### **Official User Guide Analysis**
- **Source**: `/docs/Permut8+User+Guide.txt` (extracted from PDF)
- **Key Finding**: "There are two eight-bit parameters per instruction, called 'operands'. You can set individual 'bits' of these parameters with the switches." (Line 41)
- **Interface**: Original Permut8 has 1 CLOCK FREQ knob + switches for operands
- **Custom Firmware**: Alternative firmwares can override interface with custom knob controls

## 📊 Foundational Knob Reference Table (VERIFIED)

| Physical Position | Parameter Index | Constant Name | Original Permut8 | Custom Firmware Use | Range |
|------------------|----------------|---------------|------------------|-------------------|-------|
| **Top-Left** | `params[3]` | `OPERAND_1_HIGH_PARAM_INDEX` | Operand 1 High (switches) | Custom knob control | 0-255 |
| **Bottom-Left** | `params[4]` | `OPERAND_1_LOW_PARAM_INDEX` | Operand 1 Low (switches) | Custom knob control | 0-255 |
| **Top-Right** | `params[6]` | `OPERAND_2_HIGH_PARAM_INDEX` | Operand 2 High (switches) | Custom knob control | 0-255 |
| **Bottom-Right** | `params[7]` | `OPERAND_2_LOW_PARAM_INDEX` | Operand 2 Low (switches) | Custom knob control | 0-255 |

### **System Parameters (Not User Controls)**
- `params[0]` = CLOCK_FREQ_PARAM_INDEX (sample rate)
- `params[1]` = SWITCHES_PARAM_INDEX (switch bitmask)  
- `params[2]` = OPERATOR_1_PARAM_INDEX (hex operation)
- `params[5]` = OPERATOR_2_PARAM_INDEX (hex operation)

## 🐛 Critical Issues Found

### **QUICKSTART Bitcrush Tutorial Problems**
1. ❌ **Wrong labeling**: Uses "knob 3" for `params[3]` (actually top-left)
2. ❌ **Wrong description**: Calls `params[3]` "clock sync knob" (completely incorrect)  
3. ❌ **Missing context**: Doesn't explain custom firmware interface override
4. ❌ **Inconsistent placement**: panelTextRows positioning doesn't match parameter usage

### **Documentation-Wide Issues**
- Inconsistent knob naming across all files
- Confusion between original interface and custom firmware capabilities
- Missing explanation of interface override concept

## 🎯 Required Fixes (Todo List Status)

### ✅ Completed Tasks
- [x] Create comprehensive knob reference table
- [x] Convert Permut8 User Guide PDF to readable format  
- [x] Analyze official user guide interface description
- [x] Create table distinguishing original vs custom firmware interfaces

### 🔄 In Progress
- [ ] Update parameters reference with clear knob naming table
- [ ] Audit all documentation files for incorrect knob references
- [ ] Standardize knob naming conventions across all docs
- [ ] Fix QUICKSTART bitcrush tutorial with correct knob names
- [ ] Validate all code examples use correct knob references

## 📝 Specific QUICKSTART Fixes Needed

### **Current Broken Code** (line 92):
```impala
bits = ((int) global params[3] >> 5) + 1;  // WRONG LABELING
```

### **panelTextRows Issue** (line 77):
```impala
"BIT |-------- CRUSH AMOUNT (KNOB 3) --------|",  // WRONG - params[3] is top-left, not "knob 3"
```

### **Correct Fixes Required**:
1. **Use consistent naming**: "Top-Left Knob" or "Operand 1 High"
2. **Fix panelTextRows positioning**: Row 3 (line 76) for `params[3]`
3. **Add interface explanation**: Explain custom firmware vs original interface
4. **Consider better knob choice**: Maybe use `params[6]` (top-right) for main effect control

## 🔧 Ring Modulator Reference (Working Example)

```impala
readonly array panelTextRows[8] = {
    " ",
    " ", 
    " ",
    "    |----- LEFT DELAY -----| |----- RIGHT DELAY ----|",  // params[3] and params[6]
    " ",
    " ",
    " ",
    "    |--- RING MOD RATE ----| |---- STEREO PHASE ----|"   // params[4] and params[7]
}
```

## 📁 Files Requiring Updates

### **High Priority**
- `/Documentation Project/active/content/reference/parameters_reference.md`
- `/Documentation Project/active/content/user-guides/QUICKSTART.md`

### **Secondary Priority**  
- All cookbook examples using parameter references
- All tutorial files with knob examples
- Cross-reference documentation

## 🚨 Critical Understanding for Future Work

**Key Principle**: When documenting Permut8 firmware development:
1. **Distinguish** between original interface (switches) and custom firmware (knobs)
2. **Use consistent naming**: Physical position OR parameter constant name
3. **Explain interface override** concept for beginners
4. **Verify panelTextRows positioning** matches parameter usage

## 📋 Session Context for Continuation

- **User Issue**: Bitcrush tutorial knob assignment problems and math issues
- **Root Cause**: Foundational documentation inconsistency about interface
- **Solution Approach**: Fix foundation first, then specific issues
- **Next Session**: Begin implementing standardized naming across all docs

---
**Session saved for continuation** ✅