# ADR-001: Flask Application Factory Pattern

## Status
Accepted

## Context
AIRA is designed to be a multi-environment, testable backend application. A monolithic global app instance makes configuration swapping (e.g., testing vs. development vs. production) difficult and causes state leakage across test suites.

## Decision
Adopt the Flask Application Factory pattern (`create_app(config_name=None)`).
- Environment configurations are loaded dynamically based on `FLASK_ENV` or explicit parameter.
- Database extensions (`SQLAlchemy`, `Migrate`) are instantiated unbound and attached inside the factory using `.init_app(app)`.
- Core middleware (Request ID generation, logging, centralized error handling) and routes are registered during factory execution.

## Consequences
- **Positive**: Clean isolation between test runs and live environments; zero global state mutation during testing.
- **Positive**: Simplified extension initialization and blueprint registration.
- **Trade-off**: Requires passing the app instance or using application context when performing CLI operations or migrations.
