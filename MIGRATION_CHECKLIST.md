# Microservices Migration Checklist

## ✅ Completed Setup

- [x] **Shared Library Created**
  - `shared/event_broker.py` - Event-driven communication
  - `shared/models.py` - Common data models
  - `shared/requirements.txt` - Shared dependencies

- [x] **Message Service** (`services/message-service/`)
  - HTTP function for WhatsApp webhooks
  - State machine integration
  - Event publishing

- [x] **Image Service** (`services/image-service/`)
  - Astria webhook integration
  - Image processing pipeline
  - Pack image updates

- [x] **Payment Service** (`services/payment-service/`)
  - Payment webhook handling
  - Payment processing logic
  - Event publishing

- [x] **Maintenance Service** (`services/maintenance-service/`)
  - Scheduled database cleanup
  - CronJob configuration
  - Resource cleanup

- [x] **Docker Setup**
  - Dockerfiles for all services
  - docker-compose.yml for local development
  - Multi-stage builds for optimization

- [x] **Kubernetes Deployment**
  - Config and secrets management (01-config.yaml)
  - Message service with HPA (02-message-service.yaml)
  - Image service deployment (03-image-service.yaml)
  - Payment service deployment (04-payment-service.yaml)
  - Maintenance CronJob (05-maintenance-service.yaml)
  - Ingress configuration (06-ingress.yaml)

- [x] **Documentation**
  - MICROSERVICES_README.md - Overview and quick start
  - MICROSERVICES_GUIDE.md - Detailed deployment guide
  - This checklist

## 📋 Next Steps (Implementation)

### 1. Local Development Setup
- [ ] Copy `.env.example` to `.env`
- [ ] Update `.env` with your credentials:
  - `DATABASE_URL` - PostgreSQL connection
  - `ASTRIA_API_KEY` - Astria API key
  - `WHATSAPP_VERIFY_TOKEN` - Meta verify token
  - `SERVICEBUS_CONNECTION_STRING` - Azure Service Bus
- [ ] Run `docker-compose up -d`
- [ ] Test endpoints:
  - `curl http://localhost:7071/health`
  - `curl http://localhost:7072/health`
  - `curl http://localhost:7073/health`

### 2. Update Webhook Endpoints
- [ ] **Meta/WhatsApp Portal**
  - Change webhook to point to message-service
  - Verify token configuration
  
- [ ] **Astria API Webhooks**
  - Update image callback to image-service `/pack-tune-received`
  - Update pack images webhook to `/update-images`
  
- [ ] **Payment Provider**
  - Update payment webhook to payment-service `/payment-received`

### 3. Database Preparation
- [ ] Create new PostgreSQL database (if needed)
- [ ] Run existing migrations
- [ ] Backup current production data (if migrating)
- [ ] Test database connections from each service

### 4. Event Broker Configuration
- [ ] **For Development**: Uses local in-memory broker (no setup needed)
- [ ] **For Production**:
  - [ ] Create Azure Service Bus namespace
  - [ ] Create topics for each event type:
    - `events-user_message_received`
    - `events-image_processed`
    - `events-payment_received`
    - `events-tune_created`
    - `events-pack_images_updated`
  - [ ] Create subscriptions for services that listen
  - [ ] Update `SERVICEBUS_CONNECTION_STRING` in .env

### 5. Azure Container Registry Setup
- [ ] Create Azure Container Registry
- [ ] Build and push images:
  ```bash
  az acr build -r myregistry -t message-service:latest ./services/message-service
  az acr build -r myregistry -t image-service:latest ./services/image-service
  az acr build -r myregistry -t payment-service:latest ./services/payment-service
  az acr build -r myregistry -t maintenance-service:latest ./services/maintenance-service
  ```

### 6. Kubernetes Cluster Setup
- [ ] Create Azure Kubernetes Service (AKS) cluster
- [ ] Configure kubectl access:
  ```bash
  az aks get-credentials --resource-group mygroup --name myaksc
  ```
