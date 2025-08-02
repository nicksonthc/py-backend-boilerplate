#!/bin/bash

## Prerequisites:
# 1. Copy .env.aws.example to .env.aws and configure your ECR details
# 2. Ensure AWS CLI is configured with proper permissions
# Note: The script will automatically load .env.aws if it exists

## Usage macOS/Linux
# cd scripts
# bash build_push_aws.sh your_tag      

## Usage Windows
## Copy-Item .env.aws.example .env.aws
## Edit .env.aws with your values
## cd scripts
## .\build_push_aws.sh your_tag

## Manual environment loading (optional):
# source .env.aws  # Only needed if you want to check variables beforehand

# Default image tag
image_tag=${1:-latest}

# Auto-load environment variables from .env.aws if it exists
if [ -f "../.env.aws" ]; then
    echo "Loading environment from .env.aws..."
    source ../.env.aws
elif [ -f ".env.aws" ]; then
    echo "Loading environment from .env.aws..."
    source .env.aws
else
    echo "Warning: .env.aws file not found. Please create it from .env.aws.example"
    echo "Run: cp .env.aws.example .env.aws"
fi

# Load environment variables (with defaults)
AWS_REGION=${AWS_REGION:-"ap-southeast-1"}
ECR_REGISTRY=${ECR_REGISTRY}
ECR_REPOSITORY=${ECR_REPOSITORY:-"py-backend"}

# Validate required environment variables
if [ -z "$ECR_REGISTRY" ]; then
    echo "Error: ECR_REGISTRY environment variable is required"
    echo "Example: export ECR_REGISTRY=123456789012.dkr.ecr.ap-southeast-1.amazonaws.com"
    exit 1
fi

echo "============Build on platform $OSTYPE ================"
echo "Registry: $ECR_REGISTRY"
echo "Repository: $ECR_REPOSITORY"
echo "Tag: $image_tag"
echo "Region: $AWS_REGION"

# Login to ECR
echo "===========Logging into ECR============"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Build image
echo "===========Building Docker image============"
if [[ "$OSTYPE" == "darwin"* ]]; then 
    # Unix/macOS
    docker buildx build --platform linux/amd64 -t $ECR_REPOSITORY ../.
else 
    # Windows
    docker buildx build -t $ECR_REPOSITORY ../.
fi

# Tag image
echo "===========Tag image with $image_tag=========="
docker tag $ECR_REPOSITORY:latest $ECR_REGISTRY/$ECR_REPOSITORY:$image_tag

# Push image
echo "===========Push image to ECR============"
docker push $ECR_REGISTRY/$ECR_REPOSITORY:$image_tag
read -p "Press Enter to continue..."
