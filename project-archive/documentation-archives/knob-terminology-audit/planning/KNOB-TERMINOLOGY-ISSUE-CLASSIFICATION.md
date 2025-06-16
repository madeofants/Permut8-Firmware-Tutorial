# Knob Terminology Issue Classification Matrix

**Date**: June 16, 2025  
**Phase**: Discovery and Classification Results  
**Total Files Scanned**: 79 markdown files  
**Files with Knob References**: 16 files  

## 📊 Discovery Summary

### **Overall Scope**
- **Total markdown files**: 79
- **Files containing "knob" references**: 16 files (20% of documentation)
- **Critical issues identified**: 4 high-priority files
- **Systematic pattern issues**: Generic knob numbering, operator knob misuse

### **Issue Severity Classification**

#### **🚨 CRITICAL (Must Fix Immediately)**
Files with incorrect operator knob references or severe user confusion:

| File | Issue Type | Current Problem | Impact | Priority |
|------|------------|-----------------|---------|----------|
| `QUICKSTART.md` | Incorrect operator knob usage | "Operator Knob 1 (Delay Time)" for `params[3]` | Very High - Most visible user doc | 1 |

#### **🔴 HIGH PRIORITY (Major User Confusion)**
Files with ambiguous or contextless knob references:

| File | Issue Type | Current Problem | Impact | Priority |
|------|------------|-----------------|---------|----------|
| `parameters_reference.md` | Generic knob numbering | "knob 1", "knob 2" without context | High - Reference doc | 2 |
| `complete-development-workflow.md` | Vague parameter references | "mapped from knob 0-255" | High - Tutorial doc | 3 |
| `custom-interface-bypass-tutorial.md` | Needs verification | May contain knob references | Medium-High | 4 |

#### **🟡 MEDIUM PRIORITY (Clarity Improvements)**
Files with terminology that could be clearer:

| File | Issue Type | Current Problem | Impact | Priority |
|------|------------|-----------------|---------|----------|
| `architecture_patterns.md` | Context needed | Knob references in architecture discussion | Medium | 5 |
| `getting-audio-in-and-out.md` | Context needed | Basic parameter introduction | Medium | 6 |
| Various cookbook files | Inconsistent patterns | Mixed terminology usage | Medium | 7-10 |

#### **🟢 LOW PRIORITY (Minor or Already Correct)**
Files with acceptable knob references or recently created content:

| File | Issue Type | Status | Priority |
|------|------------|--------|----------|
| Planning documents | Intentional examples | Already using correct terminology | Low |
| Reference documentation | Technical accuracy | May need minor context additions | Low |

## 🔍 Detailed Issue Analysis

### **Critical Issue: QUICKSTART.md**

**Problem Lines Identified:**
```
Line 308: "Operator Knob 1 (Delay Time)": Left = short delay, Right = long delay
Line 309: "Operator Knob 2 (Feedback)": Left = single echo, Right = multiple repeats  
Line 313: "turn Operator Knob 1 slowly to hear delay time changes"
Line 314: "Add feedback with Operator Knob 2 to create multiple echoes"
```

**Root Cause**: Confusing operator knobs (operation selection) with operand controls (parameter setting)

**Correct Fix**: Use "Control 1" and "Control 2" with proper context explanation

### **High Priority: parameters_reference.md**

**Problem Areas:**
```
Line 225: "Convert knob 1 to mix amount"
Line 228: "Convert knob 2 to feedback"
```

**Root Cause**: Generic knob numbering without interface context

**Correct Fix**: Specify "Control 1 (Instruction 1 High Operand)" etc.

### **Pattern Analysis: Generic Knob Numbering**

**Common Pattern**: `knob [0-9]` without context
- Appears in 4+ files
- Creates confusion about which physical control
- Missing distinction between original vs custom firmware

**Solution Pattern**: Always specify context and parameter mapping

## 📋 Correction Templates

### **Template 1: Custom Firmware Control References**

**Instead of:**
```markdown
Turn Knob 1 to adjust delay time
Set Knob 2 for feedback amount
```

**Use:**
```markdown
Adjust Control 1 (Instruction 1 High Operand position) for delay time
Set Control 2 (Instruction 1 Low Operand position) for feedback amount
```

### **Template 2: Code Comment Standards**

**Instead of:**
```impala
int delayTime = (int)params[3];  // Delay time from knob
```

**Use:**
```impala
int delayTime = (int)params[3];  // Control 1: Delay time (Instruction 1 High Operand)
```

### **Template 3: Original vs Custom Context**

**Always Include Context:**
```markdown
## Controls

### Original Operator System
- **Instruction 1 High Operand** (`params[3]`): Set via LED display and switches

### Custom Firmware Override  
- **Control 1** (`params[3]`): Direct delay time control (overrides operand interface)
```

## 📊 File Priority Matrix

### **Immediate Action Required (Week 1)**
1. **QUICKSTART.md** - Fix critical operator knob misuse
2. **parameters_reference.md** - Create master terminology standard
3. **complete-development-workflow.md** - Fix generic knob references

### **High Priority Updates (Week 2)**  
4. **custom-interface-bypass-tutorial.md** - Verify and fix if needed
5. **getting-audio-in-and-out.md** - Add proper context
6. **architecture_patterns.md** - Clarify interface references

### **Systematic Updates (Week 3)**
7-16. **Remaining cookbook and tutorial files** - Apply consistent terminology

## 🎯 Success Metrics

### **Completion Targets**
- **Critical issues**: 0 remaining (100% fixed)
- **High priority issues**: 0 remaining (100% fixed)  
- **Medium priority issues**: 90%+ fixed
- **Terminology consistency**: 100% across all user-facing docs

### **Quality Gates**
- [ ] No ambiguous "Knob 1/2/3/4" references remain
- [ ] All "Operator Knob" references are contextually correct
- [ ] All parameter references include proper context
- [ ] All custom firmware descriptions explain interface transformation

## 🚀 Next Phase Actions

### **Immediate Next Steps**
1. **Begin Phase 2**: Create master reference in parameters_reference.md
2. **Fix QUICKSTART critical issues** immediately after master reference
3. **Establish templates** for systematic updates
4. **Begin high-priority file updates** using established patterns

This classification provides the roadmap for systematic terminology correction across all Permut8 documentation.