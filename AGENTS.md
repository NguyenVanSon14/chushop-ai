# ChủShop AI

Build Money Brain v0.1 as a maintainable SaaS for Vietnamese small businesses.

- Keep `backend/` and `frontend/` separate. The backend owns authentication, authorization, tenant checks, persistence, business and financial logic, analytics, and AI orchestration. The frontend owns UI and API presentation.
- Backend flow is Router → Service → Repository → Database. Keep routers thin and use Alembic for schema changes.
- Every business-owned query must authenticate the user, verify `BusinessMember`, and scope access to that business. Cross-tenant access must fail.
- Store authoritative VND money as integers, never floats. Python calculates, the frontend displays, and LLMs only explain. Preserve historical costs with `cost_price_snapshot` when sales are later added.
- Test business logic, financial calculations, and tenant isolation. Never report a check as passing unless it was run.
- Current scope is Money Brain v0.1. Do not add future products, sales, analytics, AI, integrations, queues, microservices, or infrastructure without an explicit task.
- Before changes, read the relevant `WORKFLOW.md` section and related source/tests. Make the smallest correct change and review the diff.

Common commands are documented in `README.md`.
