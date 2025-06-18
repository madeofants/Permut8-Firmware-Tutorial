# PRE-COMMIT PROTOCOL FOR CLAUDE

**Purpose**: Standardized pre-commit validation and preparation process for Claude Code environment  
**Application**: Any documentation or development project requiring commit preparation  
**Environment**: Claude Code interactive sessions

---

## 🎯 PROTOCOL OVERVIEW

When user says **"run pre-commit"**, follow these 6 steps in order:

1. **Session Log** - Always create timestamped session documentation
2. **Archive Review** - Show files to be archived and get user approval  
3. **HTML Update** - Always regenerate HTML documentation
4. **README Update** - Always update README with current stats/timestamps
5. **Quality Check** - Always validate key files and count documentation
6. **Commit Summary** - Always create commit preparation report

**Key Principle**: Only file archiving requires approval - all other steps are safe operations

---

## 📋 STEP-BY-STEP PROTOCOL

### **Step 1: Session Log** ✅ ALWAYS
```markdown
File: project-archive/documentation-archives/session-history/session-logs/session-YYYY-MM-DD_HH-MM-SS-[description].md

Content Requirements:
- Date and timestamp
- Session type and objectives  
- Work completed this session
- Files modified
- Repository status
- Protocol compliance notes
```

### **Step 2: Archive Review** 🤔 APPROVAL REQUIRED
```bash
# Show files that would be archived
find "project-archive/documentation-archives/non-production" -name "*.md" -mtime +7

# Show temporary files
find . -name "*.bak" -o -name "*.tmp"

# Present list to user with details
# Get explicit approval before moving any files
# CRITICAL: Distinguish between audit files vs content files
```

**⚠️ CRITICAL SAFETY RULE**: 
- **Audit files**: Can be archived (gap analysis, session logs, progress tracking)
- **Content files**: Must be moved to active reference, NOT archived
- **Always ask user to review the list before proceeding**

### **Step 3: HTML Update** ✅ ALWAYS
```bash
cd project_root
python3 generate_documentation_html.py
# Verify output file size and success
```

### **Step 4: README Update** ✅ ALWAYS
```markdown
# Update file counts
# Add current session achievements  
# Update timestamps
# Add any critical content recovery notes
```

### **Step 5: Quality Check** ✅ ALWAYS (READ-ONLY)
```bash
# Count active documentation files
find "Documentation Project/active/content" -name "*.md" | wc -l

# Verify key files exist
- QUICKSTART.md
- core_language_reference.md  
- README.md
- generate_documentation_html.py

# Report any issues found
```

### **Step 6: Commit Summary** ✅ ALWAYS
```markdown
File: project-archive/session-logs/commit-summary-YYYY-MM-DD_HH-MM-SS.md

Content Requirements:
- Repository status
- Documentation file counts
- Session work summary
- Files modified list
- Git status
- Recommended commit message
- Next steps for staging and committing
```

---

## 🛡️ SAFETY PROTOCOLS

### **Prevention-First Principles**
1. **Never archive content files** - Always move to active reference
2. **Always preview archive candidates** - Let user see what would be moved
3. **Document all actions** - Comprehensive session logging required
4. **Verify file counts** - Ensure no unexpected losses
5. **Read-only validation** - Quality checks never modify files

### **Archive Decision Matrix**

| File Type | Location | Action |
|-----------|----------|--------|
| Audit reports | non-production/ | ✅ Archive (with approval) |
| Gap analysis | non-production/ | ✅ Archive (with approval) |
| Session logs | session-logs/ | ✅ Archive old ones (with approval) |
| Content files | non-production/ | ❌ MOVE to active reference |
| Tutorials | non-production/ | ❌ MOVE to user-guides/tutorials/ |
| Parameters | non-production/ | ❌ MOVE to reference/parameters/ |
| Advanced docs | non-production/ | ❌ MOVE to reference/advanced/ |

### **Content Recovery Protocol**
When content files are found in non-production:
1. **Stop archiving process**
2. **Identify content type** (tutorials, reference, parameters)
3. **Move to appropriate active location**
4. **Update README and file counts**
5. **Regenerate HTML to include rescued content**
6. **Document recovery in session log**

---

## 📊 SUCCESS METRICS

### **Quality Indicators**
- ✅ Session fully documented
- ✅ No content files lost to archive
- ✅ HTML documentation current
- ✅ README reflects accurate status
- ✅ All key files validated
- ✅ Commit preparation complete

### **File Count Tracking**
Always track and report:
- **Documentation files**: Before and after counts
- **Content rescued**: Files moved from non-production
- **Files archived**: Only audit/session files
- **HTML file size**: Verification of successful generation

---

## 🔄 ERROR HANDLING

### **If Archive Contains Content Files**
1. **STOP** - Do not proceed with archiving
2. **Categorize files** by type (tutorials, reference, etc.)
3. **Move to appropriate active locations**
4. **Update file counts and README**
5. **Archive only actual audit files**
6. **Document rescue operation**

### **If HTML Generation Fails**
1. **Report error** with specific details
2. **Continue with other steps**
3. **Note in commit summary** that HTML needs attention
4. **Do not block commit process**

### **If Quality Check Finds Issues**
1. **Report specific missing files**
2. **Continue with commit preparation**
3. **Flag issues in commit summary**
4. **Recommend resolution before commit**

---

## 📈 PROTOCOL COMPLIANCE

### **Session Management Integration**
This protocol follows session management guidelines:
- **Documentation-first**: Every action logged
- **Safety-focused**: Prevention of data loss
- **Quality-maintained**: Consistent validation
- **Continuity-enabled**: Complete context preservation

### **Customization Guidelines**
- **File paths**: Adjust for project structure
- **Archive criteria**: Modify age thresholds as needed
- **Quality checks**: Add project-specific validations
- **Commit messages**: Customize for project conventions

---

## 🚀 USAGE EXAMPLES

### **Standard Session**
```
User: "run pre-commit"
Claude: 
1. Creates session log ✅
2. Shows archive candidates, gets approval ✅
3. Regenerates HTML ✅ 
4. Updates README ✅
5. Validates quality ✅
6. Creates commit summary ✅
```

### **Content Recovery Session**
```
User: "run pre-commit"
Claude:
1. Creates session log ✅
2. Finds content files in non-production
3. STOPS archiving process
4. Moves content to active reference
5. Updates README with rescue info
6. Regenerates HTML with rescued content
7. Validates increased file count
8. Documents recovery in commit summary
```

---

**Remember**: This protocol ensures safe, comprehensive commit preparation while preventing loss of valuable content. Always prioritize content preservation over administrative convenience.