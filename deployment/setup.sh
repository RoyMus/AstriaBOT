#!/bin/bash
# Deployment setup script for microservices

set -e

echo "🚀 WhatsApp Astria Bot - Microservices Deployment Setup"
echo "======================================================="

# Check prerequisites
echo "✓ Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "✗ Docker is not installed"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "⚠️  kubectl not found - some features disabled"
fi

# Setup environment
echo ""
echo "📝 Setting up environment..."

if [ ! -f .env ]; then
    echo "Creating .env from .env.example"
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Build Docker images
echo ""
echo "🐳 Building Docker images..."

docker build -f services/message-service/Dockerfile -t message-service:latest .
docker build -f services/image-service/Dockerfile -t image-service:latest .
docker build -f services/payment-service/Dockerfile -t payment-service:latest .
docker build -f services/maintenance-service/Dockerfile -t maintenance-service:latest .

echo "✓ Docker images built"

# Start services with docker-compose
echo ""
echo "▶️  Starting services with docker-compose..."

docker-compose up -d

echo ""
echo "✅ All services started!"
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🔗 Service URLs:"
echo "  Message Service:     http://localhost:7071"
echo "  Image Service:       http://localhost:7072"
echo "  Payment Service:     http://localhost:7073"

echo ""
echo "📋 View logs with:"
echo "  docker-compose logs -f [service-name]"
echo ""
echo "⏹️  Stop services with:"
echo "  docker-compose down"
