# ChủShop AI Workflow

## Architecture and boundaries

```text
Next.js + TypeScript → REST → FastAPI + Python → PostgreSQL
```

The backend is authoritative for security, tenant access, business and financial logic, analytics, and AI orchestration. The frontend handles Vietnamese UI, interaction, and API presentation. It never accesses the database or calls LLM providers directly.

## Backend tasks

Use FastAPI, SQLAlchemy 2.x, Pydantic, Alembic, PostgreSQL, and Pytest. Follow Router → Service → Repository → Database. Keep routers thin, services responsible for business rules, repositories responsible for persistence, and Pydantic schemas responsible for API contracts.

Every business-owned operation follows User → BusinessMember → Business → Resource. Never trust a client business ID without membership verification. Store VND money as integers and use deterministic backend calculations.

Validate with targeted tests first, then formatting/linting and affected integration tests. Review authentication, validation, tenant isolation, secrets, and migrations.

## Frontend tasks

Use Next.js, TypeScript, Tailwind, shadcn/ui patterns, TanStack Query, and Zod. Follow Page → Feature → Hook → API Client → Backend. Routes belong in `app/`, feature logic in `features/`, shared UI in `components/`, and HTTP infrastructure in `lib/api/`.

Provide loading, error, empty, and pending states where applicable. Use Vietnamese UI text, English identifiers, and responsive layouts. Validate with lint, typecheck, affected tests, and a build when practical.

## Full-stack tasks

Work in this order: backend API contract, backend implementation, backend tests, frontend API client, frontend feature/UI, frontend checks.

## Task loop

1. Inspect `AGENTS.md`, this relevant section, related source, and tests.
2. Classify the task as backend, frontend, or full-stack.
3. Make the smallest correct change without speculative abstractions or unrelated refactors.
4. Run targeted validation.
5. Review the diff for tenant isolation, validation, money correctness, dead code, secrets, and migrations.
6. Report implemented work, executed checks, important decisions, and deferred scope concisely.

## Scope

Current target is Money Brain v0.1. Implement only the requested milestone. Products, sales, expenses, analytics, AI assistants, marketplace/social integrations, inventory, accounting, e-invoices, Redis, Celery, autonomous agents, microservices, and Kubernetes require an explicit future task.
