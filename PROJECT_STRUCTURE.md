# Project Structure Overview

```
WhatsappAstriaBOT/
│
├── 📁 services/                           # Independent microservices
│   │
│   ├── 📁 message-service/               # WhatsApp Message Processing
│   │   ├── function_app.py               # Azure Functions entry point
│   │   ├── requirements.txt              # Service dependencies
│   │   ├── Dockerfile                    # Container image
│   │   └── 📁 app/
│   │       ├── message_handler.py        # Orchestrator
│   │       └── message_processor.py      # (reused from root)
│   │
│   ├── 📁 image-service/                 # Image & Media Processing
│   │   ├── function_app.py               # Azure Functions entry point
│   │   ├── requirements.txt              # Service dependencies
│   │   ├── Dockerfile                    # Container image
│   │   └── 📁 app/
│   │       ├── image_handler.py          # Orchestrator
│   │       ├── image_processors.py       # (reused from root)
│   │       └── astria_images_video_processors.py
│   │
│   ├── 📁 payment-service/               # Payment Processing
│   │   ├── function_app.py               # Azure Functions entry point
│   │   ├── requirements.txt              # Service dependencies
│   │   ├── Dockerfile                    # Container image
│   │   └── 📁 app/
│   │       ├── payment_handler.py        # Orchestrator
│   │       └── payment_processors.py     # (reused from root)
│   │
│   └── 📁 maintenance-service/           # Database Maintenance
│       ├── function_app.py               # Azure Functions entry point
│       ├── requirements.txt              # Service dependencies
│       ├── Dockerfile                    # Container image
│       └── 📁 app/
│           ├── maintenance_handler.py    # Orchestrator
│           └── db_maintenance.py         # (reused from root)
│
├── 📁 shared/                            # Shared Code & Libraries
│   ├── event_broker.py                   # Event-driven communication
│   │                                      # - Azure Service Bus (prod)
│   │                                      # - Local broker (dev)
│   ├── models.py                         # Shared Pydantic models
│   │                                      # - UserModel
│   │                                      # - MessageModel
│   │                                      # - PackModel
│   │                                      # - RatingModel
│   └── requirements.txt                  # Shared dependencies
│
├── 📁 deployment/                        # Deployment Configurations
│   ├── MICROSERVICES_GUIDE.md           # 📖 Detailed guide
│   ├── setup.sh                          # 🔧 Linux/Mac auto-setup
│   ├── setup.bat                         # 🔧 Windows auto-setup
│   └── 📁 kubernetes/
│       ├── 01-config.yaml                # ConfigMaps & Secrets
│       ├── 02-message-service.yaml       # Message service (3-10 replicas, HPA)
│       ├── 03-image-service.yaml         # Image service (2+ replicas)
│       ├── 04-payment-service.yaml       # Payment service (2+ replicas)
│       ├── 05-maintenance-service.yaml   # Maintenance CronJob
│       └── 06-ingress.yaml               # Ingress rules
│
├── 📁 Utils/                             # Utilities (reused - unchanged)
│   ├── constants.py
│   ├── dbClient.py
│   ├── message_ids.py
│   ├── states.py
│   ├── utils.py
│   ├── WhatsappClient.py
│   ├── WhatsappWrapper.py
│   └── aiohttp_retry.py
│
├── 📁 db/                                # Database (reused - unchanged)
│   ├── CreateDB.py
│   ├── db_maintenance.py
│   ├── dbConfig.py
│   └── __pycache__/
│
├── 📁 app/                               # Original app code (for reference)
│   ├── astria_images_video_processors.py # Used by image-service
│   ├── image_processors.py               # Used by image-service
│   ├── message_processor.py              # Used by message-service
│   ├── payment_processors.py             # Used by payment-service
│   ├── state_handlers.py                 # Used by message-service
│   └── __pycache__/
│
├── 📁 tests/                             # Test suite (unchanged)
│   ├── astriaGetPacks.py
│   ├── PromptTest.py
│   ├── SendTwilioMessage.py
│   ├── Test.py
│   ├── TestField.py
│   ├── TestWhatsappMessage.py
│   ├── TuneModel.py
│   ├── ViewDB.py
│   └── (other tests)
│
├── 📄 MICROSERVICES_README.md            # ⭐ Read this first!
├── 📄 MIGRATION_SUMMARY.md               # 📋 Migration overview
├── 📄 MIGRATION_CHECKLIST.md             # ✅ Implementation steps
├── 📄 README.md                          # Original README
│
├── 📄 docker-compose.yml                 # Local development environment
├── 📄 .env.example                       # Environment configuration template
├── 📄 .env                               # (your actual secrets - not in repo)
│
├── 📄 function_app.py                    # ⚠️ Original monolith (deprecated)
├── 📄 host.json                          # Azure Functions config
├── 📄 local.settings.json                # Local settings
├── 📄 requirements.txt                   # Original monolith dependencies
│
└── 📁 __pycache__/                       # (ignore)

```

