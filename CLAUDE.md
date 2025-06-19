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

## Project Structure
- Main documentation: `Permut8-Firmware-Tutorial.html`
- Documentation generator: `generate_documentation_html.py`
- Old backup files can be ignored (e.g., `Permut8-Firmware-Tutorial-OLD.html`)