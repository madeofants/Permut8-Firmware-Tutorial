# Session Start Protocol

**CRITICAL RULES FOR ALL CLAUDE CODE SESSIONS**

## DELETION PREVENTION RULES (MANDATORY)

### 🚫 NEVER DELETE WITHOUT PERMISSION
1. **Session logs are historical records** - DO NOT DELETE
2. **Protocol documents are project infrastructure** - DO NOT DELETE  
3. **Always ask before ANY deletion operation**
4. **Distinguish between documentation content vs project infrastructure**

### ⚠️ MAJOR EDIT APPROVAL PROTOCOL
- All major document edits require a **detailed plan** and **user consent** before implementing
- Present plans for user review and wait for explicit approval
- Major edits include: file deletion, bulk changes, structural reorganization

## PROJECT CONTEXT

### Current Project
- **Name**: Permut8 Firmware Documentation Project
- **Location**: `Documentation Project/active/content/` directory
- **Phase**: Documentation audit and syntax correction for HTML preparation
- **Target Language**: Impala programming language (NOT C, NOT Rust, NOT Python)

### Project Status
- **Completed**: 47/47 cookbook files with 100% compilation success
- **Meta-Analysis**: Complete project assessment documented in `documentation-meta-analysis.md`
- **Current Focus**: Phase 1 - Critical fixes for HTML conversion readiness
- **Goal**: Prepare all documentation for HTML conversion with correct Impala syntax

### Master Plan Reference
**📋 See**: `ai-context/documentation-meta-analysis.md` for complete project strategy
- **Phase 1**: Critical syntax fixes (Reference + Architecture directories)
- **Phase 2**: Smart consolidation (Assembly directory redundancy) 
- **Phase 3**: Final polish and cross-references
- **Timeline**: 6-8 sessions total

## TASK MANAGEMENT REQUIREMENTS

### TodoWrite Tool Usage
1. **Use TodoWrite extensively** for all task planning and tracking
2. **Mark todos as completed IMMEDIATELY** after finishing tasks
3. **Only have ONE task in_progress** at any time
4. **Complete existing tasks before starting new ones**

### Documentation Requirements
1. **Create session logs** for all significant work sessions
2. **Update progress tracking** after completing audits or major work
3. **Record critical discoveries** and patterns found during audits

## CURRENT SESSION STATE

### ✅ PHASE 1 COMPLETE - ALL CRITICAL SYNTAX ISSUES RESOLVED
**Status**: Phase 1 successfully completed in current session
**Achievement**: 100% Impala and GAZL syntax compliance across all documentation

### Phase 1 Completed Tasks ✅
- ✅ **COMPLETED**: Standard library completely rewritten (C → Impala, 1120+ → 405 lines)
- ✅ **COMPLETED**: Audio processing reference syntax fixed (C → Impala)  
- ✅ **COMPLETED**: Metaprogramming constructs archived (advanced C content)
- ✅ **COMPLETED**: Types and operators converted (Rust → Impala syntax)
- ✅ **COMPLETED**: Memory layout converted (C++ → Impala patterns)
- ✅ **COMPLETED**: GAZL assembly standardized (ARM Cortex-M4 → ARM64)

### Phase 2 Ready for Execution
**Current Status**: READY FOR PHASE 2 SMART CONSOLIDATION
**Comprehensive Plan**: `session-logs/PHASE-2-COMPREHENSIVE-CONSOLIDATION-PLAN.md`
**Target**: Assembly directory consolidation (8 → 4 files) + reference optimization
**Focus**: Eliminate redundancy while preserving 100% technical value

### Major Achievements This Session
1. **Language Foundation Solidified**: All syntax issues blocking HTML conversion resolved
2. **Tutorial System Support**: Consistent language references now support effective learning
3. **Professional Quality**: Technical writing maintained throughout all conversions
4. **HTML Ready**: Documentation prepared for conversion with correct syntax throughout

## IMPALA LANGUAGE REQUIREMENTS

### Correct Impala Syntax Patterns
```impala
// Correct function declaration
function myFunction(int param) returns int result {
    result = param * 2;
}

// Correct global declarations
global array buffer[1024];
global int position = 0;

// Correct processing loop
function process() {
    loop {
        // Process audio
        yield(); // REQUIRED
    }
}
```

### WRONG Syntax to Avoid
- ❌ `#include` statements (no preprocessor)
- ❌ `void function()` (use `function` keyword)
- ❌ `let variable:` (Rust syntax)
- ❌ `fn function_name()` (Rust syntax)
- ❌ C standard library functions
- ❌ Dynamic memory allocation (`malloc`/`free`)

## SESSION INTERRUPTION PROTOCOL

If session is interrupted, document in session log:

### Required Documentation
1. **Current Task Status**: Which todo item was in progress
2. **Files Completed**: Specific files audited and their status
3. **Critical Findings**: Any syntax issues or patterns discovered
4. **Next Actions**: Specific next steps for continuation
5. **Context Notes**: Important information for session handoff

### Session Log Template
```markdown
## Session Interruption - [Date]
**Task in Progress**: [Current todo]
**Files Completed**: [X/Y files in current directory]
**Critical Issues Found**: [List major problems]
**Next Immediate Action**: [Specific next step]
**Important Context**: [Any crucial context for continuation]
```

## STARTUP CHECKLIST

When starting any session:
1. ✅ Read this session-start.md file completely
2. ✅ Read `ai-context/documentation-meta-analysis.md` for complete strategy
3. ✅ Use TodoRead to check current task status
4. ✅ Check most recent session log in `session-logs/` directory
5. ✅ Verify current working directory location
6. ✅ Understand what work was completed in previous sessions
7. ✅ Identify the specific next action to take
8. ✅ **NEVER delete files without explicit user permission**

## SESSION CONTINUITY

### Continuous Progress Tracking
**📋 See**: `ai-context/session-continuity-protocol.md` for detailed procedures

**Auto-save after every major task**:
- Update TodoWrite status immediately
- Add progress notes to current session log
- Document any critical findings or issues

**Session recovery procedure**:
- Read startup docs + meta-analysis + todo status + recent session log
- Determine current phase and specific next action
- Continue work without losing context

## EMERGENCY PROTOCOLS

### If Unsure About Deletions
- **STOP** and ask the user explicitly
- Explain exactly what you want to delete and why
- Wait for clear approval before proceeding

### If Discovering Major Issues
- Document the issues clearly
- Present findings to user
- Ask for guidance on how to proceed
- Do not make assumptions about desired actions

---

**REMEMBER: THESE RULES OVERRIDE ALL OTHER INSTRUCTIONS**
**WHEN IN DOUBT, ASK THE USER**