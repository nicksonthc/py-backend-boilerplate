# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Information
- **Framework**: FastAPI backend application with Python 3.12+
- **Database**: PostgreSQL (migrated from Microsoft SQL Server)
- **Architecture**: Layered architecture with DAL, Controllers, and API routes
- **Real-time**: Socket.IO integration for real-time communication
- **ORM**: SQLModel (combining SQLAlchemy + Pydantic)
- **Location**: `/home/nicksonthc/projects/py-backend-boilerplate`

## Development Commands

### Code Quality
- **Lint**: `ruff check .` (fast Python linter)
- **Format**: `ruff format .` (code formatting)
- **Type check**: `mypy .` 
- **Tests**: `pytest` (no test directory currently exists)

### Database Operations
- **Run migrations**: `alembic upgrade head`
- **Create migration**: `alembic revision --autogenerate -m "Description"`
- **Check migration status**: `alembic current`
- **Rollback migration**: `alembic downgrade -1`

### Application Startup
- **Development**: `python run.py`
- **Development (script)**: `./start.sh --dev`
- **Production (script)**: `./start.sh --prod`
- **Validate config**: `python validate_config.py`

### Database Setup
- **Initialize DB**: `python -c "import asyncio; from app.db.init_db import init_db; asyncio.run(init_db())"`
- **Docker PostgreSQL**: `docker run --name postgres-backend -e POSTGRES_PASSWORD=password -e POSTGRES_DB=backend-server -p 5432:5432 -d postgres:15`
- **Validate config**: `python validate_config.py`
- **Seed database**: `python seed.py`

## Architecture Overview

### Layered Architecture Pattern
The application follows a clean layered architecture:

1. **API Layer** (`app/api/v1/`): FastAPI route definitions
2. **Controller Layer** (`app/controllers/`): Business logic and orchestration
3. **DAL Layer** (`app/dal/`): Data Access Layer for database operations
4. **Model Layer** (`app/models/`):
   - `entities/`: SQLModel database entities
   - `schemas/`: Pydantic request/response models
5. **Core Layer** (`app/core/`): Configuration, middleware, and utilities

### Database Architecture
- **Base Classes**: All entities inherit from `BaseTimestamp` for consistent timestamping
- **Modern Types**: Uses Python 3.12+ union syntax (`str | None` instead of `Optional[str]`)
- **Async/Await**: Full async support with `AsyncSession`
- **Connection**: Uses `asyncpg` driver for PostgreSQL
- **Timezone Support**: All datetime fields use `DateTime(timezone=True)` for `TIMESTAMP WITH TIME ZONE`
- **Migration**: Successfully migrated from MSSQL to PostgreSQL with timezone-aware models

### Key Design Patterns
- **Dependency Injection**: Controllers receive `AsyncSession` in constructor
- **Decorator Pattern**: `@decorateAllFunctionInClass(async_log_and_raise_error())` for error handling
- **Repository Pattern**: DAL classes handle data access
- **DTO Pattern**: Separate schemas for create, update, and response operations

### Real-time Features
- **Socket.IO**: WebSocket communication via `fastapi-socketio`
- **Event Management**: `LogEventManager` and `WmsSocketIO` for real-time events
- **TCP/IP**: Custom TCP server implementation in `app/core/tcpip/`

### Background Processing
- **Log Management**: `LogManager` with cleanup services
- **HTTP Retry**: `HttpRetryManager` for resilient HTTP operations
- **Circuit Breaker**: Fault tolerance implementation
- **Scheduler**: APScheduler integration for background tasks

## File Structure Conventions

### Models
- **Entities** (`app/models/entities/`): Database table definitions
- **Schemas** (`app/models/schemas/`): API request/response models
- **DTOs** (`app/dto/`): Data transfer objects for specific use cases

### Business Logic
- **Controllers**: Main business logic, inherit from `BaseController`
- **DAL**: Database operations, inherit from `BaseDAL`
- **Routes**: API endpoint definitions with FastAPI decorators

