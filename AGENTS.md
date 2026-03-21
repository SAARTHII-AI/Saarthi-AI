# Agent instructions

Follow **`tasks/agent-workflow.md`** (and **`.cursor/rules/saarthi-agent-workflow.mdc`**) for workflow orchestration, task habits, and **repo-specific logic** (dependencies, offline/online behavior).

- Capture post-correction patterns in **`tasks/lessons.md`**.
- Track multi-step work in **`tasks/todo.md`**.

## Dependencies

- **Canonical**: repo root **`requirements.txt`**.
- **`backend/requirements.txt`** only **mirrors** the root file via `-r ../requirements.txt` — **edit the root file first**; never duplicate pins in `backend/`.

## Runtime configuration

- Copy **`.env.example`** → **`.env`** and fill values locally. **`.env` is gitignored.**
- Backend loads env from `backend/.env` or the repo root `.env` (later file wins when both exist).

## Security

- If API keys leak (chat, logs, public repo), **rotate** them in Azure / Bright Data immediately.
- **MCP** (`.mcp.json`, `.cursor/mcp.json`) may contain Bright Data tokens for IDE tooling — **treat as sensitive.**
