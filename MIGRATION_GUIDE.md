# Database Migration Guide

This guide explains how to add new models and run database migrations in the py-backend-boilerplate FastAPI application using Alembic.

## Overview

The application uses:
- **SQLModel** for database models (built on SQLAlchemy)
- **Alembic** for database migrations
- **Microsoft SQL Server** as the database
- **Async/Await** pattern for database operations

## Project Structure

```
app/
├── models/
│   └── entities/
│       ├── item_model.py      # Example existing model
│       ├── user_model.py      # Example existing model
│       └── product_model.py   # New model example
├── core/
│   └── config.py             # Database configuration
└── db/
    ├── base.py               # Base model imports
    └── session.py            # Database session setup

alembic/
├── versions/                 # Migration files
├── env.py                   # Alembic environment configuration
└── script.py.mako          # Migration template

alembic.ini                  # Alembic configuration
```

## Step 1: Create a New Model

### 1.1 Model Structure
Create your model file in `app/models/entities/`. Follow this pattern:

```python
# app/models/entities/your_model.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, func

class YourModelBase(SQLModel):
    """Base model with shared fields."""
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    # Add your fields here

class YourModel(YourModelBase, table=True):
    """SQLModel entity for the your_table table."""
    __tablename__ = "your_table"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), 
            server_default=func.now(), 
            onupdate=func.now()
        )
    )

# API Models
class YourModelCreate(YourModelBase):
    """Model for creating new records."""
    pass

class YourModelUpdate(SQLModel):
    """Model for updating existing records."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    # Make all fields optional for updates

class YourModelResponse(YourModelBase):
    """Model for API responses."""
    id: int
    created_at: datetime
    updated_at: datetime
```

### 1.2 Field Types and Constraints

Common field patterns:

```python
# String fields
name: str = Field(min_length=1, max_length=255)
description: Optional[str] = Field(default=None, max_length=1000)

# Numeric fields
price: float = Field(gt=0, description="Must be positive")
quantity: int = Field(ge=0, default=0)

# Boolean fields
is_active: bool = Field(default=True)

# Enum fields
from enum import Enum
class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

status: StatusEnum = Field(default=StatusEnum.ACTIVE)

# Foreign keys (relationships)
user_id: Optional[int] = Field(foreign_key="users.id", default=None)

# Unique constraints
email: str = Field(unique=True, max_length=255)
```

## Step 2: Import Model in Alembic

### 2.1 Update alembic/env.py
Add your new model import to make it discoverable by Alembic:

```python
# alembic/env.py
# Import Base and all models here
from app.db.base import Base
from app.models.entities import item_model
from app.models.entities import user_model
from app.models.entities import your_model  # Add this line
```

**Important**: Every new model must be imported in `alembic/env.py` or it won't be detected for migrations, for now we had added imported all with *

## Step 3: Generate Migration

### 3.1 Auto-generate Migration
```bash
# Generate migration with descriptive message
alembic revision --autogenerate -m "Add YourModel table"

# Example messages:
alembic revision --autogenerate -m "Add Product model"
alembic revision --autogenerate -m "Add User authentication fields"
alembic revision --autogenerate -m "Update Item model with new category field"
```

### 3.2 Review Generated Migration
Check the generated file in `alembic/versions/`:

```python
# Example: alembic/versions/abc123_add_product_model.py
"""Add Product model

Revision ID: abc123def456
Revises: previous_revision_id
Create Date: 2025-06-11 13:55:42.171899
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel  # Add this import if missing

def upgrade() -> None:
    # Review these commands before running
    op.create_table('products',
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        # ... other columns
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    # This will be run if you need to rollback
    op.drop_table('products')
```

### 3.3 Fix Common Issues
If migration involve alter column name or type with existing prod data, ensure modify migration script to update the value in existing column to targeted type.

```
修行靠自己
```

## Step 4: Run Migration

### 4.1 Apply Migration
```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade abc123def456

# Apply one migration at a time
alembic upgrade +1
```

### 4.2 Check Migration Status
```bash
# Show current migration
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
```

## Step 5: Rollback (if needed)

### 5.1 Rollback Commands
```bash
# Rollback to previous migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123def456

# Rollback all migrations (careful!)
alembic downgrade base
```

## Example: Complete Product Model Migration

Here's the complete example we just implemented:

