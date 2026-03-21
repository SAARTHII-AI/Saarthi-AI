# Agent workflow — Saarthi-AI (default playbook)

Use this as the **default playbook** for iterative development in this repo. Agents should align behavior with **`.cursor/rules/saarthi-agent-workflow.mdc`** (same rules, Cursor-native).

---

## Workflow orchestration

### 1. Plan mode default
- Enter **plan mode** for non-trivial work: **3+ steps**, unclear requirements, or multiple valid designs.
- If execution diverges or blockers appear, **stop and re-plan** instead of piling on fixes.
- Use planning for **verification** steps, not only implementation.
- Prefer **detailed specs** early to reduce ambiguity.

### 2. Subagent strategy
- Use **subagents / parallel exploration** to keep the main context small.
- Offload **research, codebase exploration, and parallel analysis** when it reduces risk or wall-clock time.
- Prefer **one focused task per subagent** (clear input/output).

### 3. Self-improvement loop
- After **any user correction**, append a concrete bullet to **`tasks/lessons.md`** (pattern + fix).
- Turn recurring lessons into **checklist habits** for the next session.

### 4. Verification before done
- **Never** mark work complete without **proof**: tests, smoke checks, or demonstrated behavior.
- When relevant, compare **before/after** behavior and skim **logs** for hidden errors.
- Ask: *Would this pass a careful code review?*

### 5. Demand elegance (balanced)
- For non-trivial changes, pause once: *Is there a simpler or clearer approach?*
- If a fix feels hacky, consider rewriting the **minimal elegant** version—without gold-plating trivial edits.

### 6. Autonomous bug fixing
- On failures: **diagnose → fix → re-run** tests; avoid asking the user to debug unless blocked on **secrets, access, or product decisions**.

---

## Task management

1. **Plan first** — Outline approach in **`tasks/todo.md`** with checkable items.
2. **Verify plan** — Check constraints: deploy targets (Vercel/SAM), **env vars**, API limits, **offline fallback**.
3. **Track progress** — Keep todos honest; close or split when scope creeps.
4. **Document blockers** — Use **`tasks/lessons.md`** or **`tasks/todo.md`** for follow-ups.

---

## Core principles

- **Simplicity first** — Smallest change that meets the goal; readable over clever.
- **No laziness** — Root cause, not permanent “TODO” band-aids (unless explicitly agreed).
- **Minimal impact** — Touch only what’s necessary; avoid unrelated refactors in the same change.

---

## Project-specific logic (be aware of all paths)

### Dependencies
- **Canonical file**: repo root **`requirements.txt`**. **`backend/requirements.txt`** only **mirrors** it via `-r ../requirements.txt` — **edit root first**, never duplicate pins in `backend/`.

### Runtime behavior
- **Online path**: Azure OpenAI + optional Bright Data SERP when configured; **failures must fall back** to local keyword/template answers (`OFFLINE_ONLY`, missing keys, HTTP errors).
- **Tests**: Run **`cd backend && pytest`** after backend changes; don’t assert exact translated scheme names when responses are localized.

### Secrets & config
- **App secrets**: Prefer **`.env`** (gitignored) + **`.env.example`** placeholders.
- **MCP**: `.mcp.json` / `.cursor/mcp.json` may contain Bright Data tokens for IDE tooling — **treat as sensitive**; rotate if leaked.

### Docker / SAM
- **App Runner / generic Docker**: build from **repo root**: `docker build -f backend/Dockerfile .`
- **Lambda (SAM)**: `template.yaml` uses **root** `requirements.txt` in the image (see `backend/Dockerfile.lambda`).