### Configuration
- **Environment**: Uses `pydantic-settings` with `.env` file
- **Database URLs**: Automatic generation for PostgreSQL with `CONFIG.POSTGRES_DATABASE_URL`
- **Legacy Support**: MSSQL configuration preserved for reference
- **Validation**: Configuration validation with detailed error messages via `validate_config.py`

## Development Notes

### Database Migration Workflow
1. Create model in `app/models/entities/`
2. Import model in `alembic/env.py` (currently imports all with `*`)
3. Generate migration: `alembic revision --autogenerate -m "Description"`
4. Review generated migration file
5. Apply migration: `alembic upgrade head`

### Adding New Features
1. Create entity model in `app/models/entities/`
2. Create Pydantic schemas in `app/models/schemas/`
3. Create DAL class in `app/dal/`
4. Create controller in `app/controllers/`
5. Create API routes in `app/api/v1/`
6. Register router in `app/main.py`

### Error Handling
- **Global Handlers**: Custom exception handlers for validation and general errors
- **Decorators**: `@async_log_and_raise_error()` for consistent error logging
- **Responses**: Standardized response format via `app.core.response`

### Socket.IO Events
- **Manager**: `WmsSocketIO` handles event registration
- **Events**: Connect, disconnect, ping, room management
- **Path**: `/ws/socket.io` for WebSocket connections

## Configuration Requirements

### Environment Variables
Key variables in `.env` (see `env.example`):
- `ENV`: Environment (dev/production)
- `API_HOST`, `API_PORT`: API server configuration
- `TCP_HOST`, `TCP_PORT`: TCP server configuration
- `POSTGRES_*`: PostgreSQL connection parameters (primary database)
- `MSSQL_*`: Legacy MSSQL parameters (kept for migration reference)
- `SECRET_KEY`: JWT token signing
- `TIME_ZONE`: Default timezone (Asia/Kuala_Lumpur)

### Database Dependencies
- **PostgreSQL 13+** with asyncpg driver
- **WSL2 Support**: Can connect to Windows PostgreSQL instance via network IP
- **Timezone Awareness**: All datetime fields properly handle UTC/timezone conversion
- **Connection**: Uses `asyncpg` for high-performance async operations

## PostgreSQL Migration Notes

### Recent Changes (2025-07-27)
- **Database Migration**: Successfully migrated from Microsoft SQL Server to PostgreSQL
- **Timezone Support**: Updated all datetime fields to use `DateTime(timezone=True)` for proper timezone handling
- **Model Updates**: All models now use `sa_type=DateTime(timezone=True)` with `default_factory=lambda: datetime.now(timezone.utc)`
- **Configuration**: Added `POSTGRES_DATABASE_URL` property to config while preserving MSSQL config for reference
- **Connection Issues**: Fixed SQLAlchemy Column reuse issues by using `sa_type` instead of `sa_column`

### Key Files Updated
- `app/models/entities/base_timestamp.py`: Timezone-aware base class
- `app/models/entities/log_model.py`: PostgreSQL-compatible logging
- `app/models/entities/setting_model.py`: Settings with timezone support
- `app/models/entities/log_event_model.py`: Event logging with timezones
- `app/db/init_db.py`: PostgreSQL database initialization
- `validate_config.py`: PostgreSQL connection validation

### Timezone Handling
All datetime fields now properly handle:
- UTC defaults via `datetime.now(timezone.utc)`
- PostgreSQL `TIMESTAMP WITH TIME ZONE` columns
- Proper timezone conversion and storage

## Production Considerations
- **ASGI**: Use `asgi.py` for production deployment
- **Docker**: Dockerfile and docker-compose.yml provided
- **AWS ECR**: `scripts/build_push_aws.sh` for container deployment
- **Security**: OAuth2 password flow with JWT tokens
- **CORS**: Configured for cross-origin requests
- **Static Files**: Custom Swagger UI and ReDoc served from `/static`