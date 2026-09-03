---
name: chushop-ai-engineer
description: Implement, debug, test, or review backend and frontend work for the ChủShop AI Money Brain SaaS. Use for tasks in this repository; avoid activating for unrelated projects.
---

# ChủShop AI Engineer

Read the repository `AGENTS.md` first. Then read only the relevant part of `WORKFLOW.md` and related source/tests.

Classify work as backend, frontend, or full-stack. For full-stack work, complete the backend API contract, backend implementation, and backend tests before the frontend API client, feature UI, and checks.

For backend work, use FastAPI, SQLAlchemy 2.x, Pydantic, Alembic, PostgreSQL, and Pytest. Preserve Router → Service → Repository → Database, tenant-scope every business resource through `BusinessMember`, avoid floats for authoritative money, and test business/financial rules plus cross-tenant access.

For frontend work, use Next.js, TypeScript, Tailwind, shadcn/ui patterns, TanStack Query, and Zod. Preserve Page → Feature → Hook → API Client → Backend, keep server state in TanStack Query, centralize HTTP calls, use Vietnamese UI text with English identifiers, and provide responsive loading/error/empty states.

Python is authoritative for financial values; LLMs explain and the frontend displays. Future sales items must snapshot historical cost in `cost_price_snapshot`.

For every task: inspect, plan briefly, implement, run targeted checks, review the diff, and report concisely. Avoid repository-wide scanning, unrelated refactors, speculative architecture, and future-scope implementation. Never claim a check passed unless it ran.
