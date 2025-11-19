# WhatsApp Astria BOT

A microservices-based WhatsApp bot for AI model training and image processing, built with Azure Functions, Meta's WhatsApp Cloud API, and Astria AI integration.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Services](#services)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

## Overview

WhatsApp Astria BOT is an intelligent WhatsApp bot that guides users through an AI model training workflow. Users interact via WhatsApp to:

1. **Submit Images** - Upload photos to create a training dataset
2. **Tune AI Models** - Train custom AI models using Astria API
3. **Get Feedback** - Receive AI-generated feedback on their images
4. **Make Payments** - Seamlessly integrate payments for premium features

The bot uses a **state machine pattern** to manage user workflows and a **microservices architecture** for independent scaling of each component.

## Features

- **WhatsApp Integration** - Native Meta WhatsApp Cloud API support
- **AI Model Training** - Astria API integration for custom model tuning
- **Image Processing** - OpenCV-based image analysis and transformation
- **Payment Processing** - Webhook-based payment handling
- **Event-Driven** - Azure Service Bus for inter-service communication
- **Database Persistence** - PostgreSQL for user data and state management
- **State Machine** - Clean user state management (New, PicturesLoaded, TuneReady, WritingFeedback)
- **Containerized** - Docker & Kubernetes ready
- **Production-Ready** - Comprehensive logging, error handling, and monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Meta WhatsApp Cloud API                  │
└────────────────┬────────────────────────────────────────────┘
                 │
         ┌───────▼────────┐
         │ Message Service │
         │ (Azure Function)│
         └───────┬────────┘
                 │
    ┌────────────┼────────────┬──────────────┐
    │            │            │              │
┌───▼──────┐ ┌───▼──────┐ ┌──▼──────┐ ┌────▼────┐
│  Image   │ │ Payment  │ │Database │ │  Event  │
│ Service  │ │ Service  │ │(PostgreSQL)
│ Service  │ │(Azure Fn)│ │         │ │  Broker │
└──────────┘ └──────────┘ └─────────┘ │(Svc Bus)│
                                      └─────────┘
         ┌────────────────┐
         │ Astria API     │
         │ (AI Training)  │
         └────────────────┘
```

### Service Communication

- **Synchronous**: Direct REST calls between services
- **Asynchronous**: Azure Service Bus events for loosely coupled operations
- **Development**: Local event broker for testing without Azure dependencies

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **API Gateway** | Meta WhatsApp Cloud API |
| **Functions** | Azure Functions (Python 3.9+) |
| **Message Queue** | Azure Service Bus |
| **Database** | PostgreSQL 13+ |
| **AI Training** | Astria API |
| **Image Processing** | OpenCV, Pillow, MoviePy |
| **Containers** | Docker & Docker Compose |
| **Orchestration** | Kubernetes (AKS) |
| **IaC** | Helm Charts, Kubernetes YAML |
| **HTTP Client** | aiohttp with retry logic |

## Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- PostgreSQL 13+ (or use Docker)
- Azure Subscription (for production)
- Meta WhatsApp Business Account
- Astria API account

### 1. Clone & Setup

```bash
git clone <repository-url>
cd WhatsappAstriaBOT
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Meta WhatsApp API
WHATSAPP_API_URL=https://graph.instagram.com/v18.0
WHATSAPP_NUMBER_ID=your_phone_number_id
WHATSAPP_API_KEY=your_business_account_access_token
WHATSAPP_VERIFY_TOKEN=your_verify_token

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/astria_bot

# Astria API
ASTRIA_API_KEY=your_astria_api_key
ASTRIA_API_URL=https://api.astria.ai

# Azure Service Bus (Production)
SERVICEBUS_CONNECTION_STRING=Endpoint=sb://...

# Payment Webhook Secret
PAYMENT_WEBHOOK_SECRET=your_webhook_secret
```

### 3. Start Services Locally

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database
- Message Service (port 7070)
- Image Service (port 7071)
- Payment Service (port 7073)
- Maintenance Service (scheduled)

### 4. Test the Setup

```bash
# Check all services are running
docker-compose ps

# View service logs
docker-compose logs -f message-service

# Test message webhook
curl -X POST http://localhost:7070/SmsReceived \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "1234567890",
            "type": "text",
            "text": {"body": "Hello bot"}
          }]
        }
      }]
    }]
  }'
