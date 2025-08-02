# Python Backend Boilerplate

A modern, high-performance FastAPI backend application built with Python 3.12+, featuring real-time Socket.IO communication, PostgreSQL database support, and a clean layered architecture.

## 🚀 Features

- **Modern Python 3.12+** - Latest language features and performance improvements
- **FastAPI** - High-performance web framework with automatic API documentation
- **Socket.IO** - Real-time bidirectional communication
- **SQLModel** - Modern SQL database toolkit combining SQLAlchemy + Pydantic
- **PostgreSQL** - Robust open-source database with timezone support
- **Alembic** - Database migration management
- **Async/Await** - Full asynchronous support throughout the stack
- **Type Safety** - Comprehensive type hints with Python 3.12+ syntax
- **Layered Architecture** - Clean separation of concerns
- **RESTful API** - Standardized API endpoints with filtering and pagination
- **Real-time Events** - Live updates via WebSocket connections
- **Production Ready** - Comprehensive error handling and logging

## 📋 Prerequisites

- **Python 3.12+** (Required for modern type hints and features)
- **PostgreSQL 13+** (Local, Cloud, or Docker)
- **Git** (For version control)

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd py-backend-boilerplate
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
cp env.example .env
```

Edit `.env` with your configuration:
```env
ENV=dev

# API configuration
API_HOST=127.0.0.1
API_PORT=3100

# TCP configuration
TCP_HOST=127.0.0.1
TCP_PORT=2525

# PostgreSQL Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=backend-server

# Legacy MSSQL (for migration reference)
MSSQL_HOST=localhost
MSSQL_PORT=1433
MSSQL_USER=sa
MSSQL_PASSWORD=your_password
MSSQL_DB=py-backend

TIME_ZONE=Asia/Kuala_Lumpur
```

### 5. Database Setup

#### Option A: Local PostgreSQL
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb backend-server

# Create user (optional)
sudo -u postgres createuser --interactive your_username
```

#### Option B: Docker PostgreSQL
```bash
# Run PostgreSQL in Docker
docker run --name postgres-backend \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=backend-server \
  -p 5432:5432 \
  -d postgres:15

# Or using docker-compose
docker-compose up -d postgres
```

#### Option C: WSL2 with Windows PostgreSQL
If running on WSL2 with PostgreSQL on Windows host:
1. Update `POSTGRES_HOST` in `.env` to your Windows IP (e.g., `172.21.64.1`)
2. Configure PostgreSQL to accept connections from WSL2 network
3. Update `postgresql.conf`: `listen_addresses = '*'`
4. Update `pg_hba.conf`: Add `host all all 172.21.0.0/16 md5`

### 6. Initialize Database
```bash
# Initialize database and create tables
python -c "
import asyncio
from app.db.init_db import init_db
asyncio.run(init_db())
"

# Or run database migrations
alembic upgrade head
```

### 7. Validate Configuration
```bash
# Validate your setup
python validate_config.py
```

### 8. Start the Application

#### Development Mode
```bash
python run.py
```

#### Using Startup Script
```bash
./start.sh --dev
```

#### Production Mode
```bash
./start.sh --prod
```

## 🏗️ Project Structure

