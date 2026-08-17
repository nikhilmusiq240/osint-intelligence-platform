# osint-intelligence-platform

## Dependency policy

This project targets Python 3.12.x for the backend runtime. The selected dependency set is compatible with Python 3.12, and the chosen versions are the latest stable releases available as of August 2026 without using pre-release builds.

- Packages are pinned with exact == versions for deterministic, reviewable builds.
- The architecture intentionally preserves FastAPI, SQLAlchemy, PostgreSQL, and Redis as the primary production stack.
- The PostgreSQL driver decision favors psycopg 3 over psycopg2-binary for the production foundation. psycopg 3 is the actively maintained PostgreSQL driver from the project maintainers, provides better support for modern Python releases, integrates cleanly with SQLAlchemy 2, and is the recommended choice for new production work. `psycopg[binary]` keeps the installation easy and reliable by using the binary wheel path while avoiding the legacy `psycopg2-binary` dependency chain. This is a deliberate modernization step to reduce operational risk and future maintenance cost without changing the target architecture.
- All connectors and OSINT integrations remain intentionally modular and provider-neutral. This prevents dependence on legacy or unmaintained OSINT tools and keeps source selection and licensing review explicit.