```

## Project Structure

```
WhatsappAstriaBOT/
├── app/                          # Core application logic
│   ├── message_processor.py       # Message routing & state dispatch
│   ├── state_handlers.py          # State machine implementation
│   ├── image_processors.py        # Image processing logic
│   ├── astria_images_video_processors.py
│   └── payment_processors.py      # Payment logic
│
├── services/                      # Microservices
│   ├── message-service/           # WhatsApp message handler
│   ├── image-service/             # Image processing service
│   ├── payment-service/           # Payment webhook handler
│   └── maintenance-service/       # Database maintenance
│
├── shared/                        # Shared libraries
│   ├── event_broker.py            # Event communication (Service Bus + local)
│   ├── models.py                  # Pydantic data models
│   └── __init__.py
│
├── Utils/                         # Utility modules
│   ├── WhatsappClient.py          # Meta WhatsApp API client
│   ├── WhatsappWrapper.py         # High-level WhatsApp operations
│   ├── dbClient.py                # Database client
│   ├── constants.py               # Configuration constants
│   ├── utils.py                   # Helper functions
│   ├── aiohttp_retry.py           # HTTP retry logic
│   └── states.py                  # User state definitions
│
├── db/                            # Database
│   ├── CreateDB.py                # Schema initialization
│   ├── dbConfig.py                # Database configuration
│   └── db_maintenance.py          # Maintenance tasks
│
├── deployment/                    # Production deployment
│   ├── docker/                    # Dockerfiles for each service
│   ├── kubernetes/                # K8s manifests
│   └── helm/                      # Helm charts (optional)
│
├── tests/                         # Test scripts
│   ├── Test.py
│   ├── TestWhatsappMessage.py
│   └── ...
│
├── docker-compose.yml             # Local development setup
├── requirements.txt               # Root dependencies
└── README.md                      # This file
```

## Services

### Message Service
**Port**: 7070  
**Function**: Receives WhatsApp messages and routes them based on user state

**Endpoints**:
- `POST /SmsReceived` - WhatsApp webhook
- `GET /health` - Health check

**Handles**:
- Text messages
- Media (images, videos)
- Interactive replies (buttons, lists)

### Image Service
**Port**: 7071  
**Function**: Processes images and manages AI model training

**Endpoints**:
- `POST /pack-tune-received` - Astria training callback
- `POST /update-images` - Image update notifications
- `GET /health` - Health check

**Handles**:
- Image validation & processing
- Training package management
- Astria API callbacks

### Payment Service
**Port**: 7073  
**Function**: Processes payment webhooks

**Endpoints**:
- `POST /payment-received` - Payment webhook
- `GET /health` - Health check

**Handles**:
- Payment validation
- User account updates
- Payment confirmations

### Maintenance Service
**Schedule**: Weekly (Wednesday 4:00 AM UTC)  
**Function**: Cleans up database and maintains data integrity

**Tasks**:
- Expired session cleanup
- Database optimization
- Backup triggers

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `WHATSAPP_API_URL` | Meta Graph API endpoint | `https://graph.instagram.com/v18.0` |
| `WHATSAPP_NUMBER_ID` | Your WhatsApp Business phone number ID | `120XXXXXXXXX` |
| `WHATSAPP_API_KEY` | Business account access token | `EAA...` |
| `WHATSAPP_VERIFY_TOKEN` | Webhook verify token | `your_token` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `ASTRIA_API_KEY` | Astria.ai API key | `your_key` |
| `ASTRIA_API_URL` | Astria.ai API endpoint | `https://api.astria.ai` |
| `ENVIRONMENT` | Deployment environment | `development` \| `production` |
| `SERVICEBUS_CONNECTION_STRING` | Azure Service Bus connection | `Endpoint=sb://...` |

### Database Schema

The bot uses a relational schema with tables for:
- **Users** - User profiles and state
- **Messages** - Message history
- **Packs** - AI training packages
- **Ratings** - User feedback ratings

Run database initialization:

```bash
python db/CreateDB.py
```

## Development

### Local Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start services with Docker Compose
docker-compose up -d

# Run a specific service with live reload
cd services/message-service
func start --python

# Run tests
python tests/Test.py
```

### Code Structure

#### State Machine Pattern

User states are managed through a state machine:

```python
from app.state_handlers import StateHandlerFactory, states

