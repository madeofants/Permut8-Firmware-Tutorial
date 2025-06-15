# SESSION MANAGEMENT PROTOCOLS

**Purpose**: Universal session management framework for any coding project  
**Usage**: Copy and adapt for new projects requiring session continuity  
**Extracted From**: Documentation Project and Tessellation Engine development

---

## 🔄 UNIVERSAL SESSION RECOVERY

### **Standard Recovery Command**
```
TodoRead + Read PROJECT-STATUS-TRACKER.md + Read [PROJECT_INGESTION_FILE] + Read [LATEST_SESSION_LOG] + Task "find most recent session context"
```

### **Session Startup Checklist Template**
```markdown
## Session Startup Protocol

### 1. Context Recovery (5 minutes)
- [ ] TodoRead executed
- [ ] Project status tracker reviewed
- [ ] Latest session log read
- [ ] Current development target identified

### 2. Environment Validation (3 minutes)
- [ ] Development environment ready
- [ ] Dependencies available
- [ ] Test files/samples accessible
- [ ] Git status clean or documented

### 3. Work Planning (5 minutes)
- [ ] Current session objectives defined
- [ ] TodoWrite updated with specific tasks
- [ ] Success criteria established
- [ ] Validation plan prepared
```

---

## 📋 TODO MANAGEMENT STANDARDS

### **Task Completion Rules**
- **ONLY mark completed when FULLY accomplished**
- **If errors/blockers encountered, keep as in_progress**
- **When blocked, create new task describing what needs resolution**
- **Complete existing tasks before starting new ones**

### **Task Breakdown Pattern**
```
Instead of: "Implement feature X"
Use:
- [ ] "Create basic function for X"
- [ ] "Add validation for X function"
- [ ] "Test X function with sample data"
- [ ] "Integrate X function with main system"
```

### **Priority Guidelines**
- **High**: Core functionality, blocking issues
- **Medium**: Features, improvements, debugging tools
- **Low**: Optimization, documentation, nice-to-have features

---

## 📝 SESSION LOG TEMPLATE

```markdown
# Session [Date]: [Project] - [Focus Area]

## Session Objectives
- [ ] [Primary goal for this session]
- [ ] [Secondary goal]
- [ ] [Testing/validation goal]

## Environment Status
- **Development Environment**: [Status]
- **Last Successful Build/Test**: [When]
- **Current Working Branch**: [Git info]
- **Test Data Available**: [Status]

## Work Completed
### [Timestamp] - [Task Name]
- **Files Modified**: [List]
- **Functionality Added/Changed**: [Description]
- **Testing Results**: [Pass/Fail/Pending]
- **Visual Confirmation**: [Screenshots, outputs, etc.]

## Current Status
- **Core System**: [Status - working/broken/in progress]
- **Testing Pipeline**: [Status]
- **Integration**: [How components work together]
- **Blockers**: [Any issues preventing progress]

## Next Session Handoff
**Immediate Next Action**: [Specific next step]
**Validation Required**: [What needs testing/confirmation]
**Context Notes**: [Important info not to lose]
```

---

## 🛡️ FILE SAFETY PROTOCOLS

### **Core Safety Rules**
1. **Work on copies when possible** - Preserve originals
2. **Backup before major changes** - Create safety copies
3. **Never delete without explicit permission** - Ask user first
4. **Document all changes** - Maintain audit trail

### **Working Copy Creation**
```bash
# Standard working copy setup
create_working_copy() {
    local source="$1"
    local work_dir="working-copy"
    
    echo "🛡️ Creating safe working copy..."
    rm -rf "$work_dir" 2>/dev/null
    cp -r "$source" "$work_dir"
    
    echo "✅ Working copy ready: $work_dir/"
    echo "🛡️ Originals preserved: $source"
}
```

### **Change Documentation**
```bash
# Document significant changes
document_change() {
    local file="$1"
    local description="$2"
    
    echo "$(date): Modified $file - $description" >> change-log.txt
}
```

---

## 🔧 PROJECT SETUP STANDARDS

