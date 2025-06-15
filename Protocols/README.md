# Protocols Directory

This directory contains all project management, development, and quality assurance protocols used throughout the Permut8 Firmware Tutorial project.

## Directory Structure

### `active/` - Current Protocols
- **SESSION-START-PROTOCOL.md** - Session recovery and continuation guide
- **EXTRACTED-BUILD-PROCESSING-WORKFLOWS.md** - Build and processing workflows
- **EXTRACTED-DOCUMENTATION-STANDARDS.md** - Documentation quality standards
- **EXTRACTED-FILE-SAFETY-PROTOCOLS.md** - File safety and backup protocols
- **EXTRACTED-SESSION-MANAGEMENT-PROTOCOL.md** - Session management procedures

### `reference/` - Reference Protocols
- **AUDIT-QUALITY-FRAMEWORKS.md** - Quality audit frameworks and methodologies
- **BUILD-PROCESSING-WORKFLOWS.md** - Historical build processing documentation
- **FILE-SAFETY-PROTOCOLS.md** - Comprehensive file safety procedures
- **SESSION-MANAGEMENT-PROTOCOLS.md** - Session management reference
- **PROJECT-INGESTION-TEMPLATE.md** - Template for new project ingestion

### `archived/` - Historical Protocols
- Contains outdated or superseded protocols maintained for historical reference

## Usage

### For AI Sessions
Primary session start command:
```
read session docs to recover our progress: TodoRead + Read Protocols/active/SESSION-START-PROTOCOL.md + Read Documentation Project/active/COMPREHENSIVE-AUDIT-TASK-TRACKER.md + Read Documentation Project/active/DOCUMENTATION_STATUS_TRACKER.md + Task "find most recent session log"
```

### For Development Work
- Follow protocols in `active/` for current development standards
- Reference `reference/` for comprehensive methodology documentation
- Check `archived/` for historical context when needed

## Protocol Updates

When updating protocols:
1. Modify protocols in `active/` for current use
2. Move superseded protocols to `archived/` with clear naming
3. Update references in CLAUDE.md and project documentation
4. Document changes in session logs