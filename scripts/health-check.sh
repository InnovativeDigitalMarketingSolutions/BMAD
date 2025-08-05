#!/bin/bash
# health-check.sh
# BMAD Microservices Health Check Script

set -e

SERVICES=(
    "http://localhost:8001/health"
    "http://localhost:8002/health"
    "http://localhost:8003/health"
    "http://localhost:8004/health"
    "http://localhost:8005/health"
    "http://localhost:8006/health"
)

SERVICE_NAMES=(
    "Agent Service"
    "Integration Service"
    "Context Service"
    "Workflow Service"
    "Authentication Service"
    "Notification Service"
)

echo "🔍 Running health checks for BMAD microservices..."

FAILED_SERVICES=()

for i in "${!SERVICES[@]}"; do
    service_url="${SERVICES[$i]}"
    service_name="${SERVICE_NAMES[$i]}"
    
    echo -n "Checking $service_name... "
    
    # Try to get response with timeout
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 $service_url || echo "000")
    
    if [ $response -eq 200 ]; then
        echo "✅ HEALTHY"
    else
        echo "❌ UNHEALTHY (HTTP $response)"
        FAILED_SERVICES+=("$service_name")
    fi
done

# Check database connectivity
echo -n "Checking PostgreSQL... "
if docker exec bmad-staging_postgres_1 pg_isready -U bmad_user > /dev/null 2>&1; then
    echo "✅ HEALTHY"
else
    echo "❌ UNHEALTHY"
    FAILED_SERVICES+=("PostgreSQL")
fi

# Check Redis connectivity
echo -n "Checking Redis... "
if docker exec bmad-staging_redis_1 redis-cli ping > /dev/null 2>&1; then
    echo "✅ HEALTHY"
else
    echo "❌ UNHEALTHY"
    FAILED_SERVICES+=("Redis")
fi

# Check Consul
echo -n "Checking Consul... "
if curl -s http://localhost:8500/v1/status/leader > /dev/null 2>&1; then
    echo "✅ HEALTHY"
else
    echo "❌ UNHEALTHY"
    FAILED_SERVICES+=("Consul")
fi

# Summary
echo ""
if [ ${#FAILED_SERVICES[@]} -eq 0 ]; then
    echo "✅ All services healthy!"
    exit 0
else
    echo "❌ Health check failed for the following services:"
    for service in "${FAILED_SERVICES[@]}"; do
        echo "   - $service"
    done
    echo ""
    echo "🔧 Troubleshooting tips:"
    echo "   - Check service logs: docker-compose logs <service-name>"
    echo "   - Check environment variables: docker-compose config"
    echo "   - Check port conflicts: netstat -tulpn | grep :8001"
    echo "   - Restart services: docker-compose restart"
    exit 1
fi 