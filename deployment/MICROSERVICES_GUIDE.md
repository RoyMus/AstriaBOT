# Microservices Architecture Documentation

## Overview

Your WhatsApp Astria Bot has been converted from a monolithic Azure Function App to a **microservices architecture** with independent, scalable services.

## Microservices

### 1. **Message Service** 🔵
- **Responsibility**: WhatsApp message processing, state machine management
- **Triggers**: HTTP webhook from Meta/WhatsApp
- **Endpoint**: `POST /SmsReceived`
- **Port**: 7071 (local), 80 (container)
- **Scaling**: 3-10 replicas (HPA based on CPU/Memory)

### 2. **Image Service** 🖼️
- **Responsibility**: Image processing, media handling, pack updates
- **Triggers**: Webhooks from Astria API
- **Endpoints**: 
  - `POST /pack-tune-received` - Process generated images
  - `POST /update-images` - Update pack images in Azure Storage
- **Port**: 7072 (local), 80 (container)
- **Scaling**: 2+ replicas

### 3. **Payment Service** 💳
- **Responsibility**: Payment processing and webhooks
- **Triggers**: Payment provider webhooks
- **Endpoint**: `POST /payment-received`
- **Port**: 7073 (local), 80 (container)
- **Scaling**: 2+ replicas

### 4. **Maintenance Service** 🧹
- **Responsibility**: Scheduled database cleanup
- **Triggers**: Cron job (Weekly - Wednesday 4:00 AM UTC)
- **Port**: 80 (container only)
- **Scaling**: Single instance, CronJob

## Shared Components

### Event Broker
Located in `shared/event_broker.py`, handles inter-service communication:
- **Production**: Azure Service Bus (event-driven, asynchronous)
- **Development**: Local in-memory broker

### Common Models
Located in `shared/models.py`:
- `UserModel` - User state and data
- `MessageModel` - Message structure
- `PackModel` - Pack information
- `RatingModel` - User ratings

## Local Development

### Prerequisites
```bash
- Docker Desktop
- Python 3.11+
- Azure CLI
- .env file with configuration
```

### Environment Variables
```bash
# .env
ENVIRONMENT=development
DATABASE_URL=postgresql://user:password@localhost:5432/astria_bot
ASTRIA_API_URL=https://api.astria.ai
ASTRIA_API_KEY=your_key_here
WHATSAPP_VERIFY_TOKEN=your_token
SERVICEBUS_CONNECTION_STRING=your_connection_string
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
```

### Start All Services
```bash
docker-compose up -d
```

Services will be available at:
- Message Service: http://localhost:7071
- Image Service: http://localhost:7072
- Payment Service: http://localhost:7073

### View Logs
```bash
docker-compose logs -f message-service
docker-compose logs -f image-service
```

### Stop Services
```bash
docker-compose down
```

## Production Deployment

### Azure Container Registry Setup
```bash
az acr create --resource-group mygroup --name acryourregistry --sku Basic

# Push images
docker tag message-service:latest acryourregistry.azurecr.io/astria-bot/message-service:latest
docker push acryourregistry.azurecr.io/astria-bot/message-service:latest
```

### Kubernetes Deployment
```bash
# Create namespace
kubectl create namespace astria-bot

# Create secrets
kubectl apply -f deployment/kubernetes/01-config.yaml

# Deploy all services
kubectl apply -f deployment/kubernetes/02-message-service.yaml
kubectl apply -f deployment/kubernetes/03-image-service.yaml
kubectl apply -f deployment/kubernetes/04-payment-service.yaml
kubectl apply -f deployment/kubernetes/05-maintenance-service.yaml
kubectl apply -f deployment/kubernetes/06-ingress.yaml

# Check status
kubectl get pods -n astria-bot
kubectl get svc -n astria-bot
```

## Inter-Service Communication

Services communicate through **Azure Service Bus** (production) or **local event broker** (development).

### Event Flow Example

```
User sends WhatsApp message
    ↓
Message Service receives webhook
    ↓
Publishes: UserMessageReceivedEvent
    ↓
Image Service listens (if image upload)
    ↓
Processes images, publishes: ImageProcessedEvent
    ↓
Message Service receives event, updates user
    ↓
Sends WhatsApp response
```

## Scaling Strategy

### Horizontal Scaling
- **Message Service**: 3-10 replicas based on message load
- **Image Service**: 2-5 replicas based on processing load
- **Payment Service**: 2-3 replicas (lower traffic)
- **Maintenance Service**: 1 replica (scheduled, non-concurrent)

### Vertical Scaling
Adjust resource requests/limits in Kubernetes manifests:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

## Monitoring & Logging

### Azure Monitor Integration
Each service integrates with Azure Application Insights for:
- Request tracking
- Performance monitoring
- Error logging
- Custom metrics

### Health Checks
All services expose:
- `/health` - Liveness probe
- `/ready` - Readiness probe

## Benefits of Microservices

✅ **Independent Scaling** - Scale only services that need it  
✅ **Fault Isolation** - Service failure doesn't cascade  
✅ **Technology Flexibility** - Update services independently  
✅ **Team Agility** - Teams own specific services  
✅ **Deployment Speed** - Deploy single service without full redeploy  
✅ **Resource Efficiency** - Right-size each service  

## Migration from Monolith

The original `function_app.py` routes remain intact in each service:
- Message processing → message-service
- Image handling → image-service
- Payment processing → payment-service
- Database maintenance → maintenance-service

**No breaking changes** to existing webhooks - just point them to the correct service.

## Troubleshooting

### Service won't start
```bash
docker-compose logs message-service
# Check environment variables and database connection
```

### Event broker connection issues
```bash
# Verify Service Bus connection string
az servicebus namespace show --name your-namespace
```

### Database migration
```bash
# Run migrations on each service startup if needed
python -m alembic upgrade head
```

## Next Steps

1. ✅ Set up Azure Service Bus for event-driven architecture
2. ✅ Configure Azure Container Registry
3. ✅ Deploy to Azure Kubernetes Service (AKS)
4. ✅ Set up monitoring with Application Insights
5. ✅ Configure CI/CD pipeline (GitHub Actions/Azure DevOps)
