#!/bin/bash
# deploy-staging.sh
# BMAD Staging Environment Deployment Script

set -e

echo "🚀 Deploying BMAD to Staging Environment..."

# Environment setup
export ENVIRONMENT=staging
export COMPOSE_PROJECT_NAME=bmad-staging

# Check if we're in the right directory
if [ ! -f "docker-compose.staging.yml" ]; then
    echo "❌ Error: docker-compose.staging.yml not found. Please run from project root."
    exit 1
fi

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Build and deploy
echo "🔨 Building and deploying services..."
docker-compose -f docker-compose.staging.yml up --build -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Health checks
echo "🔍 Running health checks..."
./scripts/health-check.sh

# Database migrations
echo "🗄️ Running database migrations..."
./scripts/migrate.sh

echo "✅ Staging deployment complete!"
echo "🌐 Services available at:"
echo "   - Agent Service: http://localhost:8001"
echo "   - Integration Service: http://localhost:8002"
echo "   - Context Service: http://localhost:8003"
echo "   - Workflow Service: http://localhost:8004"
echo "   - Authentication Service: http://localhost:8005"
echo "   - Notification Service: http://localhost:8006"
echo "   - Consul UI: http://localhost:8500" 