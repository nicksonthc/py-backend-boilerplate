#!/bin/bash

# FastAPI with Socket.IO Application Startup Script
# This script provides different ways to start the application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
HOST="0.0.0.0"
PORT="8000"
WORKERS="1"
ENVIRONMENT="development"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dev          Start in development mode with hot reload"
    echo "  --prod         Start in production mode"
    echo "  --host HOST    Host to bind to (default: 0.0.0.0)"
    echo "  --port PORT    Port to bind to (default: 8000)"
    echo "  --workers N    Number of workers (default: 1, recommended for Socket.IO)"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --dev                    # Development mode"
    echo "  $0 --prod                   # Production mode"
    echo "  $0 --dev --port 8080        # Development on port 8080"
    echo "  $0 --prod --host 127.0.0.1  # Production on localhost only"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            ENVIRONMENT="development"
            shift
            ;;
        --prod)
            ENVIRONMENT="production"
            shift
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
if [ -f "requirements.txt" ]; then
    print_info "Installing/updating dependencies..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_warning "requirements.txt not found, skipping dependency installation"
fi

# Set environment variables
export ENVIRONMENT=$ENVIRONMENT

print_info "Starting FastAPI application with Socket.IO..."
print_info "Environment: $ENVIRONMENT"
print_info "Host: $HOST"
print_info "Port: $PORT"
print_info "Workers: $WORKERS"

if [ "$ENVIRONMENT" = "development" ]; then
    print_info "Starting in development mode with hot reload..."
    python3 run.py
else
    print_info "Starting in production mode..."
    
    # Check if gunicorn is available
    if command -v gunicorn &> /dev/null; then
        print_info "Using Gunicorn with Uvicorn workers..."
        gunicorn asgi:application \
            -w $WORKERS \
            -k uvicorn.workers.UvicornWorker \
            --bind $HOST:$PORT \
            --access-logfile - \
            --error-logfile -
    else
        print_warning "Gunicorn not found, falling back to Uvicorn..."
        uvicorn asgi:application \
            --host $HOST \
            --port $PORT \
            --workers $WORKERS
    fi
fi 