### 1. Created Model
```python
# app/models/entities/product_model.py
class Product(ProductBase, table=True):
    __tablename__ = "products"
    id: Optional[int] = Field(default=None, primary_key=True)
    # ... full implementation above
```

### 2. Updated Alembic
```python
# alembic/env.py
from app.models.entities import *
```

### 3. Generated Migration
```bash
alembic revision --autogenerate -m "Add Product model"
# Generated: 6838d9e72087_add_product_model.py
```

### 4. Applied Migration
```bash
alembic upgrade head
# Created products table in database
```

## Common Migration Scenarios

### Adding a New Column
```python
# In your model, add the new field:
new_field: str = Field(default="default_value", max_length=100)

# Generate migration:
alembic revision --autogenerate -m "Add new_field to YourModel"
```

### Modifying Existing Column
```python
# Change the field in your model:
name: str = Field(min_length=1, max_length=500)  # Changed from 255

# Generate migration:
alembic revision --autogenerate -m "Increase name field length in YourModel"
```

### Adding Relationships
```python
# In your model:
user_id: Optional[int] = Field(foreign_key="users.id", default=None)

# Generate migration:
alembic revision --autogenerate -m "Add user relationship to YourModel"
```

### Dropping a Table
```python
# Remove the model class and import
# Generate migration:
alembic revision --autogenerate -m "Remove YourModel table"
```

## Best Practices

### 1. Migration Messages
Use descriptive messages:
- ✅ "Add Product model with inventory tracking"
- ✅ "Update User model with authentication fields"
- ✅ "Remove deprecated Category table"
- ❌ "Update models"
- ❌ "Changes"

### 2. Review Before Apply
Always review generated migrations before running them:
- Check column types are correct
- Verify constraints are appropriate
- Ensure foreign keys are properly set
- Test on development database first

### 3. Backup Before Migration
For production environments:
```bash

# Run migration
alembic upgrade head
```

### 4. Environment-Specific Migrations
```bash
# Development
alembic -c alembic-dev.ini upgrade head

# Production
alembic -c alembic-prod.ini upgrade head
```

## Troubleshooting

### Common Errors

**1. "Table already exists"**
- Solution: Check if migration was already applied
- Command: `alembic current` and `alembic history`

**2. "sqlmodel not found"**
- Solution: Add `import sqlmodel` to migration file

**3. "Foreign key constraint failed"**
- Solution: Ensure referenced table exists first
- Check migration order

**4. "Column cannot be null"**
- Solution: Add default values or make field optional
- Update model definition

**5. "Connection failed"**
- Solution: Check database is running
- Verify `.env` configuration
- Run: `python validate_config.py`

### Debug Mode
```bash
# Run with verbose output
alembic -x verbose=true upgrade head

# Show SQL commands without executing
alembic upgrade head --sql
```

## Configuration Files

### alembic/env.py 
```
It import CONFIG.POSTGRES_DATABASE_URL , ensure your .env is created
```

### .env
```env
MSSQL_HOST=localhost
MSSQL_PORT=1433
MSSQL_USER=sa
MSSQL_PASSWORD=Pingspace@2025
MSSQL_DB=py-backend
```

## Testing Migrations

### 1. Test Migration Up/Down
```bash
# Apply migration
alembic upgrade head

# Test rollback
alembic downgrade -1

# Apply again
alembic upgrade head
```

### 2. Test with Sample Data
```python
# Create test script
async def test_new_model():
    from app.models.entities.product_model import Product
    from app.db.session import SessionLocal
    
    async with SessionLocal() as session:
        product = Product(
            name="Test Product",
            price=10.99,
            category="Test",
            sku="TEST001"
        )
        session.add(product)
        await session.commit()
        print(f"Created product with ID: {product.id}")
```

## Next Steps

After creating your model and running migrations:

1. **Create Repository** (`app/dal/your_model_repository.py`)
2. **Create Service** (`app/services/your_model_service.py`)
3. **Create API Routes** (`app/api/v1/your_model_routes.py`)
4. **Add to Main App** (include router in `app/main.py`)
5. **Write Tests** (`tests/test_your_model.py`)

## Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy Core Documentation](https://docs.sqlalchemy.org/en/14/core/)
- [MSSQL Setup Guide](./MSSQL_SETUP.md) 