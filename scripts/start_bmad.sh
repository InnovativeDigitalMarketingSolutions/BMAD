#!/bin/bash

# BMAD System Startup Script
# This script starts all BMAD microservices

set -e

echo "🚀 Starting BMAD System..."
echo "=========================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env files exist
echo "📋 Checking environment files..."
for service in auth-service notification-service agent-service workflow-service context-service integration-service api-gateway; do
    if [ ! -f "microservices/$service/.env" ]; then
        echo "❌ Missing .env file for $service"
        echo "💡 Run: python setup_database_connection.py"
        exit 1
    fi
done

echo "✅ All environment files found"

# Create monitoring directories if they don't exist
echo "📊 Setting up monitoring..."
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources

# Create basic Grafana datasource
cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
services=(
    "bmad-redis:6379"
    "bmad-api-gateway:8000"
    "bmad-auth-service:8001"
    "bmad-notification-service:8002"
    "bmad-agent-service:8003"
    "bmad-workflow-service:8004"
    "bmad-context-service:8005"
    "bmad-integration-service:8006"
    "bmad-prometheus:9090"
    "bmad-grafana:3000"
)

for service in "${services[@]}"; do
    container_name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if docker ps | grep -q $container_name; then
        echo "✅ $container_name is running"
    else
        echo "❌ $container_name is not running"
    fi
done

echo ""
echo "🎉 BMAD System is starting up!"
echo ""
echo "📊 Service URLs:"
echo "   API Gateway:     http://localhost:8000"
echo "   Auth Service:    http://localhost:8001"
echo "   Notification:    http://localhost:8002"
echo "   Agent Service:   http://localhost:8003"
echo "   Workflow:        http://localhost:8004"
echo "   Context:         http://localhost:8005"
echo "   Integration:     http://localhost:8006"
echo "   Prometheus:      http://localhost:9090"
echo "   Grafana:         http://localhost:3000 (admin/admin)"
echo ""
echo "📋 Useful commands:"
echo "   View logs:       docker-compose logs -f"
echo "   Stop services:   docker-compose down"
echo "   Restart:         docker-compose restart"
echo "   Status:          docker-compose ps"
echo ""
echo "🔗 API Documentation: http://localhost:8000/docs" 