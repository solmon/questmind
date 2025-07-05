# Questmind Monorepo

This monorepo is managed with [Nx](https://nx.dev/) and supports both Python and Node.js/TypeScript projects.

## Structure

- `apps/api` – FastAPI backend (Python)
- `apps/web` – Next.js frontend (TypeScript/React)
- `packages/shared` – Shared Python code
- `packages/ui` – Shared JS/TS UI components

## Prerequisites

- [pnpm](https://pnpm.io/) for JS/TS dependencies
- [uv](https://github.com/astral-sh/uv) for Python dependencies
- [poethepoet](https://github.com/nat-n/poethepoet) for Python task running

## Install dependencies

```bash
pnpm install           # Install JS/TS dependencies
uv pip install -r requirements.txt  # (If you add a requirements.txt for Python shared deps)
```

## API (FastAPI)

- **Run locally:**
  ```bash
  poe serve
  ```
  (Runs `uvicorn apps.api.main:app --reload`)

- **Install Python deps:**
  ```bash
  uv pip install fastapi pydantic
  ```

## Web (Next.js)

- **Run locally:**
  ```bash
  pnpm --filter ./apps/web dev
  ```

- **Build:**
  ```bash
  pnpm --filter ./apps/web build
  ```

- **Preview production build:**
  ```bash
  pnpm --filter ./apps/web start
  ```

## Nx Monorepo Commands

- **Run all builds:**
  ```bash
  pnpm nx run-many -t build
  ```
- **See project graph:**
  ```bash
  pnpm nx graph
  ```

---

For more, see the individual app/package README files or the Nx documentation.