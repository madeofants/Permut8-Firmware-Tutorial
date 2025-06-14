# PROJECT INGESTION TEMPLATE

**Purpose**: Universal template for creating project ingestion files  
**Usage**: Copy and customize for any new project requiring session management  
**Instructions**: Replace [PLACEHOLDER] sections with project-specific information

---

## 📋 TEMPLATE USAGE INSTRUCTIONS

### **Quick Setup Checklist**
1. Copy this template to `[PROJECT-NAME]-INGESTION.md`
2. Replace all `[PLACEHOLDER]` sections with project-specific details
3. Customize the development tasks for your project type
4. Adapt the environment setup for your tech stack
5. Modify session protocols for project-specific needs

### **Customization Areas**
- **Project Overview**: Vision, status, tech stack
- **Environment Setup**: Dependencies, tools, structure
- **Development Rules**: Coding standards, validation requirements
- **Task Breakdown**: Phase-based development plan
- **Success Metrics**: Quality gates and completion criteria

---

# [PROJECT-NAME] - PROJECT INGESTION

**Purpose**: [Brief description of project purpose]  
**Context**: [Project background - new development, refactoring, etc.]  
**Session Recovery Command**: `TodoRead + Read [PROJECT-NAME]-INGESTION.md + Read PROJECT-STATUS-TRACKER.md + Read [LATEST_SESSION_LOG]`

---

## 🎯 PROJECT OVERVIEW