```
py-backend-boilerplate/
├── app/
│   ├── api/v1/                 # API route definitions
│   │   ├── auth_routes.py      # Authentication endpoints
│   │   ├── job_routes.py       # Job endpoints
│   │   ├── order_routes.py     # Order endpoints
│   │   ├── setting_routes.py   # Settings endpoints
│   │   ├── log_event_routes.py # Log event endpoints
│   │   └── http_retry_routes.py # HTTP retry endpoints
│   ├── auth/                   # Authentication services
│   │   ├── auth_services.py    # Auth business logic
│   │   └── token.py            # JWT token handling
│   ├── controllers/            # Business logic layer
│   │   ├── base_controller.py  # Base controller class
│   │   ├── job_controller.py   # Job business logic
│   │   ├── order_controller.py # Order business logic
│   │   ├── setting_controller.py # Settings business logic
│   │   ├── log_controller.py   # Log business logic
│   │   ├── log_event_controller.py # Log event business logic
│   │   └── http_retry_controller.py # HTTP retry business logic
│   ├── dal/                    # Data Access Layer
│   │   ├── base_dal.py         # Base DAL class
│   │   ├── job_dal.py          # Job data access
│   │   ├── order_dal.py        # Order data access
│   │   ├── setting_dal.py      # Settings data access
│   │   ├── log_dal.py          # Log data access
│   │   ├── log_event_dal.py    # Log event data access
│   │   └── http_retry_dal.py   # HTTP retry data access
│   ├── models/
│   │   ├── entities/           # SQLModel database entities
│   │   │   ├── base_timestamp.py # Base timestamp fields
│   │   │   ├── job_model.py    # Job entity
│   │   │   ├── order_model.py  # Order entity
│   │   │   ├── setting_model.py # Settings entity
│   │   │   ├── log_model.py    # Log entity
│   │   │   ├── log_event_model.py # Log event entity
│   │   │   └── http_retry_model.py # HTTP retry entity
│   │   └── schemas/            # Pydantic request/response schemas
│   │       ├── job_schema.py   # Job request/response models
│   │       ├── order_schema.py # Order request/response models
│   │       ├── setting_schema.py # Settings request/response models
│   │       ├── log_event_schema.py # Log event request/response models
│   │       └── http_retry_schema.py # HTTP retry request/response models
│   ├── dto/                    # Data Transfer Objects
│   │   ├── auth_dto.py         # Authentication DTOs
│   │   └── setting_dto.py      # Settings DTOs
│   ├── core/                   # Core configuration and utilities
│   │   ├── config.py           # Environment configuration
│   │   ├── middleware.py       # Response middleware
│   │   ├── response.py         # Standardized response models
│   │   ├── decorators.py       # Common decorators
│   │   ├── circuit_breaker.py  # Circuit breaker implementation
│   │   ├── socketio_manager.py # Socket.IO event management
│   │   ├── log_manager.py      # Log processing manager
│   │   ├── log_event_manager.py # Log event processing
│   │   ├── http_retry_manager.py # HTTP retry logic
│   │   ├── http_headers_manager.py # HTTP headers management
│   │   └── tcpip/              # TCP/IP communication
│   │       ├── tcp_server.py   # TCP server implementation
│   │       ├── async_tcp_server.py # Async TCP server
│   │       └── async_tcp_client.py # Async TCP client
│   ├── db/                     # Database configuration
│   │   ├── base.py             # SQLAlchemy base
│   │   ├── session.py          # Async session management
│   │   └── init_db.py          # Database initialization
│   ├── services/               # External service integrations
│   ├── utils/                  # Utility functions
│   │   ├── console.py          # Console output utilities
│   │   ├── conversion.py       # Data conversion utilities
│   │   ├── enum.py             # Common enumerations
│   │   ├── logger.py           # Logging utilities
│   │   └── scheduler.py        # Task scheduling utilities
│   └── main.py                 # FastAPI application entry point
├── alembic/                    # Database migrations
│   ├── versions/               # Migration version files
│   ├── env.py                  # Alembic environment config
│   └── script.py.mako          # Migration script template
├── scripts/                    # Utility scripts
│   ├── build_push_aws.sh       # AWS ECR build and push
│   ├── bump_version.py         # Version bumping script
│   ├── azuresql_docker.sh      # Azure SQL Docker setup
│   └── mssql_docker.sh         # MSSQL Docker setup
├── static/                     # Static files
│   ├── swagger-ui/             # Custom Swagger UI assets
│   └── redoc/                  # Custom ReDoc assets
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Python project configuration
├── run.py                      # Development server runner
├── asgi.py                     # ASGI application for production
├── seed.py                     # Database seeding script
├── validate_config.py          # Configuration validation
├── version.py                  # Application version
├── start.sh                    # Startup script
├── dockerfile                  # Docker configuration
├── docker_compose.yml          # Docker Compose configuration
├── Procfile                    # Process file for deployment
├── env.example                 # Environment variables template
├── alembic.ini                 # Alembic configuration
├── MIGRATION_GUIDE.md          # Database migration guide
└── README.md                   # This file
```

## 🌐 API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://127.0.0.1:3100/docs
- **ReDoc**: http://127.0.0.1:3100/redoc
- **OpenAPI Schema**: http://127.0.0.1:3100/openapi.json

### Available Endpoints

#### Orders
- `GET /api/v1/orders` - List orders with filtering and pagination
- `POST /api/v1/orders` - Create new order
- `GET /api/v1/orders/{order_id}` - Get specific order
- `PUT /api/v1/orders/{order_id}` - Update order
- `DELETE /api/v1/orders/{order_id}` - Delete order

#### Jobs
- `GET /api/v1/jobs` - List jobs
- `POST /api/v1/jobs` - Create new job
- `GET /api/v1/jobs/{job_id}` - Get specific job
- `PUT /api/v1/jobs/{job_id}` - Update job
- `DELETE /api/v1/jobs/{job_id}` - Delete job

#### System
- `GET /` - API welcome page
- `GET /health` - Health check endpoint

