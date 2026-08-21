# NLPT-Kiosk Agents

This document describes all AI agents available for the NLPT-Kiosk project, their purposes, trigger phrases, and how they work together.

## Knowledge Architecture

The project uses a **split-knowledge** system:

| File | Scope | Loaded By | Purpose |
|---|---|---|---|
| `.github/copilot-instructions.md` | Shared | All agents + general Copilot | Project overview, architecture, conventions, domain model summary — lightweight context for any task |
| `.github/agents/project-expert.agent.md` | Deep reference | project-expert agent | Full element tables, endpoint methods, helper details, frontend component tree, interfaces — the "reference manual" |

When an agent needs project knowledge, it loads from both files: shared context first (concise), then deep reference as needed. The git-sync-agent is responsible for keeping both up to date after code changes.

---

## Agent Index

| Agent | File | Purpose |
|---|---|---|
| **Project Expert** | `project-expert.agent.md` | General-purpose coding assistant with full project knowledge — handles any task |
| **Update Expert** | `update-expert.agent.md` | Analyzes git commits and updates both knowledge files to reflect current codebase state |
| **Update Changelog** | `update-changelog.agent.md` | Compares git commits against CHANGELOG, identifies missing user-facing entries |
| **Project Planner** | `project-planner.agent.md` | Plans features through chapter-based workflow with savepoint support and user approval gates |

---

## 1. Project Expert Agent

**File:** `.github/agents/project-expert.agent.md`  
**Description:** General-purpose expert AI assistant with deep knowledge of the NLPT-Kiosk project. Handles ANY task — coding, debugging, refactoring, adding features, writing tests, reviewing code, explaining concepts.

### When to Use
- Any coding task on this project
- Debugging issues across backend/frontend/infrastructure
- Refactoring or adding new features
- Explaining how any part of the system works
- Code review or architecture questions

### How It Works
Loads `.github/copilot-instructions.md` for shared context, then `.github/agents/project-expert.agent.md` for deep reference details (element tables, endpoint methods, helper descriptions, frontend component tree, TypeScript interfaces).

---

## 2. Update Expert Agent

**File:** `.github/agents/update-expert.agent.md`  
**Description:** Analyzes all commits on the current git branch and updates both knowledge files (`.github/copilot-instructions.md` and `.github/agents/project-expert.agent.md`) so they accurately reflect the current state of the codebase.

### Trigger Phrases
- "do your work"
- "analyze branch"
- "start"
- "go ahead"
- "sync agent knowledge"
- "update project-expert"
- Any similar instruction to analyze and update documentation

### Workflow Summary
1. **Determine version & baseline** — uses git tags for version, sync-baseline.md for last-synced commit
2. **Gather commits** — targeted diffs by category (elements, endpoints, helpers, frontend, infra)
3. **Analyze changes** — categorizes each change and routes it to the correct knowledge file using routing rules:

| Change Type | Destination | Rationale |
|---|---|---|
| Element classes (attributes/methods) | `project-expert` only | Deep reference detail |
| Endpoint classes (custom methods) | `project-expert` only | API contract detail |
| Helper files (function descriptions) | `project-expert` only | Implementation detail |
| Frontend components/services/interfaces | `project-expert` only | Component/service contract detail |
| Dependencies (requirements.txt / package.json) | Both files | Shared: tech stack; Expert: full list |
| Docker services / ports | Both files | Shared: architecture diagram; Expert: daemon details |
| Backend startup sequence | Both files | Shared: boot order summary; Expert: step-by-step |
| Frontend routes (app.routes.ts) | Both files | Shared: key routes table; Expert: full route table |
| Auth mechanism / API conventions | `copilot-instructions` only | Convention knowledge |
| Domain entities / relationships | Both files | Shared: summary; Expert: detail tables |
| HAProxy config | `copilot-instructions` only (unless new rewrite rules) | Architecture diagram update |
| Environment variables / settings | `copilot-instructions` only | Convention knowledge |

**Decision Algorithm:** Internal "how" → expert. Project "what" → shared. Both if needed.