- [ ] Create namespace:
  ```bash
  kubectl create namespace astria-bot
  ```
- [ ] Apply configuration:
  ```bash
  kubectl apply -f deployment/kubernetes/01-config.yaml
  ```

### 7. Deploy to Kubernetes
- [ ] Update image registry URLs in YAML files
- [ ] Apply service deployments:
  ```bash
  kubectl apply -f deployment/kubernetes/02-message-service.yaml
  kubectl apply -f deployment/kubernetes/03-image-service.yaml
  kubectl apply -f deployment/kubernetes/04-payment-service.yaml
  kubectl apply -f deployment/kubernetes/05-maintenance-service.yaml
  ```
- [ ] Apply ingress:
  ```bash
  kubectl apply -f deployment/kubernetes/06-ingress.yaml
  ```
- [ ] Verify deployments:
  ```bash
  kubectl get pods -n astria-bot
  kubectl get svc -n astria-bot
  ```

### 8. Monitoring & Observability
- [ ] Set up Azure Application Insights
- [ ] Configure logging for each service
- [ ] Set up alerts for:
  - High error rates
  - Pod restarts
  - Resource limits exceeded
  - Event broker failures
- [ ] Create dashboards in Azure Monitor

### 9. CI/CD Pipeline
- [ ] Set up GitHub Actions or Azure DevOps
- [ ] Configure automatic image builds on push
- [ ] Set up automated Kubernetes deployments
- [ ] Configure rollback procedures

### 10. Testing & Validation
- [ ] Unit tests for each service
- [ ] Integration tests for event broker
- [ ] Load testing with production-like volume
- [ ] Chaos engineering (test fault scenarios)
- [ ] Blue-green deployment testing

### 11. Documentation Updates
- [ ] Update API documentation
- [ ] Document service dependencies
- [ ] Create runbooks for common operations
- [ ] Document scaling procedures

### 12. Rollout Strategy
- [ ] Week 1: Run in parallel with monolith (shadow mode)
- [ ] Week 2: Route 10% of traffic to microservices
- [ ] Week 3: Route 50% of traffic
- [ ] Week 4: Full migration to microservices
- [ ] Maintain fallback to monolith during this period

## 🔍 Validation Checklist

After each deployment stage:

- [ ] All services are healthy (running pods, ready status)
- [ ] Endpoints respond with correct status codes
- [ ] Database queries execute successfully
- [ ] Event broker is publishing/consuming messages
- [ ] Logs show no errors
- [ ] Performance metrics are within expected ranges
- [ ] Service-to-service communication works
- [ ] Webhooks from external services are received
- [ ] Database cleanup job runs on schedule

## 📊 Metrics to Monitor

- **Message Service**: 
  - Requests per second
  - Average response time
  - Error rate
  - Queue depth

- **Image Service**:
  - Image processing time
  - CPU/Memory usage
  - Failed images count

- **Payment Service**:
  - Webhook processing latency
  - Payment success rate
  - Transaction volume

- **All Services**:
  - Pod restart count
  - Memory usage
  - CPU usage
  - Network I/O
  - Event broker latency

## 🚨 Rollback Plan

If issues occur:

1. **Immediate**: Route traffic back to monolith
2. **Investigate**: Check service logs and metrics
3. **Fix**: Address issue in microservice
4. **Redeploy**: Re-push fixed image
5. **Validate**: Run full test suite
6. **Gradual Rollout**: Start with shadow traffic again

## 📞 Support Resources

- Check logs: `docker-compose logs -f [service-name]`
- Kubernetes logs: `kubectl logs -f deployment/[service] -n astria-bot`
- Event broker issues: Check Service Bus in Azure Portal
- Database issues: Verify connection string and PostgreSQL status

---

**Status**: ✅ All microservices created and documented. Ready for implementation!
