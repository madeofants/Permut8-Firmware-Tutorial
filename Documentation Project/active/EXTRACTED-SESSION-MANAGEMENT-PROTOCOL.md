# SESSION MANAGEMENT PROTOCOL

**Purpose**: Reusable framework for managing complex documentation projects across multiple sessions  
**Extracted From**: Session-start.md, session-continuity-protocol.md, and SESSION-RECOVERY-GUIDE.md  
**Application**: Any multi-session documentation or development project requiring continuity

---

## 🔄 CORE SESSION MANAGEMENT PRINCIPLES

### **1. PREVENTION-FIRST APPROACH**
- **Never delete without explicit permission** - Distinguish between content vs infrastructure
- **Always ask before major edits** - Present detailed plans and wait for approval
- **Historical records are sacred** - Session logs and protocol documents preserve project knowledge
- **Major changes require approval protocol** - Bulk changes, structural reorganization, file deletion

### **2. AUTO-SAVE REQUIREMENTS**
Update tracking systems after every major task completion:

#### **Immediate Task Completion Actions**
```markdown
// After completing any significant work unit:
1. TodoWrite - Mark task as "completed"
2. TodoWrite - Update next task to "in_progress" if continuing
3. Document progress in current session log
4. Add critical findings or patterns discovered
```

#### **Session Log Requirements**
- **File naming**: `session-[DATE]-[brief-description].md`
- **Required information**: Tasks completed, current status, critical findings, files modified, handoff instructions
- **Update frequency**: After every major task, brief notes after minor tasks

### **3. SESSION RECOVERY PROTOCOL**

#### **Universal Session Ingestion Command**
```
read session docs to recover progress: TodoRead + Read [PROJECT_STATUS_TRACKER] + Read [SESSION_START_GUIDE] + Read [LATEST_SESSION_LOG] + Task "find most recent session log"
```

#### **Mandatory Startup Checklist**
1. ✅ Read session-start guide completely
2. ✅ Read project meta-analysis for full strategy  
3. ✅ Use TodoRead to check current task status
4. ✅ Find and read most recent session log
5. ✅ Verify current working directory location
6. ✅ Understand what work was completed in previous sessions
7. ✅ Identify the specific next action to take
8. ✅ Never delete files without explicit user permission

### **4. CRASH RECOVERY TEMPLATE**
```markdown
## Session Recovery Check - [Date]

### Context Verification
- [ ] Read session-start rules
- [ ] Read project strategy document
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

---

## 📋 TASK MANAGEMENT FRAMEWORK

### **TodoWrite Integration Requirements**
1. **Use TodoWrite extensively** for all task planning and tracking
2. **Mark todos as completed IMMEDIATELY** after finishing tasks
3. **Only have ONE task in_progress** at any time  
4. **Complete existing tasks before starting new ones**

### **Task Completion Standards**
- **ONLY mark completed when FULLY accomplished**
- **If errors/blockers encountered, keep as in_progress**
- **When blocked, create new task describing what needs resolution**
- **Never mark completed if**: Tests failing, implementation partial, unresolved errors, missing dependencies

### **Task Breakdown Principles**
- Create specific, actionable items
- Break complex tasks into manageable steps
- Use clear, descriptive task names
- Include time estimates when possible

---

## 📊 PROGRESS TRACKING METHODOLOGY

### **Continuous Progress Markers**

#### **After Each File/Component**
```markdown
- ✅ `filename.md` - [STATUS] - Issues: [brief list] - [timestamp]
```

#### **After Each Directory/Section**
```markdown
### [Section] Directory Complete
**Files processed**: X/Y
**Major issues**: [Summary]
**Next target**: [Next section]
**Phase status**: [X% complete]
```

#### **After Each Fix Implementation**
```markdown
### Fix Applied: [File]
**Issue**: [What was wrong]
**Solution**: [What was fixed]  
**Verification**: [How it was tested]
**Status**: [Ready for production / Needs more work]
```

### **Session Log Organization**

#### **File Naming Convention**
```
session-logs/
├── session-[DATE]-[phase]-[focus-area].md
├── session-[DATE]-[component]-[status].md
└── session-[DATE]-[deliverable]-[completion].md
```

#### **Session Log Template**
```markdown
# Session [Date]: [Phase] - [Focus Area]

## Objective
[What this session is trying to accomplish]

## Starting Status
- **Phase**: [Current phase]
- **Component**: [Current focus]
- **Prior work**: [What was completed before]

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

---

## 🔧 INTERRUPTION HANDLING PROTOCOL

### **Session Interruption Documentation**
When session is interrupted, document:
1. **Current Task Status**: Which todo item was in progress
2. **Files Completed**: Specific files audited and their status
3. **Critical Findings**: Any issues or patterns discovered
4. **Next Actions**: Specific next steps for continuation
5. **Context Notes**: Important information for session handoff

### **Emergency Protocols**

#### **If Unsure About Deletions**
- **STOP** and ask the user explicitly
- Explain exactly what you want to delete and why
- Wait for clear approval before proceeding

#### **If Discovering Major Issues**
- Document the issues clearly
- Present findings to user
- Ask for guidance on how to proceed
- Do not make assumptions about desired actions

---

## 🎯 QUALITY ASSURANCE INTEGRATION

### **Documentation Requirements Between Sessions**
1. **Session logs saved between major tasks**
2. **Progress tracking updated with current status**
3. **Comprehensive reports for major transformations**
4. **Todo lists maintained with current priorities**

### **Strategic Planning Integration**
- **Roadmap established** for all major phases
- **Priority evaluation** prepared for decision points
- **Time estimates updated** based on actual patterns
- **Quality standards maintained** throughout

---

## 📈 SUCCESS METRICS

### **Key Principles**
- **Speed Over Perfection**: Quick updates better than no updates
- **Essential Information Only**: Current task, files worked on, major issues, next action
- **Fail-Safe Recovery**: Always possible to determine where work left off

### **Success Indicators**
- **Zero context loss** between sessions
- **Smooth continuation** regardless of interruption timing
- **Complete audit trail** of all work performed
- **Consistent quality** maintained across sessions

---

## 🔄 ADAPTATION GUIDELINES

### **Customization for Different Projects**
1. **Adjust session log templates** for project-specific needs
2. **Modify todo categorization** based on work types
3. **Customize quality metrics** for domain requirements
4. **Adapt file naming conventions** for organizational standards

### **Scaling Considerations**
- **Small projects**: Simplified logging, basic todo tracking
- **Medium projects**: Full protocol implementation
- **Large projects**: Enhanced reporting, milestone tracking
- **Team projects**: Shared documentation standards, handoff protocols

---

**Remember**: The goal is continuity and progress, not perfect documentation. Consistent application of these patterns enables seamless project continuation regardless of session interruptions or team changes.