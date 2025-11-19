@REM Deployment setup script for microservices (Windows)

@echo off
echo 🚀 WhatsApp Astria Bot - Microservices Deployment Setup
echo =======================================================

REM Check prerequisites
echo ✓ Checking prerequisites...

where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ✗ Docker is not installed
    exit /b 1
)

REM Setup environment
echo.
echo 📝 Setting up environment...

if not exist .env (
    echo Creating .env from .env.example
    copy .env.example .env
    echo ⚠️  Please update .env with your configuration
)

REM Build Docker images
echo.
echo 🐳 Building Docker images...

docker build -f services\message-service\Dockerfile -t message-service:latest .
docker build -f services\image-service\Dockerfile -t image-service:latest .
docker build -f services\payment-service\Dockerfile -t payment-service:latest .
docker build -f services\maintenance-service\Dockerfile -t maintenance-service:latest .

echo ✓ Docker images built

REM Start services with docker-compose
echo.
echo ▶️  Starting services with docker-compose...

docker-compose up -d

echo.
echo ✅ All services started!
echo.
echo 📊 Service Status:
docker-compose ps

echo.
echo 🔗 Service URLs:
echo   Message Service:     http://localhost:7071
echo   Image Service:       http://localhost:7072
echo   Payment Service:     http://localhost:7073

echo.
echo 📋 View logs with:
echo   docker-compose logs -f [service-name]
echo.
echo ⏹️  Stop services with:
echo   docker-compose down
