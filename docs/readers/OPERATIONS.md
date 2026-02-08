# NomadAI - Operations Guide

> Deployment, monitoring, and maintenance for DevOps/SRE teams

---

## Deployment Options

### Option 1: Vercel (Recommended for MVP)

**Pros:** Zero-ops, auto-scaling, global CDN
**Cons:** Cold starts, 10s function timeout

```bash
# Install CLI
npm i -g vercel

# Login
vercel login

# Deploy to production
vercel --prod

# Set secrets
vercel env add ZHIPUAI_API_KEY production
```

**Vercel Configuration (`vercel.json`):**
```json
{
  "version": 2,
  "builds": [
    { "src": "api/index.py", "use": "@vercel/python" },
    { "src": "public/**", "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "api/index.py" },
    { "src": "/(.*)", "dest": "public/$1" }
  ]
}
```

### Option 2: Docker + Cloud Run

**Pros:** More control, longer timeouts, persistent connections
**Cons:** More setup, cost at scale

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "api.index:app"]
```

```bash
# Build
docker build -t nomadai:latest .

# Run locally
docker run -p 8080:8080 \
  -e ZHIPUAI_API_KEY=$ZHIPUAI_API_KEY \
  nomadai:latest

# Deploy to Cloud Run
gcloud run deploy nomadai \
  --image gcr.io/PROJECT/nomadai \
  --set-env-vars ZHIPUAI_API_KEY=$ZHIPUAI_API_KEY
```

### Option 3: Kubernetes

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nomadai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nomadai
  template:
    metadata:
      labels:
        app: nomadai
    spec:
      containers:
      - name: nomadai
        image: nomadai:latest
        ports:
        - containerPort: 8080
        env:
        - name: ZHIPUAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: nomadai-secrets
              key: zhipuai-api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: nomadai
spec:
  selector:
    app: nomadai
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

---

## Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ZHIPUAI_API_KEY` | Z.AI API authentication | `507b2d0b...` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Environment mode |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `SESSION_TTL` | `3600` | Session timeout (seconds) |
| `MAX_AUDIO_SIZE` | `10485760` | Max audio upload (10MB) |
| `RATE_LIMIT` | `100` | Requests per minute per IP |

### Secrets Management

**Vercel:**
```bash
vercel env add ZHIPUAI_API_KEY production
```

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name nomadai/production \
  --secret-string '{"ZHIPUAI_API_KEY":"xxx"}'
```

**Kubernetes:**
```bash
kubectl create secret generic nomadai-secrets \
  --from-literal=zhipuai-api-key=$ZHIPUAI_API_KEY
```

---

## Monitoring

### Health Checks

| Endpoint | Expected Response | Purpose |
|----------|-------------------|---------|
| `GET /` | `{"status": "ok"}` | Liveness probe |
| `GET /api/health` | `{"status": "healthy"}` | Readiness probe |

**Kubernetes Probes:**
```yaml
livenessProbe:
  httpGet:
    path: /
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /api/health
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Metrics to Track

| Metric | Alert Threshold | Description |
|--------|-----------------|-------------|
| `response_time_p99` | > 3s | 99th percentile latency |
| `error_rate` | > 5% | HTTP 5xx rate |
| `asr_accuracy` | < 90% | Transcription quality |
| `api_quota_remaining` | < 10% | Z.AI API quota |
| `active_sessions` | > 1000 | Concurrent users |

### Logging

**Structured Logging Format:**
```json
{
  "timestamp": "2026-02-08T12:00:00Z",
  "level": "INFO",
  "service": "nomadai",
  "trace_id": "abc123",
  "message": "Voice chat completed",
  "duration_ms": 1250,
  "skill": "room_service",
  "language": "en"
}
```

**Log Aggregation:**
```bash
# Vercel logs
vercel logs --follow

# Docker logs
docker logs -f nomadai

# Kubernetes logs
kubectl logs -f deployment/nomadai
```

---

## Scaling

### Horizontal Scaling

| Load | Instances | Notes |
|------|-----------|-------|
| < 100 req/min | 1-2 | MVP phase |
| 100-1000 req/min | 3-5 | Standard |
| 1000+ req/min | 5-10+ | High traffic |

### Vertical Scaling

| Component | Min | Recommended | Notes |
|-----------|-----|-------------|-------|
| CPU | 0.25 vCPU | 0.5 vCPU | Per instance |
| Memory | 256 MB | 512 MB | Per instance |
| Disk | N/A | N/A | Stateless |

### Auto-scaling Rules

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nomadai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nomadai
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Disaster Recovery

### Backup Strategy

| Data | Backup Frequency | Retention |
|------|------------------|-----------|
| Session data | N/A (ephemeral) | - |
| Knowledge base | Daily | 30 days |
| Configuration | On change | Versioned |

### Recovery Procedures

**Service Degradation:**
1. Check Z.AI API status: https://status.z.ai
2. Enable fallback responses
3. Notify affected users

**Full Outage:**
1. Failover to backup region
2. Verify health checks
3. Update DNS if needed

### RTO/RPO

| Metric | Target |
|--------|--------|
| RTO (Recovery Time) | < 5 minutes |
| RPO (Data Loss) | 0 (stateless) |

---

## Security

### API Security

| Control | Implementation |
|---------|----------------|
| Authentication | API key in header |
| Rate limiting | 100 req/min per IP |
| Input validation | Schema validation |
| CORS | Allowed origins list |

### Data Security

| Control | Implementation |
|---------|----------------|
| Encryption at rest | AES-256 |
| Encryption in transit | TLS 1.3 |
| Audio retention | 24 hours max |
| PII handling | Anonymize in logs |

### Compliance

| Standard | Status |
|----------|--------|
| GDPR | Compliant |
| CCPA | Compliant |
| SOC 2 | In progress |

---

## Runbooks

### High Error Rate

```
1. Check /api/health endpoint
2. Review error logs: vercel logs --level error
3. Check Z.AI API status
4. If Z.AI down: enable fallback mode
5. If app issue: rollback to previous deployment
```

### Slow Response Times

```
1. Check response_time_p99 metric
2. Identify slow endpoint from logs
3. Check Z.AI API latency
4. Scale up if CPU > 70%
5. Enable response caching if applicable
```

### API Quota Exceeded

```
1. Check api_quota_remaining metric
2. Contact Z.AI for quota increase
3. Enable request queueing
4. Prioritize critical requests
```

---

## Contacts

| Role | Contact |
|------|---------|
| On-call | oncall@nomadai.com |
| Engineering Lead | eng@nomadai.com |
| Z.AI Support | support@z.ai |
