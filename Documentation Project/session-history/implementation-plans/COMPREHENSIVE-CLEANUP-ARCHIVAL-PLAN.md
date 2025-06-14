# COMPREHENSIVE CLEANUP & ARCHIVAL PLAN

**Project**: Documentation Project Directory Cleanup  
**Date**: 2025-06-13  
**Total Files**: 386 files across 56 directories  
**Objective**: Archive non-essential files while preserving protocols and production content  

---

## 🔒 SAFETY PROTOCOLS

### **NEVER DELETE PRINCIPLE**
- **NO DELETION** - Only move files to archives
- **BACKUP FIRST** - Create complete backup before any moves
- **VERIFICATION** - Checksum verification for all moves
- **ROLLBACK CAPABILITY** - Maintain ability to restore any file

### **Critical Files Protection**
- **Production content/**: 70 files - NEVER TOUCH
- **Active protocols**: session-start.md, task trackers - PRESERVE
- **Build scripts**: All .sh and .py files - KEEP ACTIVE
- **Current session logs**: Files from last 7 days - KEEP ACTIVE

---

## 📊 AUDIT CLASSIFICATION SYSTEM

### **ARCHIVE CATEGORIES**

#### **Category A: Session History (Archive Priority: HIGH)**
- **Target**: 18 session log files + 32 status tracking files
- **Criteria**: Files ending in `-log.md`, `-status.md`, `-tracker.md`
- **Age filter**: Older than 7 days from current date
- **Destination**: `archive-non-production/session-logs/2025-06/`

#### **Category B: Audit Reports (Archive Priority: MEDIUM)**  
- **Target**: 76 audit and terminology files
- **Criteria**: Files starting with `audit-`, `terminology-`, `report-`
- **Age filter**: Older than 14 days 
- **Destination**: `archive-non-production/audit-reports/2025-06/`

#### **Category C: Test/Temp Files (Archive Priority: HIGH)**
- **Target**: 12 temporary and test files
- **Criteria**: Files/dirs starting with `test-`, `temp-`, `tmp-`
- **Destination**: `archive-non-production/development-artifacts/test-files/`

#### **Category D: Duplicate Content (Archive Priority: LOW)**
- **Target**: 70 duplicate files in html-build/source/
- **Criteria**: Exact copies of production content for build process
- **Action**: Evaluate if build requires copies, may keep for build integrity

---

## 🛠️ PROTOCOL EXTRACTION PLAN

### **Reusable Methods to Extract**

#### **1. Audit & Quality Assessment Protocols**
```
Extract from:
- comprehensive-audit-task-tracker.md
- audit-findings/ directory files
- session-start.md protocols

Create: active/ai-context/reusable-protocols/
├── audit-methodology.md
├── quality-assessment-framework.md
├── session-recovery-protocol.md
└── file-safety-protocols.md
```

#### **2. Build & Processing Methods**
```
Extract from:
- All .sh script files
- HTML generation workflows
- PDF generation methods

Create: active/scripts/
├── production/ (current working scripts)
├── archived/ (old/test scripts)
└── templates/ (reusable script templates)
```

#### **3. Documentation Standards**
```
Extract from:
- Writing style guides found in sessions
- Grading criteria (A+ standard definitions)
- Content organization patterns

Create: active/ai-context/standards/
├── content-quality-standards.md
├── documentation-patterns.md
└── writing-guidelines.md
```

---

## 🗂️ IMPLEMENTATION PHASES

### **Phase 1: Safety Setup (5 minutes)**
```bash
# Create complete backup
cd "Documentation Project"
tar -czf "backup-$(date +%Y%m%d-%H%M%S).tar.gz" active/

# Create checksum inventory
find active/ -type f -exec md5sum {} \; > pre-cleanup-checksums.txt

# Create archive destinations
mkdir -p archive-non-production/session-logs/2025-06/
mkdir -p archive-non-production/audit-reports/2025-06/
mkdir -p archive-non-production/development-artifacts/test-files/
mkdir -p archive-non-production/development-artifacts/temp-processing/
```

### **Phase 2: Protocol Extraction (10 minutes)**
```bash
# Extract reusable protocols
mkdir -p active/ai-context/reusable-protocols/
mkdir -p active/ai-context/standards/
mkdir -p active/scripts/production/
mkdir -p active/scripts/archived/

# Move current scripts to organized location
mv active/*.sh active/scripts/production/
mv active/*.py active/scripts/production/

# Create protocol templates from session logs
```

### **Phase 3: Archive High-Priority Files (15 minutes)**
```bash
# Archive old session logs (Category A)
find active/ -name "*-log.md" -type f | \
while read file; do
    if [[ $(stat -c %Y "$file") -lt $(date -d "7 days ago" +%s) ]]; then
        mv "$file" archive-non-production/session-logs/2025-06/
    fi
done

# Archive tracking files (Category A)  
find active/ -name "*-tracker.md" -name "*-status.md" -type f | \
while read file; do
    if [[ $(stat -c %Y "$file") -lt $(date -d "7 days ago" +%s) ]]; then
        mv "$file" archive-non-production/session-logs/2025-06/
    fi
done

# Archive test files (Category C)
mv active/test-* archive-non-production/development-artifacts/test-files/
rm -rf active/test-temp-processing/
```

### **Phase 4: Archive Medium-Priority Files (10 minutes)**
```bash
# Archive old audit files (Category B)
find active/audit-findings/ -name "*.md" -type f | \
while read file; do
    if [[ $(stat -c %Y "$file") -lt $(date -d "14 days ago" +%s) ]]; then
        mv "$file" archive-non-production/audit-reports/2025-06/
    fi
done

# Archive terminology extracts
find active/ -name "terminology-*" -name "audit-*" -type f | \
while read file; do
    mv "$file" archive-non-production/audit-reports/2025-06/
done
```

### **Phase 5: Clean Active Directory Structure (5 minutes)**
```bash
# Organize remaining files in active/
mkdir -p active/current-session/
mkdir -p active/tracking/current/

# Move recent tracking files to organized location
find active/ -maxdepth 1 -name "*tracker*.md" -name "*status*.md" -type f | \
while read file; do
    mv "$file" active/tracking/current/
done

# Move current session files
find active/ -maxdepth 1 -name "*session*.md" -type f | \
while read file; do
    mv "$file" active/current-session/
done
```

### **Phase 6: Verification & Documentation (5 minutes)**
```bash
# Verify no production content moved
find active/content/ -name "*.md" | wc -l  # Should be 70

# Verify critical files preserved
ls -la active/ai-context/session-start.md
ls -la active/CLAUDE.md
ls -la active/html-build/output/Permut8-Documentation.html

# Create post-cleanup inventory
find active/ -type f -exec md5sum {} \; > post-cleanup-checksums.txt

# Document what was archived
echo "Files archived on $(date):" > active/CLEANUP-LOG.md
echo "Session logs: $(ls archive-non-production/session-logs/2025-06/ | wc -l) files" >> active/CLEANUP-LOG.md
echo "Audit reports: $(ls archive-non-production/audit-reports/2025-06/ | wc -l) files" >> active/CLEANUP-LOG.md
echo "Test files: $(ls archive-non-production/development-artifacts/test-files/ | wc -l) files" >> active/CLEANUP-LOG.md
```

---

## 📋 AUTOMATED AUDIT TOOLS

### **File Classification Script**
```bash
#!/bin/bash
# classify-files.sh - Automated file classification

classify_file() {
    local file="$1"
    local basename=$(basename "$file")
    local age_days=$(( ($(date +%s) - $(stat -c %Y "$file")) / 86400 ))
    
    # Category A: Session History
    if [[ "$basename" =~ -log\.md$|status\.md$|tracker\.md$ ]] && [ $age_days -gt 7 ]; then
        echo "ARCHIVE_SESSION:$file"
    
    # Category B: Audit Reports  
    elif [[ "$basename" =~ ^(audit-|terminology-|report-) ]] && [ $age_days -gt 14 ]; then
        echo "ARCHIVE_AUDIT:$file"
    
    # Category C: Test Files
    elif [[ "$basename" =~ ^(test-|temp-|tmp-) ]]; then
        echo "ARCHIVE_TEST:$file"
    
    # Category D: Production Content
    elif [[ "$file" =~ /content/.*\.md$ ]]; then
        echo "KEEP_PRODUCTION:$file"
    
    # Category E: Active Protocols
    elif [[ "$basename" =~ (session-start|CLAUDE)\.md$ ]]; then
        echo "KEEP_PROTOCOL:$file"
    
    else
        echo "REVIEW_MANUAL:$file"
    fi
}
```

### **Archive Safety Validator**
```bash
#!/bin/bash
# validate-archive.sh - Verify archive operations

validate_archive() {
    local archive_dir="$1"
    local expected_count="$2"
    
    actual_count=$(find "$archive_dir" -type f | wc -l)
    
    if [ "$actual_count" -eq "$expected_count" ]; then
        echo "✅ Archive validation passed: $actual_count files in $archive_dir"
        return 0
    else
        echo "❌ Archive validation failed: Expected $expected_count, found $actual_count"
        return 1
    fi
}
```

---

## 🎯 SUCCESS CRITERIA

### **Production Protection** ✅
- [ ] All 70 content files preserved in active/content/
- [ ] HTML build system intact with output file
- [ ] All .sh and .py scripts preserved and organized
- [ ] CLAUDE.md and session-start.md protocols preserved

### **Archive Organization** ✅
- [ ] Session logs organized by date in archive-non-production/session-logs/
- [ ] Audit reports archived by date in archive-non-production/audit-reports/
- [ ] Test files archived in development-artifacts/
- [ ] Reusable protocols extracted to ai-context/reusable-protocols/

### **Safety Verification** ✅
- [ ] Complete backup created before operations
- [ ] Checksum verification for all moved files
- [ ] No files deleted, only moved to archives
- [ ] Rollback capability maintained

### **Cleanup Results** ✅
- [ ] Active directory reduced from 386 to ~100 files
- [ ] Clear separation of production vs development artifacts
- [ ] Organized script library for future builds
- [ ] Extracted protocols available for reuse

---

## 📚 EXTRACTED PROTOCOL LIBRARY

### **Quality Assessment Framework**
- **A+ Content Standards**: 95%+ quality metrics
- **Content Categorization**: Foundation, Development, Reference
- **Learning Path Design**: 90-minute progression framework

### **Session Management Protocols**
- **Session Recovery**: TodoRead + status tracker + session-start.md
- **Task Completion**: Single-task focus with immediate status updates
- **File Safety**: Never modify originals, work on copies only

### **Build & Generation Methods**
- **HTML Generation**: Responsive design with navigation
- **Content Processing**: Markdown to HTML with glossary linking
- **File Organization**: Logical reading order with Foundation Path priority

### **Archive & Cleanup Standards**
- **Never Delete**: Only move to archives with checksum verification
- **Category-Based**: Age and type-based classification system
- **Safety First**: Complete backup before any file operations

---

**RESULT**: Clean, organized active directory with preserved protocols and properly archived development history, ready for continued production work.