## 🔌 Real-time Socket.IO

### Connection Details
- **URL**: `ws://127.0.0.1:3100/ws/socket.io`
- **Path**: `/ws/socket.io`
- **Transport**: WebSocket

### Client Example
```python
import socketio

# Create Socket.IO client
sio = socketio.Client()

# Connect to server
url = "ws://127.0.0.1:3100/ws/socket.io"
sio.connect(
    url, 
    socketio_path="/ws/socket.io", 
    wait_timeout=10, 
    transports=["websocket"]
)

# Listen for events
@sio.event
def connect():
    print("Connected to server!")

@sio.event
def disconnect():
    print("Disconnected from server!")

@sio.on("welcome")
def on_welcome(data):
    print(f"Welcome message: {data}")

# Emit events
sio.emit("ping", {"message": "Hello server!"})
```

### Available Events
- `connect` - Client connects
- `disconnect` - Client disconnects
- `ping` - Ping server (responds with `pong`)
- `join_room` - Join a room
- `leave_room` - Leave a room
- `welcome` - Welcome message from server

## 🗄️ Database Management

### Generate Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Check current status
alembic current

# Rollback migration
alembic downgrade -1
```

### Database Models
The application uses SQLModel entities with PostgreSQL timezone support and modern Python 3.12+ type hints:

```python
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from sqlalchemy import DateTime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .order_model import Order

class Job(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    status: str = Field(default="pending")
    order_id: int = Field(foreign_key="order.id")
    
    # Timezone-aware datetime with PostgreSQL support
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False
    )
    
    # Relationships
    order: "Order" = Relationship(back_populates="jobs")
```

#### Timezone Support
All datetime fields use:
- `DateTime(timezone=True)` for PostgreSQL `TIMESTAMP WITH TIME ZONE`
- `datetime.now(timezone.utc)` for UTC defaults
- Proper timezone-aware datetime handling throughout the application

## 🧪 Development

### Code Style
This project uses modern Python 3.12+ features:

- **Type Hints**: `str | None` instead of `Optional[str]`
- **Type Aliases**: `type UserID = int`
- **Pattern Matching**: `match/case` statements
- **Enhanced F-strings**: Latest f-string capabilities

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_orders.py
```

### Code Formatting
```bash
# Format code with Black
black app/

# Sort imports with isort
isort app/

# Type checking with mypy
mypy app/
```

## 🚀 Deployment

### Production Setup
1. Set `ENV=production` in `.env`
2. Configure production database credentials
3. Set up proper CORS origins
4. Configure logging and monitoring
5. Use ASGI server (Gunicorn + Uvicorn)

### Docker Deployment

#### AWS ECR Setup

> **Prerequisites:**
> - Docker must be installed and running locally
> - AWS CLI configured with proper ECR permissions
> - Valid AWS credentials (via `~/.aws/credentials` or environment variables)

**1. Configure ECR Environment:**
```bash
# Copy the example configuration
cp .env.aws.example .env.aws

# Edit .env.aws with your actual ECR details
# Update ECR_REGISTRY with your AWS account ID
```

**2. Build and Push to ECR:**
```bash
# Build and push Docker image (default tag: latest)
# The script automatically loads .env.aws
cd scripts
./build_push_aws.sh

# To use a custom image tag:
./build_push_aws.sh my_custom_tag
```

> The `build_push_aws.sh` script will:
> 1. Automatically load environment variables from `.env.aws`
> 2. Validate required environment variables are set
> 3. Build the Docker image with the specified tag (default: `latest`)
> 4. Authenticate with AWS ECR using your AWS credentials
> 5. Push the image to your configured ECR repository

**Environment Variables Required:**
- `ECR_REGISTRY`: Your ECR registry URL (e.g., `123456789012.dkr.ecr.ap-southeast-1.amazonaws.com`)
- `ECR_REPOSITORY`: Repository name (default: `py-backend`)
- `AWS_REGION`: AWS region (default: `ap-southeast-1`)

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment (dev/prod) | `dev` |
| `API_HOST` | API server host | `127.0.0.1` |
| `API_PORT` | API server port | `3100` |
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_USER` | PostgreSQL username | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | - |
| `POSTGRES_DB` | PostgreSQL database | `backend-server` |
| `TIME_ZONE` | Application timezone | `Asia/Kuala_Lumpur` |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint when server is running
- **Issues**: Create an issue in the repository
- **Migration Guide**: See `MIGRATION_GUIDE.md` for database changes

## 🔗 Related Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Socket.IO Python Client](https://python-socketio.readthedocs.io/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
