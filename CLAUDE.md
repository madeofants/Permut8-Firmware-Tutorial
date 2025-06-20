# Claude Code Memory

## Git Configuration
- SSH key for GitHub: `~/.ssh/ai_agent_key`
- To push changes: `GIT_SSH_COMMAND="ssh -i ~/.ssh/ai_agent_key" git push`
- The ai-agent key is located at `~/.ssh/ai_agent_key` and needs to be specified explicitly

## Development Commands
- Push to GitHub: `GIT_SSH_COMMAND="ssh -i ~/.ssh/ai_agent_key" git push`
- Standard git commands work normally, only push requires the SSH key specification

## Implementation Protocol
**CRITICAL RULE**: Never implement anything without a plan and explicit user approval
- Always create a plan first using TodoWrite
- Present the plan to the user
- Wait for explicit approval before proceeding
- No code changes or file modifications without permission
- Do not make decisions without user input - always ask for approval first
- Present options and recommendations, but let user choose the path forward

## Solution Strategy
**FOCUS ON ACHIEVABLE SOLUTIONS FIRST**: Always prioritize getting basic functionality working before adding complexity
- First plans should focus on "can our base goal be achieved?"
- Get the minimum viable solution working completely
- Only then iterate to add features, optimizations, or complexity
- Validate each step works before moving to the next level
- Simple working solution beats complex broken solution

## Session Continuity
**SAVE PROGRESS FREQUENTLY**: Always create session continuation guides for complex multi-phase work
- Create SESSION_CONTINUATION_GUIDE.md for any work spanning multiple sessions
- Update progress status between major tasks and phases
- Document current state, completed work, and immediate next actions
- Include key patterns, file references, and success criteria
- Ensure seamless continuation even after interruptions

## Project Structure
- Main documentation: `Permut8-Firmware-Tutorial.html`
- Documentation generator: `generate_documentation_html.py`
- Old backup files can be ignored (e.g., `Permut8-Firmware-Tutorial-OLD.html`)