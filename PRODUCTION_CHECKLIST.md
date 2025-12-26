# Production Deployment Checklist

Use this checklist to ensure your Marker deployment is production-ready.

## Pre-Deployment

### Infrastructure Setup
- [ ] GCP project created with billing enabled
- [ ] Required APIs enabled (Cloud Run, GKE, Cloud Storage, etc.)
- [ ] Service accounts created with appropriate IAM roles
- [ ] Storage buckets created (uploads, outputs, backups)
- [ ] Databases configured (Cloud SQL, Firestore, Redis)

### Security
- [ ] Service account has minimal required permissions
- [ ] Secrets stored in Secret Manager (not in code/config)
- [ ] SSL/TLS certificates configured
- [ ] VPC Service Controls configured (if applicable)
- [ ] Network policies restrict traffic appropriately
- [ ] CORS configuration reviewed and restricted
- [ ] Rate limiting configured
- [ ] Input validation enabled

### Configuration
- [ ] Environment variables reviewed and set
- [ ] Logging level set to INFO (not DEBUG)
- [ ] Performance tuning applied (caching, auto-scaling)
- [ ] Backup and recovery procedures documented
- [ ] Disaster recovery plan created

### Testing
- [ ] Unit tests passing (pytest)
- [ ] Integration tests passing
- [ ] Load tests completed
- [ ] Security scanning passed
- [ ] Docker image builds successfully
- [ ] Container registry accessible

## Deployment

### Cloud Run Deployment
- [ ] Docker image built and pushed
- [ ] Service deployed with correct memory/CPU
- [ ] Health checks configured
- [ ] Auto-scaling thresholds set
- [ ] Environment variables verified
- [ ] Service accessible and responding to requests

### GKE Deployment
- [ ] Kubernetes cluster created
- [ ] Node pool configured for workload
- [ ] Persistent volumes configured (if needed)
- [ ] Ingress controller installed
- [ ] Kustomization manifests applied
- [ ] Pod replicas running and healthy
- [ ] HPA (Horizontal Pod Autoscaler) verified

### Monitoring & Logging
- [ ] Cloud Logging enabled and working
- [ ] Cloud Monitoring dashboards created
- [ ] Alert policies configured for:
  - [ ] High error rate (>1%)
  - [ ] High latency (>5s)
  - [ ] High CPU/memory usage
  - [ ] Service unavailability
- [ ] Log aggregation verified
- [ ] Metrics collection verified

## Post-Deployment

### Verification
- [ ] Service health check passing
- [ ] Load test successful
- [ ] Smoke tests passing
- [ ] End-to-end workflow working
- [ ] Document conversion working for all formats
- [ ] RAG indexing and search working
- [ ] API response times within SLA

### Documentation
- [ ] Deployment procedure documented
- [ ] Runbook created for on-call team
- [ ] Troubleshooting guide updated
- [ ] Architecture diagram created/updated
- [ ] Configuration documented

### Backups
- [ ] Database backups configured and tested
- [ ] Cloud Storage backup tested
- [ ] Backup retention policies set
- [ ] Restore procedure tested

### Team Readiness
- [ ] Team trained on deployment
- [ ] On-call schedule established
- [ ] Incident response procedures reviewed
- [ ] Rollback procedure tested

## Ongoing Operations

### Daily
- [ ] Monitor service health dashboard
- [ ] Check error rates and logs
- [ ] Verify no anomalous scaling events

### Weekly
- [ ] Review performance metrics
- [ ] Check backup status
- [ ] Review security logs
- [ ] Analyze cost trends

### Monthly
- [ ] Performance optimization review
- [ ] Security audit
- [ ] Disaster recovery drill
- [ ] Update dependencies and patches

### Quarterly
- [ ] Load testing
- [ ] Capacity planning
- [ ] Architecture review
- [ ] Compliance audit

## Troubleshooting

### If deployment fails:
1. Check Cloud Build logs
2. Verify service account permissions
3. Check image pushing to registry
4. Verify resource limits not exceeded
5. Check network connectivity

### If service is down:
1. Check pod/instance status
2. Check logs for errors
3. Verify health check endpoint
4. Check resource constraints
5. Verify external dependencies (database, storage)

### If performance degrades:
1. Check CPU/memory usage
2. Review database performance
3. Check for traffic spikes
4. Verify auto-scaling is working
5. Check for slow queries/operations

### If security incident occurs:
1. Isolate affected resources
2. Review logs for unauthorized access
3. Rotate compromised credentials
4. Apply patches/fixes
5. Review security group rules
6. Document incident

## Quick Command Reference

```bash
# GCP Project Setup
export GCP_PROJECT_ID="your-project-id"
bash .gcp/setup-project.sh $GCP_PROJECT_ID us-central1 production

# Build and Deploy
bash .gcp/deploy.sh production us-central1 deploy

# View Logs
bash .gcp/deploy.sh production us-central1 logs

# Rollback
kubectl rollout undo deployment/marker-pdf-service

# Health Check
curl https://marker-service-url/health

# View Metrics
gcloud monitoring timeseries list --filter='metric.type="run.googleapis.com/*"'

# Destroy Infrastructure
bash .gcp/deploy.sh production us-central1 destroy
```

## Emergency Procedures

### Immediate Shutdown
```bash
# Cloud Run
gcloud run services delete marker-pdf-service --quiet

# GKE
kubectl delete deployment marker-pdf-service
```

### Data Protection
```bash
# Backup database
gcloud sql backups create emergency-backup \
  --instance=marker-production-db

# Backup Cloud Storage
gsutil -m cp -r gs://uploads-bucket gs://emergency-backup/
```

### Service Restoration
```bash
# Restore from backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=marker-production-db

# Revert deployment
kubectl rollout undo deployment/marker-pdf-service
```

---

**Last Updated**: January 2025  
**Status**: Production-Ready ✅