## 📍 Key Locations

### Documentation
- **Start here**: `MICROSERVICES_README.md`
- **Migration details**: `deployment/MICROSERVICES_GUIDE.md`
- **Implementation steps**: `MIGRATION_CHECKLIST.md`
- **Summary**: `MIGRATION_SUMMARY.md`

### Services
- **Message Processing**: `services/message-service/`
- **Image Handling**: `services/image-service/`
- **Payment Processing**: `services/payment-service/`
- **Database Cleanup**: `services/maintenance-service/`

### Configuration
- **Docker compose**: `docker-compose.yml`
- **Environment template**: `.env.example`
- **Kubernetes manifests**: `deployment/kubernetes/`

### Shared Code
- **Event broker**: `shared/event_broker.py`
- **Common models**: `shared/models.py`

## 🔄 File Usage

### Reused from Original Monolith
```
app/message_processor.py          → Used by message-service
app/state_handlers.py             → Used by message-service
app/image_processors.py           → Used by image-service
app/astria_images_video_processors.py → Used by image-service
app/payment_processors.py         → Used by payment-service
db/db_maintenance.py              → Used by maintenance-service
Utils/                            → Shared by all services
db/dbConfig.py                    → Shared by all services
```

### Newly Created
```
services/*/function_app.py        → Service entry points
services/*/app/*_handler.py       → Service orchestrators
shared/event_broker.py            → Inter-service communication
shared/models.py                  → Shared data models
deployment/kubernetes/*.yaml      → K8s manifests
docker-compose.yml                → Local development
deployment/setup.sh / setup.bat   → Auto-setup scripts
```

## 📦 Service Dependencies

```
All Services:
├── shared/requirements.txt      (event broker, models)
├── Utils/                       (all shared utilities)
└── db/                          (database access)

Message Service:
├── app/message_processor.py
├── app/state_handlers.py
└── Utils/WhatsappWrapper.py

Image Service:
├── app/image_processors.py
├── app/astria_images_video_processors.py
└── Utils/constants.py

Payment Service:
├── app/payment_processors.py
└── Utils/ (various utilities)

Maintenance Service:
└── db/db_maintenance.py
```

## 🚀 Deployment Pipeline

```
Local Development
    ↓ (docker-compose up)
    ↓
Docker Images
    ↓ (docker build/push)
    ↓
Azure Container Registry
    ↓ (kubectl apply)
    ↓
Azure Kubernetes Service (AKS)
    ↓
Production Environment
```

## 📊 Scaling Map

```
Service              Instances (Local)    Instances (Production Min-Max)
─────────────────────────────────────────────────────────────────────
Message Service      1                    3-10 (HPA enabled)
Image Service        1                    2-5 (based on workload)
Payment Service      1                    2-3 (consistent traffic)
Maintenance Service  1                    1 (CronJob, single instance)
```

## 🔐 Security Notes

- **Secrets**: Store in `.env` (local) or Kubernetes Secrets (production)
- **Database**: Connection string in secrets only
- **API Keys**: Never commit to version control
- **Event Broker**: Use Service Bus with managed identities in production

---

**Structure is complete and ready for deployment!** 🎉
