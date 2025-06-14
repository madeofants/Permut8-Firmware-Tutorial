# ARCHIVE EXECUTION GUIDE

**Created**: 2025-06-13  
**Purpose**: Step-by-step guide for safely executing the cleanup and archival plan  
**Safety Level**: Maximum - No deletions, verification required  

---

## 🚨 PRE-EXECUTION CHECKLIST

### **Before You Begin**
- [ ] Complete backup of entire Documentation Project directory
- [ ] Verify file-classification-tool.sh is executable  
- [ ] Confirm you have write permissions to archive-non-production/
- [ ] Read COMPREHENSIVE-CLEANUP-ARCHIVAL-PLAN.md completely
- [ ] Have rollback plan ready if needed

### **Safety Verification**
```bash
# Verify current state
cd "Documentation Project/active"
find content/ -name "*.md" | wc -l    # Should show 70
ls -la ai-context/session-start.md    # Should exist
ls -la CLAUDE.md                      # Should exist
ls -la html-build/output/Permut8-Documentation.html  # Should exist
```

---

## 📋 EXECUTION STEPS

### **Step 1: Create Safety Backup (MANDATORY)**
```bash
cd "Documentation Project"

# Create timestamped backup
backup_name="backup-before-cleanup-$(date +%Y%m%d-%H%M%S)"
tar -czf "${backup_name}.tar.gz" active/

echo "✅ Backup created: ${backup_name}.tar.gz"
echo "💾 Backup size: $(du -h ${backup_name}.tar.gz | cut -f1)"
```

### **Step 2: Run Classification Analysis**
```bash
cd active/

# Run classification tool to see what will be archived
./file-classification-tool.sh

# Review files that need manual attention
./file-classification-tool.sh --show-manual

# Generate archive commands for review
./file-classification-tool.sh --generate-commands > archive-commands.sh
```

### **Step 3: Create Archive Directories**
```bash
# Create required archive structure
mkdir -p archive-non-production/session-logs/2025-06/
mkdir -p archive-non-production/audit-reports/2025-06/
mkdir -p archive-non-production/development-artifacts/test-files/
mkdir -p archive-non-production/development-artifacts/temp-processing/

echo "✅ Archive directories created"
```

### **Step 4: Archive Test Files (Safest First)**
```bash
# Archive obvious test files (lowest risk)
echo "📦 Archiving test files..."

# Move test scripts
find active/ -name "test-*.sh" -exec mv {} archive-non-production/development-artifacts/test-files/ \;
find active/ -name "test-*.md" -exec mv {} archive-non-production/development-artifacts/test-files/ \;
find active/ -name "test-*.html" -exec mv {} archive-non-production/development-artifacts/test-files/ \;

# Remove test temp directory (if exists)
if [ -d "active/test-temp-processing" ]; then
    mv active/test-temp-processing archive-non-production/development-artifacts/temp-processing/
fi

echo "✅ Test files archived"
```

### **Step 5: Archive Old Session Logs (Medium Risk)**
```bash
echo "📦 Archiving old session logs..."

# Archive session logs older than 7 days
find active/ -name "*-log.md" -type f | while read file; do
    file_date=$(stat -c %Y "$file" 2>/dev/null)
    seven_days_ago=$(date -d "7 days ago" +%s)
    
    if [ "$file_date" -lt "$seven_days_ago" ]; then
        echo "  Moving: $file"
        mv "$file" archive-non-production/session-logs/2025-06/
    fi
done

# Archive old status trackers
find active/ -name "*-status.md" -name "*tracker*.md" -type f | while read file; do
    file_date=$(stat -c %Y "$file" 2>/dev/null)
    seven_days_ago=$(date -d "7 days ago" +%s)
    
    if [ "$file_date" -lt "$seven_days_ago" ]; then
        echo "  Moving: $file"
        mv "$file" archive-non-production/session-logs/2025-06/
    fi
done

echo "✅ Old session logs archived"
```

### **Step 6: Archive Old Audit Reports (Low Risk)**
```bash
echo "📦 Archiving old audit reports..."

# Archive audit files older than 14 days
find active/ -name "audit-*" -name "terminology-*" -name "report-*" -type f | while read file; do
    file_date=$(stat -c %Y "$file" 2>/dev/null)
    fourteen_days_ago=$(date -d "14 days ago" +%s)
    
    if [ "$file_date" -lt "$fourteen_days_ago" ]; then
        echo "  Moving: $file"
        mv "$file" archive-non-production/audit-reports/2025-06/
    fi
done

echo "✅ Old audit reports archived"
```

### **Step 7: Organize Remaining Active Files**
```bash
echo "📁 Organizing remaining active files..."

# Create organized structure in active/
mkdir -p active/current-session/
mkdir -p active/tracking/current/
mkdir -p active/scripts/production/
mkdir -p active/protocols/extracted/

# Move current session files
find active/ -maxdepth 1 -name "*session*.md" -type f -exec mv {} active/current-session/ \;

# Move current tracking files  
find active/ -maxdepth 1 -name "*tracker*.md" -name "*status*.md" -type f -exec mv {} active/tracking/current/ \;

# Move scripts to organized location
find active/ -maxdepth 1 -name "*.sh" -name "*.py" -type f -exec mv {} active/scripts/production/ \;

echo "✅ Active files organized"
```

