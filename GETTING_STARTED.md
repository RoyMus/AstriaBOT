# 🚀 Getting Started with Microservices

Welcome! Your WhatsApp Astria Bot has been converted to microservices architecture. Here's how to get started.

## ⭐ READ THIS FIRST

Start with this 5-minute overview:

### What Changed?
Your monolithic Azure Function App is now split into 4 independent microservices:
- **Message Service** - WhatsApp webhook handler
- **Image Service** - Media processing
- **Payment Service** - Payment webhooks
- **Maintenance Service** - Database cleanup

### Why?
- ✅ Scale each service independently
- ✅ Isolate failures (one service down ≠ entire system down)
- ✅ Deploy faster (change one service, not everything)
- ✅ Better code organization
- ✅ Team scalability (multiple teams can own services)

## 🎯 Quick Start (5 minutes)

### Step 1: Setup Environment
```bash
# Copy template to actual config
cp .env.example .env

# Edit with your credentials
# (API keys, database URL, etc.)
```

### Step 2: Start All Services
```bash
# Option A: Using docker-compose
docker-compose up -d

# Option B: Using setup script
cd deployment
./setup.sh          # Linux/Mac
setup.bat          # Windows
```

### Step 3: Verify Services Are Running
```bash
# Check if all services are up
docker-compose ps

# Test each service
curl http://localhost:7071/health  # Message Service
curl http://localhost:7072/health  # Image Service
curl http://localhost:7073/health  # Payment Service
```

That's it! Your services are running locally. 🎉

## 📖 Documentation Guide

After getting started locally, read these in order:

1. **[MICROSERVICES_README.md](MICROSERVICES_README.md)** ← Main guide
   - Project structure
   - Service descriptions
   - Architecture overview
   - Testing instructions

2. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** ← File organization
   - What files were created
   - What was reused
   - Service dependencies

3. **[MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)** ← Overview
   - Before/after comparison
   - Benefits explained
   - Scaling examples

4. **[deployment/MICROSERVICES_GUIDE.md](deployment/MICROSERVICES_GUIDE.md)** ← Production deployment
   - Azure Container Registry setup
   - Kubernetes deployment
   - Monitoring configuration
   - Troubleshooting

5. **[MIGRATION_CHECKLIST.md](MIGRATION_CHECKLIST.md)** ← Implementation
   - Step-by-step checklist
   - Validation procedures
   - Rollout strategy

## 🔗 Update Your Webhooks

After local testing, update these endpoints to point to the new services:

| Provider | Old Endpoint | New Endpoint |
|----------|--------------|--------------|
| Meta/WhatsApp | Any Azure Function | `/message-service/SmsReceived` |
| Astria API | Any Azure Function | `/image-service/pack-tune-received` |
| Payment Provider | Any Azure Function | `/payment-service/payment-received` |

## 📚 Key Files

```
MICROSERVICES_README.md        ← Main documentation
MIGRATION_CHECKLIST.md         ← Implementation steps
PROJECT_STRUCTURE.md           ← File organization
MIGRATION_SUMMARY.md           ← Architecture overview
COMPLETION_SUMMARY.txt         ← What was created

docker-compose.yml             ← Local development
.env.example                   ← Configuration template
deployment/kubernetes/         ← Production deployment
services/                      ← Microservices
shared/                        ← Shared code
```

## ⚙️ Local Development

### Start Services
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f message-service
docker-compose logs -f image-service
docker-compose logs -f payment-service
```

### Stop Services
```bash
docker-compose down
```

### Rebuild Images
```bash
docker-compose build --no-cache
```

## 🚀 Production Deployment

### Quick Summary
1. Set up Azure Container Registry
2. Build and push Docker images
3. Create Kubernetes cluster (AKS)
4. Apply Kubernetes manifests
5. Configure monitoring

**See [deployment/MICROSERVICES_GUIDE.md](deployment/MICROSERVICES_GUIDE.md) for detailed steps.**

## 🆘 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs message-service

# Verify .env file
cat .env

# Check Docker is running
docker ps
```

### Can't connect to database
```bash
# Verify connection string in .env
# Test connection directly
psql $DATABASE_URL -c "SELECT 1"
```

### Services slow or crashing
```bash
# Check resource usage
docker stats

# Increase resource limits in docker-compose.yml
# Restart services
docker-compose restart
```

## 🎓 Learning Path

**Time Estimate: 1 hour to get started**

1. **Now (5 min)**: Read this file
2. **Local setup (5 min)**: `docker-compose up -d`
3. **Testing (10 min)**: Curl endpoints, check logs
4. **Read docs (20 min)**: MICROSERVICES_README.md
5. **Understand architecture (10 min)**: PROJECT_STRUCTURE.md
6. **Plan production (10 min)**: deployment/MICROSERVICES_GUIDE.md

## ✨ What's New

### Created
- 4 independent microservices
- Shared event broker for inter-service communication
- Docker setup for local development
- Kubernetes manifests for production
- Comprehensive documentation

### Reused (No Changes)
- `app/message_processor.py` - Message processing logic
- `app/state_handlers.py` - State machine
- `app/image_processors.py` - Image processing
- `app/payment_processors.py` - Payment logic
- `db/db_maintenance.py` - Database cleanup
- All utilities and database config

**No breaking changes to existing code!**

## 💡 Pro Tips

### Tip 1: Local Development with Multiple Services
Each service runs on a different port:
- Message: http://localhost:7071
- Image: http://localhost:7072
- Payment: http://localhost:7073

### Tip 2: Environment Variables
Keep `local.env` for local overrides, don't commit to git:
```bash
# Add to .gitignore if not there
echo "local.env" >> .gitignore
```

### Tip 3: Database Connection
Use the same PostgreSQL database for all services:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/astria_bot
```

### Tip 4: Event Broker
Local development uses in-memory broker (no setup needed).
Production uses Azure Service Bus (configure in secrets).

## 🎯 Your Next Steps

**This Week:**
- [ ] Read MICROSERVICES_README.md
- [ ] Run `docker-compose up -d`
- [ ] Test services locally
- [ ] Update webhook endpoints

**This Month:**
- [ ] Set up Azure Container Registry
- [ ] Deploy to Kubernetes
- [ ] Configure monitoring
- [ ] Gradual traffic migration

**Questions?** Check the detailed documentation:
- [MICROSERVICES_README.md](MICROSERVICES_README.md) - Complete guide
- [deployment/MICROSERVICES_GUIDE.md](deployment/MICROSERVICES_GUIDE.md) - Production setup
- [MIGRATION_CHECKLIST.md](MIGRATION_CHECKLIST.md) - Implementation steps

## 📞 Still Need Help?

1. Check `docker-compose logs` for error messages
2. Read [deployment/MICROSERVICES_GUIDE.md](deployment/MICROSERVICES_GUIDE.md) Troubleshooting section
3. Review [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for file locations
4. Check [MIGRATION_CHECKLIST.md](MIGRATION_CHECKLIST.md) validation procedures

---

**Ready to go?** Start with:
```bash
cp .env.example .env
docker-compose up -d
```

Then read [MICROSERVICES_README.md](MICROSERVICES_README.md) for the complete guide!

Happy coding! 🚀
