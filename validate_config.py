#!/usr/bin/env python3
"""
Configuration validation script for FastAPI with MSSQL application.

This script helps validate that your environment configuration is correct
before running the application.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app.core.config import CONFIG
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure you have installed all dependencies: pip install -r requirements.txt")
    sys.exit(1)


class ConfigValidator:
    """Validates the application configuration."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.success: List[str] = []

    def print_result(self, success: bool, message: str, level: str = "info"):
        """Print formatted result message."""
        if success:
            print(f"✅ {message}")
            self.success.append(message)
        elif level == "warning":
            print(f"⚠️  {message}")
            self.warnings.append(message)
        else:
            print(f"❌ {message}")
            self.errors.append(message)

    def validate_env_file(self) -> bool:
        """Validate that .env file exists and has required variables."""
        print("\n🔍 Validating environment configuration...")

        env_file = Path(".env")
        if not env_file.exists():
            self.print_result(False, ".env file not found. Copy env.example to .env")
            return False

        self.print_result(True, ".env file found")

        # Check required environment variables
        required_vars = ["MSSQL_USER", "MSSQL_PASSWORD", "MSSQL_HOST", "MSSQL_PORT", "MSSQL_DB", "SECRET_KEY"]

        missing_vars = []
        for var in required_vars:
            value = getattr(CONFIG, var, None)
            if not value or (isinstance(value, str) and value.strip() == ""):
                missing_vars.append(var)

        if missing_vars:
            self.print_result(False, f"Missing required environment variables: {', '.join(missing_vars)}")
            return False

        self.print_result(True, "All required environment variables are set")
        return True

    def validate_secret_key(self) -> bool:
        """Validate that secret key is properly configured."""
        print("\n🔒 Validating security configuration...")

        if CONFIG.SECRET_KEY == "your-super-secret-key-change-this-in-production":
            self.print_result(False, "SECRET_KEY is still using default value. Please change it!", "warning")
            return False

        if len(CONFIG.SECRET_KEY) < 32:
            self.print_result(False, "SECRET_KEY should be at least 32 characters long", "warning")
            return False

        self.print_result(True, "SECRET_KEY is properly configured")
        return True

    async def test_database_connection(self) -> bool:
        """Test actual database connection."""
        print("\n🔗 Testing database connection...")

        try:
            engine = create_async_engine(CONFIG.POSTGRES_DATABASE_URL, pool_pre_ping=True, connect_args={"timeout": 10})

            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1 as test"))
                test_value = result.scalar()

                if test_value == 1:
                    self.print_result(True, "Database connection successful!")

                    # Test if database exists and is accessible
                    db_result = await conn.execute(text("SELECT current_database() as db_name"))
                    db_name = db_result.scalar()

                    if db_name:
                        self.print_result(True, f"Connected to database: {db_name}")

                        if db_name.lower() == "py-backend":
                            self.print_result(True, "Connected to the correct database")
                        else:
                            self.print_result(False, f"Connected to '{db_name}' but expected 'py-backend'", "warning")

                    return True
                else:
                    self.print_result(False, "Database connection test failed")
                    return False

        except Exception as e:
            self.print_result(False, f"Database connection failed: {str(e)}")
            print(f"   Connection string: {CONFIG.POSTGRES_DATABASE_URL}")
            return False
        finally:
            if "engine" in locals():
                await engine.dispose()

    def validate_dependencies(self) -> bool:
        """Validate that required dependencies are installed."""
        print("\n📦 Validating dependencies...")

        required_packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "sqlmodel",
            "aioodbc",
            "pyodbc",
            "python-socketio",
            "httpx",
            "alembic",
        ]

        missing_packages = []
        for package in required_packages:
            try:
                # Special handling for packages with different import names
                import_name = package.replace("-", "_")
                if package == "python-socketio":
                    import_name = "socketio"

                __import__(import_name)
                self.print_result(True, f"{package} is installed")
            except ImportError:
                missing_packages.append(package)
                self.print_result(False, f"{package} is not installed")

        if missing_packages:
            print(f"\n💡 Install missing packages with: pip install {' '.join(missing_packages)}")
            return False

        return True

    def validate_files(self) -> bool:
        """Validate that required files exist."""
        print("\n📁 Validating required files...")

        required_files = [
            "requirements.txt",
            "alembic.ini",
            "run.py",
            "asgi.py",
            "app/main.py",
            "app/core/config.py",
        ]

        missing_files = []
        for file_path in required_files:
            if Path(file_path).exists():
                self.print_result(True, f"{file_path} exists")
            else:
                missing_files.append(file_path)
                self.print_result(False, f"{file_path} is missing")

        return len(missing_files) == 0

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("📋 VALIDATION SUMMARY")
        print("=" * 60)

        print(f"✅ Success: {len(self.success)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")

        if self.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        if self.errors:
            print(f"\n❌ Errors:")
            for error in self.errors:
                print(f"   • {error}")

        if not self.errors:
            print("\n🎉 Configuration validation completed successfully!")
            print("You can now run the application with: python run.py")
        else:
            print(f"\n🚨 Please fix the {len(self.errors)} error(s) above before running the application.")
            return False

        return True


async def main():
    """Main validation function."""
    print("🚀 FastAPI MSSQL Configuration Validator")
    print("=" * 60)

    validator = ConfigValidator()

    # Run all validations
    validations = [
        validator.validate_files(),
        validator.validate_dependencies(),
        validator.validate_env_file(),
        validator.validate_secret_key(),
    ]

    # Test database connection only if basic validations pass
    if all(validations):
        await validator.test_database_connection()

    # Print summary and return success status
    success = validator.print_summary()
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Validation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error during validation: {e}")
        sys.exit(1)
