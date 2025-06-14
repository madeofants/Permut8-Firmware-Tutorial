# Session Continuity Protocol

**Purpose**: Maintain project progress across session interruptions without manual closing procedures

## Auto-Save Requirements for Session Interruptions

### 🔄 **After Every Major Task Completion**
When completing any significant work unit, automatically update these tracking systems:

#### 1. Update TodoWrite Status
```markdown
// Immediately after completing a task
TodoWrite - Mark task as "completed"
TodoWrite - Update next task to "in_progress" if continuing
```

#### 2. Document Progress in Session Log
**File**: Create/update current session log in `session-logs/`
**Naming**: `session-[DATE]-[brief-description].md`

**Required Information**:
```markdown
## Session Progress: [Date] - [Brief Description]

### Tasks Completed This Session
- [X] Specific task with file names and outcomes
- [X] Another completed task with results

### Current Task Status  
- **In Progress**: [Specific current task]
- **Next**: [Specific next action when resuming]

### Critical Findings
- [Any syntax issues discovered]
- [Any significant problems found]
- [Any pattern discoveries]

### Files Modified
- `path/to/file.md` - [Brief description of changes]
- `another/file.md` - [Brief description of changes]

### Session Interruption Handoff
**If session interrupted, resume with**: [Specific next action]
**Context needed**: [Any important context for continuation]
**Tools needed**: [Specific tools or files to access first]
```

### 🔄 **After Every Minor Task/File**
For smaller work units (individual file audits, single fixes):

#### Quick Progress Note
Add brief progress note to current session log:
```markdown
### In-Progress Updates
- ✅ [File]: [Brief status] - [Timestamp]
- 🔄 [File]: [Current work] - [Timestamp]
```

## Session Recovery Protocol

### 🚀 **Starting Any New Session**

#### Session Ingestion Command (Use this first):
```
read session docs to recover our progress: TodoRead + Read Documentation Project/active/COMPREHENSIVE-AUDIT-TASK-TRACKER.md + Read Documentation Project/active/DOCUMENTATION_STATUS_TRACKER.md + Read Documentation Project/active/ai-context/session-start.md + Task "find most recent session log"
```

#### Step 1: Context Loading (MANDATORY)
1. **Read** `ai-context/session-start.md` completely
2. **Read** `ai-context/documentation-meta-analysis.md` for full strategy
3. **Use TodoRead** to check current task status
4. **Find** most recent session log in `session-logs/`

#### Step 2: Orientation Check
Verify understanding of:
- **Current phase** (Phase 1, 2, or 3)
- **Current directory** being worked on
- **Specific task in progress**
- **Last completed work**

#### Step 3: Immediate Action Determination
Based on todo status and session log:
- **If task marked "in_progress"**: Continue where left off
- **If task marked "completed"**: Start next pending task
- **If unclear**: Ask user for guidance

## Crash Recovery Template

### 🔧 **For Unexpected Session Termination**

When resuming after crash/interruption, immediately create this status check:

```markdown
## Session Recovery Check - [Date]

### Context Verification
- [ ] Read session-start.md rules
- [ ] Read documentation-meta-analysis.md strategy  
- [ ] Checked TodoRead for current status
- [ ] Found last session log: `[filename]`

### Status Assessment
**Last known task**: [From todo or session log]
**Last modified files**: [From session log if available]
**Estimated progress**: [X% through current phase]

### Recovery Action
**Resuming with**: [Specific action to take]
**Verification needed**: [Any work that needs to be checked]

### Continuation Plan
1. [First specific action]
2. [Second specific action]  
3. [Pattern for moving forward]
```

## Automated Continuity Markers

### 📍 **After Each File Audit**
```markdown
// Add to current session log
- ✅ `filename.md` - [KEEP/FIX/NEEDS_REWRITE] - Issues: [brief list]
```

### 📍 **After Each Directory Completion**
```markdown
// Update session log
### [Directory] Directory Complete
**Files processed**: X/Y
**Major issues**: [Summary]
**Next directory**: [Next target]
**Phase status**: [X% complete]
```

### 📍 **After Each Fix Implementation**
```markdown
// Update session log  
### Fix Applied: [File]
**Issue**: [What was wrong]
**Solution**: [What was fixed]
**Verification**: [How it was tested]
**Status**: [Ready for HTML / Needs more work]
```

## Session Log Organization

### 📂 **File Naming Convention**
```
session-logs/
├── session-2025-01-06-phase1-reference-fixes.md
├── session-2025-01-06-phase1-architecture-fixes.md  
├── session-2025-01-07-phase2-assembly-consolidation.md
└── session-2025-01-07-phase3-final-polish.md
```

### 📋 **Session Log Template**
```markdown
# Session [Date]: [Phase] - [Focus Area]

## Objective
[What this session is trying to accomplish]

## Starting Status
- **Phase**: [1/2/3]  
- **Directory**: [Current focus]
- **Prior work**: [What was completed before this session]

## Work Completed
### [Timestamp] - [Task Name]
- **Action**: [What was done]
- **Files**: [What was modified]
- **Result**: [Outcome]

## Current Status
- **Task in progress**: [Current todo item]
- **Files modified this session**: [List]
- **Next action**: [Specific next step]

## Handoff Notes
**For next session**: [Instructions for continuation]
**Critical context**: [Important info not to lose]
**Verification needed**: [Any work to double-check]
```

## Key Principles

### ⚡ **Speed Over Perfection**
- Quick updates better than no updates
- Brief notes better than detailed documentation  
- Continuous progress tracking over perfect session logs

### 🎯 **Essential Information Only**
- Current task status
- Files being worked on
- Major issues discovered
- Next specific action

### 🔄 **Fail-Safe Recovery**
- Always possible to determine where work left off
- Always possible to verify what was completed
- Always possible to continue without losing context

---

**Remember**: The goal is continuity, not perfect documentation. Quick updates after each task keep the project moving forward even with session interruptions.