### **Universal Directory Structure**
```
project-name/
├── core/                 # Main implementation
├── examples/             # Working demos and tests
├── tests/               # Validation and testing
├── docs/                # Documentation
├── session-logs/        # Session tracking
├── existing-code/       # Legacy/reference code
├── PROJECT-STATUS-TRACKER.md
└── [PROJECT-NAME]-INGESTION.md
```

### **Standard Files to Create**
```bash
# Core tracking files
touch PROJECT-STATUS-TRACKER.md
touch README.md
touch .gitignore

# Session management
mkdir -p session-logs
touch session-logs/session-$(date +%Y%m%d)-initialization.md

# Development structure
mkdir -p {core,examples,tests,docs}
```

### **Development Environment Validation**
```python
# Standard validation script template
def validate_environment():
    """Verify development environment is ready"""
    checks = {
        'dependencies': check_dependencies(),
        'test_data': check_test_data(),
        'core_functions': test_core_functions()
    }
    
    for check, status in checks.items():
        print(f"{'✅' if status else '❌'} {check}")
    
    return all(checks.values())
```

---

## 📊 QUALITY VALIDATION PATTERNS

### **Universal Validation Requirements**
- **Functional Testing**: Core features work as expected
- **Integration Testing**: Components work together
- **Regression Testing**: Changes don't break existing functionality
- **Visual Confirmation**: Output matches expectations (where applicable)

### **Validation Script Template**
```bash
#!/bin/bash
# validate-project.sh

echo "🔍 Project Validation"
echo "===================="

# Test core functionality
echo "Testing core functions..."
if run_core_tests; then
    echo "✅ Core tests pass"
else
    echo "❌ Core tests fail"
    exit 1
fi

# Test integration
echo "Testing integration..."
if run_integration_tests; then
    echo "✅ Integration tests pass"
else
    echo "❌ Integration tests fail"
    exit 1
fi

echo "🎉 All validations pass"
```

---

## 🚀 PROJECT INGESTION TEMPLATE

### **Ingestion File Structure**
```markdown
# [PROJECT-NAME] - PROJECT INGESTION

**Purpose**: [Brief description]
**Context**: [Project background]
**Session Recovery Command**: [Standard recovery command]

## 🎯 PROJECT OVERVIEW
[Vision, status, requirements]

## 🚀 IMMEDIATE PROJECT SETUP
[Step-by-step setup instructions]

## 📋 SESSION MANAGEMENT PROTOCOLS
[Project-specific session rules]

## 🔧 DEVELOPMENT RULES
[Coding standards and practices]

## 🎯 DEVELOPMENT TASKS
[Phased task breakdown]

## 📊 SUCCESS METRICS
[How to measure progress]
```

---

## 🔄 ADAPTATION GUIDELINES

### **For Different Project Types**

#### **Code Refactoring Projects**
- Add migration validation requirements
- Include side-by-side comparison protocols
- Emphasize preservation of existing functionality

#### **New Development Projects**
- Focus on incremental building and testing
- Add architectural decision documentation
- Include prototype and proof-of-concept phases

#### **Documentation Projects**
- Add content quality assessment frameworks
- Include systematic audit procedures
- Focus on completeness and accuracy validation

#### **Research/Experimental Projects**
- Add hypothesis tracking and validation
- Include experiment documentation protocols
- Focus on learning capture and iteration

---

## 📝 USAGE INSTRUCTIONS

### **For New Projects**
1. Copy relevant protocols from this meta-protocols folder
2. Adapt session log template for project specifics
3. Customize directory structure for project needs
4. Create project-specific ingestion file
5. Establish project-specific validation criteria

### **For Ongoing Projects**
1. Use session recovery command at start of each session
2. Follow session startup checklist
3. Update session logs after major work
4. Use TodoWrite for task management
5. Apply file safety protocols for changes

### **For Project Handoffs**
1. Ensure session logs are complete
2. Verify PROJECT-STATUS-TRACKER.md is current
3. Create comprehensive ingestion file
4. Document any project-specific procedures
5. Test session recovery process

---

**This meta-protocols folder serves as a reusable foundation for any future project requiring systematic session management, quality validation, and development continuity.**