4. **Apply updates** — edits both files, preserving unchanged content
5. **Report results** — commits analyzed, categories found, sections updated per file

### Important Constraints
- Only modifies knowledge files — never source code
- Uses git commands to gather information, never guesses
- Preserves overall structure and formatting of both files

---

## 3. Update Changelog Agent

**File:** `.github/agents/update-changelog.agent.md`  
**Description:** Compares all git commits since the last tagged release against the CHANGELOG and identifies any user-facing changes that are missing from the upcoming release notes.

### Trigger Phrases
- "start"
- "do your work"
- "start analyze"
- "review changelog"
- "check changelog"
- "what's missing in the changelog"
- Any similar instruction to review or compare the CHANGELOG

### Language Rule
**ALWAYS write the CHANGELOG and all output in English**, regardless of what language the user uses.

### Workflow Summary
1. **Determine versions** — finds last release tag via `git tag`, identifies upcoming version section in CHANGELOG
2. **Gather commits** — `git log <last_release_tag>..HEAD --oneline --no-merges`
3. **Analyze each commit** — categorizes as user-facing (feature/fix/improvement) or internal-only (tooling/docs/CI)
4. **Compare against CHANGELOG** — identifies missing entries
5. **Report findings** — lists gaps and suggests additions

### Change Categories
| Category | Include in CHANGELOG? | Section |
|---|---|---|
| New features / capabilities | Yes | "New Features" |
| Bug fixes | Yes | "Fixes/Improvements" |
| Internal-only (tooling, docs, CI) | No | — |

---

## 4. Project Planner Agent

**File:** `.github/agents/project-planner.agent.md`  
**Description:** Helps users plan, structure, and implement new features, fixes, or projects through a disciplined chapter-based workflow with savepoint support.

### Core Workflow

#### Phase 1: Planning
- Check for existing savepoints in `docs/dev/planning-session-*.md`
- Ask user to restore previous session or create new one
- Research codebase, break work into chapters, present plan
- **Wait for explicit approval** before any code changes

#### Phase 2: Savepoint Creation
- Write savepoint file documenting sessions rules, overview, chapters with plans/decisions/options, status table, open questions
- Present chapter overview to user

#### Phase 3: Chapter Implementation
- Implement one chapter at a time — only touch files directly related to that chapter
- Update savepoint after each chapter (mark done/partially done/not started)
- Present status overview and ask what's next

### Session Rules (Always Enforced)
- **NO FILE CHANGES during planning phase** — all work is discussion/planning until user explicitly gives permission
- After loading a saved checkpoint: list all chapters with status, ask where to continue — do not proceed without user selection
- **"Update the savepoint" exception:** Allowed — modify this file in-place (mark chapters done, add decisions)
- **"Implement a specific chapter" exception:** Allowed — modify files for that chapter only

### Savepoint Location
`docs/dev/planning-session-<session_name>.md`

---

## Agent Interaction Patterns

### Typical Workflows

**Adding a new feature:**
1. **Project Planner** → plan the feature, create savepoint, get user approval
2. **Project Expert** → implement chapter by chapter (or use planner's implementation phase)
| **Update Expert** → run after merge to update knowledge files with new code

**Preparing a release:**
| **Update Changelog** → compare commits against CHANGELOG, identify missing entries
| **Update Expert** → ensure knowledge files reflect the released state

**Debugging an issue:**
1. **Project Expert** → diagnose and fix (has full project context)
| **Update Expert** → run after fix to update documentation if relevant

### Agent Orchestration
Agents can invoke each other via the `agent` tool. For example:
- Project Planner can delegate implementation to Project Expert
- Git Knowledge Sync runs independently but its output feeds all other agents' knowledge

---

## File Locations

```
.github/agents/
├── update-changelog.agent.md    # Update Changelog Agent
├── update-expert.agent.md       # Update Expert Agent
├── project-expert.agent.md      # Project Expert Agent (deep reference)
├── project-planner.agent.md     # Project Planner Agent
├── update-expert-sync-baseline.md  # Last synced commit tracking data
└── AGENTS.md                    # ← You are here

.github/copilot-instructions.md   # Shared context
```