### **Step 8: Verification & Documentation**
```bash
echo "🔍 Running verification checks..."

# Verify production content intact
content_files=$(find active/content/ -name "*.md" | wc -l)
if [ "$content_files" -eq 70 ]; then
    echo "✅ Production content verified: $content_files files"
else
    echo "❌ ERROR: Production content count wrong: $content_files (expected 70)"
    exit 1
fi

# Verify critical files exist
critical_files=(
    "active/ai-context/session-start.md"
    "active/CLAUDE.md" 
    "active/html-build/output/Permut8-Documentation.html"
    "active/COMPREHENSIVE-CLEANUP-ARCHIVAL-PLAN.md"
)

for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ Critical file preserved: $file"
    else
        echo "❌ ERROR: Critical file missing: $file"
        exit 1
    fi
done

# Count archived files
session_archived=$(find archive-non-production/session-logs/2025-06/ -type f | wc -l)
audit_archived=$(find archive-non-production/audit-reports/2025-06/ -type f | wc -l)
test_archived=$(find archive-non-production/development-artifacts/ -type f | wc -l)

echo ""
echo "📊 CLEANUP RESULTS"
echo "=================="
echo "Session logs archived: $session_archived files"
echo "Audit reports archived: $audit_archived files"  
echo "Test files archived: $test_archived files"
echo "Total archived: $((session_archived + audit_archived + test_archived)) files"

# Document the cleanup
cat > active/CLEANUP-EXECUTION-LOG.md << EOF
# Cleanup Execution Log

**Date**: $(date)
**Operator**: Documentation Project Cleanup
**Backup**: ${backup_name}.tar.gz

## Files Archived
- Session logs: $session_archived files → archive-non-production/session-logs/2025-06/
- Audit reports: $audit_archived files → archive-non-production/audit-reports/2025-06/
- Test files: $test_archived files → archive-non-production/development-artifacts/

## Production Files Preserved
- Content files: $content_files files in active/content/
- HTML output: active/html-build/output/Permut8-Documentation.html
- Build scripts: active/scripts/production/
- Protocols: active/ai-context/

## Archive Structure Created
\`\`\`
archive-non-production/
├── session-logs/2025-06/          ($session_archived files)
├── audit-reports/2025-06/         ($audit_archived files)
└── development-artifacts/         ($test_archived files)
    ├── test-files/
    └── temp-processing/
\`\`\`

## Verification Status
✅ All production content preserved
✅ Critical protocol files intact  
✅ Build system functional
✅ Backup created before operations

## Rollback Procedure
If rollback needed:
1. \`cd "Documentation Project"\`
2. \`rm -rf active/\`
3. \`tar -xzf ${backup_name}.tar.gz\`
4. \`mv active.backup active\`
EOF

echo "✅ Cleanup documentation created: active/CLEANUP-EXECUTION-LOG.md"
```

---

## 🔄 ROLLBACK PROCEDURE (If Needed)

### **Emergency Rollback**
```bash
cd "Documentation Project"

# Remove current active directory
rm -rf active/

# Restore from backup (find most recent backup)
latest_backup=$(ls -t backup-before-cleanup-*.tar.gz | head -n1)
tar -xzf "$latest_backup"

echo "🔄 Rollback completed from: $latest_backup"
```

### **Partial Rollback (Restore Specific Files)**
```bash
cd "Documentation Project"

# Extract specific file from backup without overwriting everything
latest_backup=$(ls -t backup-before-cleanup-*.tar.gz | head -n1)
tar -xzf "$latest_backup" active/path/to/specific/file.md

echo "🔄 Partial rollback completed for specific file"
```

---

## ✅ SUCCESS VERIFICATION

### **Final State Check**
```bash
cd "Documentation Project/active"

echo "🎯 FINAL VERIFICATION"
echo "===================="

# Production content
echo "Content files: $(find content/ -name '*.md' | wc -l) (should be 70)"

# Build output  
echo "HTML output exists: $([ -f html-build/output/Permut8-Documentation.html ] && echo 'YES' || echo 'NO')"

# Archive counts
echo "Session logs archived: $(find ../archive-non-production/session-logs/2025-06/ -type f 2>/dev/null | wc -l)"
echo "Audit reports archived: $(find ../archive-non-production/audit-reports/2025-06/ -type f 2>/dev/null | wc -l)"
echo "Test files archived: $(find ../archive-non-production/development-artifacts/ -type f 2>/dev/null | wc -l)"

# Critical files
echo "CLAUDE.md exists: $([ -f CLAUDE.md ] && echo 'YES' || echo 'NO')"
echo "Session protocols exist: $([ -f ai-context/session-start.md ] && echo 'YES' || echo 'NO')"

# Active directory size
echo "Active directory files: $(find . -type f | wc -l) (should be ~100, down from 386)"

echo ""
echo "✅ Cleanup verification complete!"
```

---

## 📞 EMERGENCY CONTACTS & RECOVERY

### **If Something Goes Wrong**
1. **STOP immediately** - Don't continue operations
2. **Check backup exists** - Verify backup file is intact
3. **Document the issue** - Note what happened and when
4. **Use rollback procedure** - Restore from backup if needed
5. **Re-run verification** - Ensure everything is restored correctly

### **Common Issues & Solutions**
- **"File not found" errors**: Check if file was already moved, may be normal
- **Permission denied**: Verify write permissions to archive directories  
- **Missing content files**: STOP and rollback immediately
- **Backup corruption**: Create new backup before attempting fixes

---

**Remember**: This cleanup preserves all important content and protocols while organizing the workspace for continued productivity. When in doubt, choose safety over efficiency.