# WhatsApp Astria Bot - Microservices Architecture

Your monolithic Azure Function App has been successfully converted to a **production-ready microservices architecture**.

## 📦 Project Structure

```
WhatsappAstriaBOT/
├── services/                          # Independent microservices
│   ├── message-service/               # WhatsApp message processing (3-10 replicas)
│   │   ├── function_app.py
│   │   ├── app/
│   │   │   ├── message_handler.py
│   │   │   └── message_processor.py   # (reuses existing)
│   │   ├── state_handlers.py          # State machine (reuses existing)
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── image-service/                 # Image & media processing (2-5 replicas)
│   │   ├── function_app.py
│   │   ├── app/
│   │   │   ├── image_handler.py
│   │   │   └── image_processors.py    # (reuses existing)
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── payment-service/               # Payment webhooks (2-3 replicas)
│   │   ├── function_app.py
│   │   ├── app/
│   │   │   ├── payment_handler.py
│   │   │   └── payment_processors.py  # (reuses existing)
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── maintenance-service/           # DB cleanup (1 CronJob)
│       ├── function_app.py
│       ├── app/
│       │   └── maintenance_handler.py
│       ├── requirements.txt
│       └── Dockerfile
│
├── shared/                            # Shared code & configuration
│   ├── event_broker.py               # Inter-service communication
│   ├── models.py                     # Common data models
│   └── requirements.txt              # Shared dependencies
│
├── deployment/                        # Deployment configurations
│   ├── MICROSERVICES_GUIDE.md        # Detailed guide
│   ├── setup.sh                      # Linux/Mac setup script
│   ├── setup.bat                     # Windows setup script
│   └── kubernetes/                   # K8s manifests
│       ├── 01-config.yaml           # ConfigMaps & Secrets
│       ├── 02-message-service.yaml   # Message service (3-10 replicas, HPA)
│       ├── 03-image-service.yaml    # Image service (2+ replicas)
│       ├── 04-payment-service.yaml   # Payment service (2+ replicas)
│       ├── 05-maintenance-service.yaml  # CronJob
│       └── 06-ingress.yaml          # Ingress rules
│
├── docker-compose.yml                # Local development
├── .env.example                      # Environment template
├── Utils/                            # (reused - unchanged)
├── db/                               # (reused - unchanged)
└── function_app.py                   # (original monolith - deprecated)
```

## 🚀 Quick Start

### Option 1: Local Development with Docker Compose

**Prerequisites**: Docker Desktop, Python 3.11+

```bash
# 1. Clone or navigate to project
cd WhatsappAstriaBOT

# 2. Setup environment
cp .env.example .env
# Edit .env with your API keys and database URL

# 3. Start all services
docker-compose up -d

# 4. Verify services are running
docker-compose ps

# 5. View logs
docker-compose logs -f message-service
```

**Services available at:**
- Message Service: http://localhost:7071
- Image Service: http://localhost:7072
- Payment Service: http://localhost:7073

### Option 2: Automated Setup (One Command)

**Linux/Mac:**
```bash
cd deployment
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
cd deployment
setup.bat
```

### Option 3: Production Deployment (Azure Kubernetes Service)

See [deployment/MICROSERVICES_GUIDE.md](deployment/MICROSERVICES_GUIDE.md) for:
- Azure Container Registry setup
- Kubernetes cluster creation
- Service deployment
- Monitoring configuration

## 📊 Architecture Overview

```
                              ┌─────────────────────┐
                              │  Meta/WhatsApp API  │
                              └──────────┬──────────┘
                                         │
                                    HTTP POST
                                         │
                    ┌────────────────────▼────────────────────┐
                    │    Message Service (3-10 replicas)      │
                    │  - Processes WhatsApp webhooks          │
                    │  - State machine logic                  │
                    │  - User management                      │
                    └────────────────┬─────────────────────────┘
                                     │
                    ┌────────────────┴─────────────────┐
                    │    Azure Service Bus             │
                    │  (Event-driven messaging)        │
                    └──┬─────────────────────────────┬─┘
                       │                             │
        ┌──────────────▼──────────────┐  ┌──────────▼────────────────┐
        │  Image Service              │  │  Payment Service         │
        │  (2-5 replicas)             │  │  (2-3 replicas)          │
        │  - Image processing         │  │  - Payment webhooks      │
        │  - Media handling           │  │  - Billing logic         │
        └─────────────────────────────┘  └──────────────────────────┘
        
        ┌─────────────────────────────────────────────────────────────┐
        │  Maintenance Service (1 CronJob)                           │
        │  - Database cleanup (weekly)                               │
        └─────────────────────────────────────────────────────────────┘
```