### **Project Vision**
[Describe what you're building and why]

### **Project Status**: [NEW DEVELOPMENT / REFACTORING / CONVERSION / etc.]
[Brief description of current state and what needs to be done]

### **Core Requirements**
- **[Requirement 1]**: [Description]
- **[Requirement 2]**: [Description]
- **[Requirement 3]**: [Description]
- **[Requirement 4]**: [Description]

### **Technical Architecture**
- **Language**: [Primary programming language]
- **Core Libraries**: [Key dependencies]
- **Development Style**: [Development approach]
- **Output**: [What the project produces]

---

## 🚀 IMMEDIATE PROJECT SETUP

### **Step 1: Environment Creation (First 10 minutes)**
```bash
# Create project directory
mkdir [project-directory-name]
cd [project-directory-name]

# [Tech-stack specific setup - examples below]

# For Python projects:
# python -m venv venv
# source venv/bin/activate  # On Windows: venv\Scripts\activate
# pip install [core-dependencies]

# For Node.js projects:
# npm init -y
# npm install [core-dependencies]

# For other tech stacks:
# [Custom setup commands]

# Create project structure
mkdir -p {[core-directories]}
mkdir -p session-logs

# Initialize version control
git init
echo "[temp-files]" > .gitignore
echo "[output-files]" >> .gitignore
echo "[cache-files]" >> .gitignore
```

### **Step 2: Project Structure Creation**
```bash
# Create core project files
touch [core-source-files]

# Create directory for existing code if applicable
mkdir -p existing-code

# Project tracking files
touch PROJECT-STATUS-TRACKER.md
touch session-logs/session-$(date +%Y%m%d)-project-initialization.md
```

### **Step 3: Verification Test**
```bash
# [Project-specific verification script]
cat > examples/setup_verification.[ext] << 'EOF'
[Setup verification code - test that core dependencies work]
EOF

[command-to-run-verification]
```

---

## 📋 SESSION MANAGEMENT PROTOCOLS

### **Session Recovery Protocol**
When starting any new session, use this command sequence:
```bash
# 1. Read current status
TodoRead

# 2. Read project status
Read PROJECT-STATUS-TRACKER.md

# 3. Read latest session log
Read session-logs/session-[LATEST_DATE]*.md

# 4. Check current working state
[project-specific-verification-command]
```

### **Session Log Template**
```markdown
# Session [Date]: [Project-Name] - [Focus Area]

## Session Objectives
- [ ] [Primary goal for this session]
- [ ] [Secondary goal]
- [ ] [Testing/validation goal]

## Environment Status
- **Development Environment**: [Status]
- **Last Successful Test**: [When verification last passed]
- **Current Working Branch**: [Git branch if using]
- **[Project-specific status]**: [Status]

## Work Completed
### [Timestamp] - [Task Name]
- **Files Modified**: [List]
- **[Project-specific output]**: [Description]
- **Testing Results**: [Pass/Fail/Pending]
- **Validation**: [Results]

## Current Status
- **[Core Component 1]**: [Status - working/broken/in progress]
- **[Core Component 2]**: [Status]
- **Integration**: [How components work together]
- **Blockers**: [Any issues preventing progress]

## Next Session Handoff
**Immediate Next Action**: [Specific next step]
**Validation Required**: [What needs testing/confirmation]
**Context Notes**: [Important info not to lose]
```

---

## 🔧 DEVELOPMENT RULES AND PROTOCOLS

### **Core Development Principles**

#### **1. [PROJECT-SPECIFIC VALIDATION REQUIREMENT]**
```[language]
# Every [key-function-type] must have [validation-requirement]
def [example-function]([parameters]):
    """[Function description]"""
    [implementation]
    
    # REQUIRED: [Validation requirement]
    if [validation-condition]:
        [validation-action]
    
    return [result]
```

#### **2. [PROJECT-SPECIFIC QUALITY REQUIREMENT]**
```[language]
# Every [component-type] must meet [quality-standard]
[example-quality-check]
```

#### **3. ITERATIVE DEVELOPMENT PATTERN**
```[language]
# Always build incrementally with testing
def development_cycle_example():
    """Standard development cycle for this project"""
    
    # Step 1: Minimal working version
    [basic-implementation]
    
    # Step 2: Add validation/visualization
    [validation-step]
    
    # Step 3: Add testing
    [testing-step]
    
    # Step 4: Integration
    [integration-step]
```

### **File Organization Rules**
```[language]
# [primary-module] - [description]
class [PrimaryClass]:
    def __init__(self):
        self.debug_mode = True  # Always start with debugging
        
    def [core-method](self, [parameters]):
        """[Method description] with validation"""
        [implementation]

# [secondary-module] - [description]
class [SecondaryClass]:
    def [core-method](self, [parameters]):
        """[Method description] with validation"""
        [implementation]
```

---

## 🎯 INITIAL DEVELOPMENT TASKS

### **Phase 1: [Phase Name] (Sessions 1-2)**
```markdown
## [Component/Area] Tasks
- [ ] [Specific task 1]
- [ ] [Specific task 2]
- [ ] [Specific task 3]
- [ ] [Specific task 4]

## Validation Requirements
- [ ] [Validation requirement 1]
- [ ] [Validation requirement 2]
- [ ] [Validation requirement 3]
- [ ] [Validation requirement 4]
```

### **Phase 2: [Phase Name] (Sessions 3-4)**
```markdown
## [Component/Area] Tasks
- [ ] [Specific task 1]
- [ ] [Specific task 2]
- [ ] [Specific task 3]
- [ ] [Specific task 4]

## Validation Requirements
- [ ] [Validation requirement 1]
- [ ] [Validation requirement 2]
- [ ] [Validation requirement 3]
- [ ] [Validation requirement 4]
```

### **Phase 3: [Phase Name] (Sessions 5-6)**
```markdown
## [Component/Area] Tasks
- [ ] [Specific task 1]
- [ ] [Specific task 2]
- [ ] [Specific task 3]
- [ ] [Specific task 4]

## Validation Requirements
- [ ] [Validation requirement 1]
- [ ] [Validation requirement 2]
- [ ] [Validation requirement 3]
- [ ] [Validation requirement 4]
```

---

## 🔧 CRITICAL DEVELOPMENT PROTOCOLS

### **Error Handling and Recovery**
```[language]
# Standard error handling pattern for this project
try:
    result = [risky-operation]()
    [validate-result](result)
    [project-specific-confirmation](result)
except [ProjectSpecificError] as e:
    [logger].error(f"[Error type] failed: {e}")
    [project-specific-debug-action](input_data, e)
    raise
except Exception as e:
    [logger].error(f"Unexpected error: {e}")
    [save-debug-state](locals())
    raise
```

### **Performance Monitoring**
```[language]
# Monitor performance of key functions
def performance_monitor(func):
    """Monitor performance of critical functions"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        [memory-monitoring-start]
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        [memory-monitoring-end]
        
        print(f"🔧 {func.__name__}: {end_time - start_time:.3f}s, "
              f"[memory-usage-format]")
        
        return result
    return wrapper
```

### **Version Control Strategy**
```bash
# Git workflow for this project
git add -A
git commit -m "Session [DATE]: [COMPONENT] - [WHAT_ACCOMPLISHED]

- [Validation type]: [STATUS]
- [Quality check]: [STATUS]
- [Integration status]: [STATUS]"

# Backup critical work
cp -r [core-directories] backups/[backup-name]-$(date +%Y%m%d-%H%M%S)/
```

---

## 🚀 SESSION STARTUP CHECKLIST

### **Every Session Must Begin With:**
```markdown
## Session Startup Protocol

### 1. Environment Validation (2 minutes)
- [ ] [Development environment activated]
- [ ] [Core dependencies available]
- [ ] [Project-specific tool available]
- [ ] [Test files available]

### 2. Context Recovery (5 minutes)
- [ ] TodoRead executed
- [ ] PROJECT-STATUS-TRACKER.md reviewed
- [ ] Latest session log read
- [ ] Current development target identified

### 3. [Project-Specific] Baseline Confirmation (3 minutes)
- [ ] Run latest working example
- [ ] Confirm [key-output] matches expected
- [ ] Verify [core-pipeline] if applicable
- [ ] Check [validation-system] passes

### 4. Work Planning (5 minutes)
- [ ] Current session objectives defined
- [ ] TodoWrite updated with specific tasks
- [ ] Success criteria established
- [ ] [Project-specific] plan prepared

### Total Startup Time: ~15 minutes
```

---

## 📊 SUCCESS METRICS AND VALIDATION

### **Technical Success Criteria**
```markdown
## Phase Completion Gates

### Phase 1: [Phase Name] Complete When:
- [ ] [Specific completion criterion 1]
- [ ] [Specific completion criterion 2]
- [ ] [Specific completion criterion 3]
- [ ] [Specific completion criterion 4]

### Phase 2: [Phase Name] Complete When:
- [ ] [Specific completion criterion 1]
- [ ] [Specific completion criterion 2]
- [ ] [Specific completion criterion 3]
- [ ] [Specific completion criterion 4]

### Project Complete When:
- [ ] [Overall completion criterion 1]
- [ ] [Overall completion criterion 2]
- [ ] [Overall completion criterion 3]
- [ ] [Overall completion criterion 4]
```

### **Quality Gates**
```[language]
# Code quality validation for this project
def validate_project_quality():
    """Validate current development state"""
    checks = {
        '[quality-aspect-1]': [test-function-1](),
        '[quality-aspect-2]': [test-function-2](),
        '[quality-aspect-3]': [test-function-3](),
        '[quality-aspect-4]': [test-function-4]()
    }
    
    all_passed = all(checks.values())
    
    for check, status in checks.items():
        status_symbol = "✅" if status else "❌"
        print(f"{status_symbol} {check}: {'PASS' if status else 'FAIL'}")
    
    return all_passed
```

---

## 🎯 FINAL PROJECT SETUP VERIFICATION

### **Complete Setup Validation Script**
```[language]
# Create this as: [validation-script-path]
"""
Complete project setup validation
Run this after initial setup to confirm everything is ready
"""

[validation-script-content]

if __name__ == "__main__":
    main()
```

---

## 🔄 NEXT SESSION RECOVERY INSTRUCTIONS

**When starting the next session, use this exact sequence:**

1. **Navigate to project directory**
2. **Activate development environment**: `[environment-activation-command]`
3. **Run session recovery**: Execute the session recovery command at the top of this file
4. **Validate environment**: `[validation-command]`
5. **Begin development**: Follow the phase-appropriate tasks from the task list above

**This file contains everything needed to resume productive work immediately in any new session.**

---

## 📝 CUSTOMIZATION NOTES

### **Required Customizations**
- Replace all `[PLACEHOLDER]` sections with project-specific information
- Adapt environment setup commands for your tech stack
- Modify validation requirements for your project type
- Customize development phases for your specific workflow
- Update file organization patterns for your architecture

### **Optional Enhancements**
- Add project-specific debugging tools
- Include domain-specific validation criteria
- Customize error handling for your use case
- Add specialized monitoring for your project type
- Include project-specific automation scripts

---

**Save this customized file as `[PROJECT-NAME]-INGESTION.md` in your project root directory.**