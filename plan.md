# Delivery API — Build Plan and Evolution

## Phase 0: Goals and Constraints
- Build a delivery API covering orders, couriers, assignments.
- Favor simplicity and speed first; durability added incrementally.
- Provide cross-platform usage (Windows PowerShell and Linux/macOS).
- Enable benchmarking via Prometheus metrics.
- Keep auth minimal but realistic with JWT roles.

## Phase 1: Foundation (In-Memory)
- Scaffold FastAPI app: routers for health, orders, couriers, assignments.
- Pydantic schemas for request/response.
- In-memory services for rapid iteration.
- Quick developer feedback and endpoint exploration.

## Phase 2: Auth + Metrics
- Add OAuth2 password with JWT (PyJWT); demo users: admin, courier, customer.
- Protect non-health endpoints with bearer auth.
- Integrate Prometheus FastAPI instrumentator; expose /metrics for scraping and benchmarking.

## Phase 3: Testing
- Add pytest-based tests for services and schema validation.
- Introduce simple edge cases and validations.
- Verify functional flows across orders, couriers, assignments.

## Phase 4: Persistence Migration (SQLite)
- Move services from memory to SQLAlchemy 2.0 async with SQLite (aiosqlite).
- Create models: Order, Courier, Assignment; setup session and Base.
- Ensure startup runs DDL and seeds sample data for quick experimentation.

## Phase 5: Idempotency + Version Columns
- Implement Idempotency-Key header support for POST endpoints.
- Persist idempotency records (key, endpoint, actor, request hash, response) with a unique constraint to deduplicate requests.
- Add version columns to orders and assignments; increment on update to prepare for optimistic concurrency patterns.
- Extend tests to cover idempotent behavior and version increments.

## Phase 6: Documentation
- README.md with summary, stack, description, quick start, and endpoint examples for Windows/Linux.
- Plan.md capturing design evolution and phased approach.

## Suggestions / Next Phases
- Status transition guardrails: define allowed transitions and role-based constraints.
- Optimistic concurrency: compare-and-swap based on version to prevent lost updates.
- Idempotency TTL and GC: configurable retention, cleanup jobs.
- Role-based permissions: enforce per-route actions (e.g., courier actions vs dispatcher).
- Webhooks/outbox pattern: reliable event delivery with retry and dead-letter handling.
- Pagination and filtering: scalable listing of orders/assignments (e.g., time ranges, states).
- Rate limiting: protect endpoints during benchmarks and public exposure.
- Error catalog: consistent error codes and human-readable messages.

## Benchmarks and Observability
- Use /metrics to capture request rates, latency histograms, and error counts per route.
- Configure Prometheus and Grafana dashboards for latency and throughput curves.
- Synthetic load scripts (k6 or locust) to drive mixed workflows (create → assign → update status).