## 🔄 Service Communication

Services communicate through **event-driven architecture**:

- **Production**: Azure Service Bus (async, decoupled, scalable)
- **Development**: In-memory event broker (same interface)

### Example Event Flow

```python
# Message Service publishes event
event = UserMessageReceivedEvent(
    event_type="user_message_received",
    data={"user_id": "123", "message": "Hello"},
    source_service="message-service"
)
await event_broker.publish(event)

# Image Service subscribes
async def on_user_message(event: Event):
    if event_contains_image:
        await process_image()

await event_broker.subscribe("user_message_received", on_user_message)
```

## 📈 Scaling

### Auto-Scaling (Kubernetes)
- **Message Service**: 3-10 replicas based on CPU (70%) and Memory (80%)
- **Image Service**: 2-5 replicas based on workload
- **Payment Service**: 2-3 replicas (consistent traffic)
- **Maintenance**: 1 instance (scheduled, non-concurrent)

### Manual Scaling
```bash
# Scale message service to 5 replicas
kubectl scale deployment message-service --replicas=5 -n astria-bot
```

## 🔧 Configuration

All services use environment variables:

```bash
ENVIRONMENT=production                           # production|development
DATABASE_URL=postgresql://...                    # PostgreSQL connection
ASTRIA_API_URL=https://api.astria.ai            # Astria API endpoint
ASTRIA_API_KEY=xxx                              # Astria authentication
WHATSAPP_VERIFY_TOKEN=xxx                       # Meta verification
SERVICEBUS_CONNECTION_STRING=xxx                # Azure Service Bus
TWILIO_ACCOUNT_SID=xxx                          # Twilio credentials
TWILIO_AUTH_TOKEN=xxx                           # Twilio credentials
```

## 📋 Webhook Routing

Update your webhook endpoints on Meta, Astria, and payment provider:

| Service | Endpoint | Method |
|---------|----------|--------|
| Message | `/SmsReceived` | POST |
| Image | `/pack-tune-received` | POST |
| Image | `/update-images` | POST |
| Payment | `/payment-received` | POST |

## 🧪 Testing

### Health Checks
```bash
# Message Service
curl http://localhost:7071/health
curl http://localhost:7071/ready

# Image Service
curl http://localhost:7072/health
```

### Test Message Processing
```bash
curl -X POST http://localhost:7071/SmsReceived \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "From": "+1234567890",
      "Body": "Hello"
    }]
  }'
```

## 📚 Documentation

- **[Detailed Microservices Guide](deployment/MICROSERVICES_GUIDE.md)** - Complete setup, deployment, and troubleshooting
- **[Event Broker Documentation](shared/event_broker.py)** - Inter-service communication patterns
- **[Common Models](shared/models.py)** - Shared data structures

## 🔄 Migration from Monolith

**Existing code reused:**
- `app/message_processor.py` - Message processing logic
- `app/state_handlers.py` - State machine
- `app/image_processors.py` - Image processing
- `app/payment_processors.py` - Payment logic
- `db/db_maintenance.py` - Database cleanup
- `Utils/` - Utilities (unchanged)
- `db/` - Database config (unchanged)

**New abstractions:**
- `shared/event_broker.py` - Event-driven communication
- Service handlers route requests to existing processors
- **No breaking changes** to business logic

## ✨ Benefits

✅ **Independent Scaling** - Scale only what you need  
✅ **Fault Isolation** - One service down ≠ entire system down  
✅ **Deployment Agility** - Deploy single service without full redeploy  
✅ **Technology Flexibility** - Update services independently  
✅ **Team Scalability** - Teams own specific services  
✅ **Resource Efficiency** - Right-size each service  
✅ **High Availability** - Multiple replicas with load balancing  
✅ **Observability** - Monitor each service independently  

## 🆘 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs [service-name]

# Verify environment variables
cat .env

# Check database connection
psql $DATABASE_URL -c "SELECT 1"
```

### Event broker not working
```bash
# Verify Service Bus connection (production)
az servicebus namespace show --name your-namespace

# Check local broker in development
docker-compose logs message-service | grep "event"
```

### Performance issues
```bash
# Check resource usage
kubectl top pods -n astria-bot

# Scale up replica count
kubectl scale deployment message-service --replicas=5 -n astria-bot
```

## 📞 Support

For detailed guides and troubleshooting, see:
- [deployment/MICROSERVICES_GUIDE.md](deployment/MICROSERVICES_GUIDE.md)
- Service-specific logs: `docker-compose logs -f [service-name]`

## 📄 License

Same as original project

---

**Migration complete!** Your monolith is now a scalable, maintainable microservices architecture. 🎉