# Get appropriate handler for user state
handler = StateHandlerFactory.create(user_state)
await handler.handle_text_message(user_id, message_text)
```

**States**:
- `NEW` - First time user, collecting initial images
- `PICTURES_LOADED` - Images submitted, ready to tune model
- `TUNE_READY` - Model trained, waiting for results
- `WRITING_FEEDBACK` - Providing feedback on results

#### Event-Driven Communication

```python
from shared.event_broker import Event, EventPublisher

# Publish an event
event = UserMessageReceivedEvent(data={...})
await event_broker.publish(event)

# Subscribe to events
async def on_payment_received(event):
    # Handle payment event
    pass
```

### Running Tests

```bash
# Test WhatsApp message handling
python tests/TestWhatsappMessage.py

# Test Astria pack retrieval
python tests/astriaGetPacks.py

# View database
python tests/ViewDB.py
```

## Deployment

### Azure Functions Deployment

```bash
# Install Azure Functions Core Tools
# https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local

# Deploy message service
cd services/message-service
func azure functionapp publish <YOUR_FUNCTION_APP_NAME>
```

### Docker Deployment

```bash
# Build images
docker build -t myregistry/message-service services/message-service
docker build -t myregistry/image-service services/image-service
docker build -t myregistry/payment-service services/payment-service

# Push to registry
docker push myregistry/message-service
docker push myregistry/image-service
docker push myregistry/payment-service
```

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace astria-bot

# Apply configurations
kubectl apply -f deployment/kubernetes/01-configmap.yaml
kubectl apply -f deployment/kubernetes/02-secrets.yaml
kubectl apply -f deployment/kubernetes/03-message-service.yaml
kubectl apply -f deployment/kubernetes/04-payment-service.yaml
kubectl apply -f deployment/kubernetes/05-image-service.yaml
kubectl apply -f deployment/kubernetes/06-maintenance-service.yaml

# Verify deployment
kubectl get pods -n astria-bot
kubectl logs -f deployment/message-service -n astria-bot
```

### Environment Setup Scripts

We provide platform-specific setup scripts:

```bash
# macOS/Linux
bash setup.sh

# Windows PowerShell
.\setup.ps1
```

## API Documentation

### WhatsApp Webhook Format

**Incoming Message**:
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "messages": [{
          "from": "1234567890",
          "id": "wamid.xxx",
          "timestamp": "1234567890",
          "type": "text",
          "text": {
            "body": "User message"
          }
        }]
      }
    }]
  }]
}
```

**Outgoing Message**:
```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "text",
  "text": {
    "body": "Bot response"
  }
}
```

### Event Schema

```python
class Event(BaseModel):
    event_type: str
    timestamp: datetime
    data: dict
    source_service: str
```

**Event Types**:
- `UserMessageReceivedEvent`
- `ImageProcessedEvent`
- `PaymentReceivedEvent`
- `TuneCreatedEvent`
- `PackImagesUpdatedEvent`

## Monitoring & Logging

### Service Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f message-service

# Kubernetes
kubectl logs -f deployment/message-service -n astria-bot
```

### Application Logs

Logs are written to stdout and include:
- Request/response details
- Database operations
- API calls to external services (Meta, Astria)
- State transitions
- Error traces

## 🐛 Troubleshooting

### Common Issues

**Service not starting**
```bash
# Check logs
docker-compose logs message-service

# Verify environment variables
env | grep WHATSAPP
```

**Database connection failed**
```bash
# Verify PostgreSQL is running
docker-compose ps

# Check connection string
psql $DATABASE_URL
```

**WhatsApp webhooks not received**
- Verify webhook URL is publicly accessible
- Check webhook token matches in settings
- Verify phone number ID is correct

**Astria API errors**
- Confirm API key is valid
- Check API quota limits
- Verify image format requirements (JPEG/PNG)

### Debug Mode

Enable verbose logging:

```bash
export LOG_LEVEL=DEBUG
docker-compose up
```

## Support & Contributions

For issues, questions, or contributions:

1. Check existing documentation in `/docs`
2. Review test files for usage examples
3. Open an issue on the repository

## License

MIT License

## Notes

- This project uses the **state machine pattern** for clean user workflow management
- **Microservices architecture** enables independent scaling and deployment
- **Event-driven communication** with Azure Service Bus for production reliability
- **Local development mode** uses in-memory event broker for faster iterations

---

**Last Updated**: November 2025  
**Architecture Version**: 2.0 (Microservices)  
**Meta API Version**: v18.0
