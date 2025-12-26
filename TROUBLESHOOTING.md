# Troubleshooting Guide - Production Issues

## Common Issues and Solutions

### 1. Cloud Run Service Not Responding

**Symptom**: 503 Service Unavailable or timeouts

**Check 1: Service Status**
```bash
gcloud run services describe marker-pdf-service \
  --platform=managed --region=us-central1
```
Look for `Ready: True` and `Status: Active`

**Check 2: View Recent Logs**
```bash
gcloud run services logs read marker-pdf-service \
  --limit=100 --format=json | jq '.message'
```

**Check 3: Verify Health Endpoint**
```bash
SERVICE_URL=$(gcloud run services describe marker-pdf-service \
  --platform=managed --region=us-central1 --format='value(status.url)')
curl -v "$SERVICE_URL/health"
```

**Solutions**:
- Increase memory: `--memory=4Gi` or higher
- Increase timeout: `--timeout=3600` for large files
- Check Cloud Run quota: `gcloud compute project-info describe --project=PROJECT_ID | grep -A5 quota`
- Review recent changes in deployment

---

### 2. GKE Pods Crashing

**Symptom**: Pods stuck in CrashLoopBackOff or Error state

**Check 1: Pod Status**
```bash
kubectl get pods -n default
kubectl describe pod POD_NAME -n default
```

**Check 2: Pod Logs**
```bash
kubectl logs POD_NAME -n default
kubectl logs POD_NAME -n default --previous  # For crashed pod
```

**Check 3: Resource Constraints**
```bash
kubectl describe nodes
kubectl top pods -n default
```

**Solutions**:
```bash
# Check available resources
kubectl describe nodes | grep -A 5 "Allocated resources"

# Increase resource limits
kubectl set resources deployment marker-pdf-service \
  --limits=memory=4Gi,cpu=2 \
  -n default

# Restart deployment
kubectl rollout restart deployment/marker-pdf-service -n default
```

---

### 3. Image Pull Errors

**Symptom**: `ImagePullBackOff` or `ErrImagePull` in pod status

**Check 1: Image Exists**
```bash
gcloud container images list --repository=gcr.io/$PROJECT_ID
gcloud container images describe gcr.io/$PROJECT_ID/marker-pdf-service:latest
```

**Check 2: Service Account Permissions**
```bash
# Verify service account can pull images
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:*"
```

**Solutions**:
```bash
# Push image to registry
docker build -t gcr.io/$PROJECT_ID/marker-pdf-service:latest .
docker push gcr.io/$PROJECT_ID/marker-pdf-service:latest

# Verify image is public or service account has access
gcloud container images add-iam-policy-binding \
  gcr.io/$PROJECT_ID/marker-pdf-service:latest \
  --member=serviceAccount:$SERVICE_ACCOUNT_EMAIL \
  --role=roles/storage.objectViewer
```

---

### 4. Database Connection Failures

**Symptom**: "Connection refused" or "Auth failed" errors in logs

**Check 1: Database Status**
```bash
gcloud sql instances describe marker-production-db
gcloud sql instances status-check marker-production-db
```

**Check 2: Connection Information**
```bash
# Get connection string
gcloud sql instances describe marker-production-db \
  --format='value(connectionName)'

# Verify from GKE cluster
kubectl run -it --image=postgres:15 psql -- \
  psql "postgresql://user@marker-prod-db/marker"
```

**Check 3: Network Configuration**
```bash
gcloud sql instances describe marker-production-db | grep -A 5 "ipAddresses"
```

**Solutions**:
```bash
# Authorize GKE cluster IP
CLUSTER_IP=$(gcloud container clusters describe marker-prod-cluster \
  --region=us-central1 --format='value(clusterIpv4Cidr)')

gcloud sql instances patch marker-production-db \
  --network=default

# Reset root password
gcloud sql users set-password root \
  --instance=marker-production-db \
  --password=NEWPASSWORD

# Test connection
gcloud sql connect marker-production-db --user=postgres
```

---

### 5. Storage Access Issues

**Symptom**: "Access Denied" or "Bucket not found" errors

**Check 1: Bucket Permissions**
```bash
gsutil ls gs://uploads-bucket
gsutil iam ch serviceAccount:$SERVICE_ACCOUNT:objectAdmin gs://uploads-bucket
```

**Check 2: Service Account Roles**
```bash
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT"
```

**Solutions**:
```bash
# Grant storage permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/storage.objectAdmin"

# Make bucket public (if needed)
gsutil iam ch allUsers:objectViewer gs://uploads-bucket

# Check bucket exists
gsutil ls
```

---

### 6. High Memory Usage

**Symptom**: OOMKilled errors or memory allocation failures

**Check 1: Memory Usage**
```bash
# Cloud Run
gcloud run services logs read marker-pdf-service \
  --filter='severity="ERROR"' | grep -i memory

# GKE
kubectl top pods -n default
kubectl describe pod POD_NAME | grep -A 5 "memory"
```

**Check 2: Memory Limits**
```bash
# Cloud Run - check allocation
gcloud run services describe marker-pdf-service \
  --format='value(spec.template.spec.containers[0].resources.limits.memory)'

# GKE - check pod limits
kubectl get pods -o json | jq '.items[].spec.containers[].resources'
```

**Solutions**:
```bash
# Cloud Run - increase memory
gcloud run services update marker-pdf-service \
  --memory=8Gi --concurrency=10

# GKE - increase resource limits
kubectl set resources deployment marker-pdf-service \
  --limits=memory=8Gi,cpu=4 \
  -n default

# Monitor memory intensive operations
# Reduce concurrent document processing
# Enable document streaming instead of loading whole file
```

---

### 7. Slow Document Processing

**Symptom**: Document conversion takes longer than expected

**Check 1: Performance Metrics**
```bash
# Check processing metrics
curl http://SERVICE_URL/metrics | grep -i duration

# View recent logs for timing
kubectl logs -n default deployment/marker-pdf-service | grep -i "processed\|duration"
```

**Check 2: Resource Availability**
```bash
# CPU usage
kubectl top pod POD_NAME -n default

# GPU availability (if using)
kubectl describe node | grep -A 5 "nvidia.com/gpu"
```

**Check 3: Input Factors**
- Document size (pages)
- Document complexity (images, tables, equations)
- Output format (markdown vs JSON)

**Solutions**:
```bash
# Enable GPU for faster processing (if available)
# Update deployment to use GPU nodes
kubectl patch deployment marker-pdf-service \
  -p '{"spec":{"template":{"spec":{"nodeSelector":{"cloud.google.com/gke-accelerator":"nvidia-tesla-t4"}}}}}'

# Scale up for parallel processing
kubectl scale deployment marker-pdf-service --replicas=5

# Enable caching for repeated documents
# Use batch processing for better throughput
```

---

### 8. Out of Quota Errors

**Symptom**: "Quota exceeded" errors in Cloud Build or deployment logs

**Check 1: Current Quotas**
```bash
gcloud compute project-info describe --project=$PROJECT_ID | grep -A 5 "QUOTA"
```

**Check 2: Usage**
```bash
gcloud compute instance-templates list
gcloud container clusters list
gcloud sql instances list
```

**Solutions**:
```bash
# Request quota increase
# 1. Go to Google Cloud Console
# 2. IAM & Admin > Quotas
# 3. Select the metric to increase
# 4. Click Edit Quotas

# Or via CLI
gcloud compute project-info describe --project=$PROJECT_ID

# Free up resources
gcloud container clusters delete CLUSTER_NAME
gcloud sql instances delete INSTANCE_NAME
gcloud storage buckets delete gs://old-bucket
```

---

### 9. Certificate/SSL Issues

**Symptom**: SSL certificate errors or HTTPS not working

**Check 1: Certificate Status**
```bash
# Cloud Run - managed certificate
gcloud run services describe marker-pdf-service \
  --format='value(spec.template.metadata.annotations."run.googleapis.com/ingress")'

# GKE - ingress certificate
kubectl describe ingress marker-pdf-ingress
kubectl get certificate -n default
```

**Solutions**:
```bash
# Cloud Run - enable HTTPS (default)
gcloud run services update marker-pdf-service \
  --ingress=all --allow-unauthenticated

# GKE - create certificate
kubectl apply -f - <<EOF
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: marker-cert
spec:
  domains:
    - marker.example.com
EOF
```

---

### 10. Deployment Not Progressing

**Symptom**: Deployment stuck in "progressing" state

**Check 1: Deployment Status**
```bash
kubectl rollout status deployment/marker-pdf-service -n default
kubectl get deployment marker-pdf-service -o yaml | grep -A 10 "status:"
```

**Check 2: Events**
```bash
kubectl describe deployment marker-pdf-service -n default
kubectl get events -n default --sort-by='.lastTimestamp'
```

**Solutions**:
```bash
# Increase timeout
kubectl rollout status deployment/marker-pdf-service --timeout=10m

# Check resource availability
kubectl describe nodes

# Increase replica count if stuck
kubectl scale deployment marker-pdf-service --replicas=1

# Force rollback to previous version
kubectl rollout undo deployment/marker-pdf-service

# Delete and recreate
kubectl delete deployment marker-pdf-service
kubectl apply -f deployment.yaml
```

---

## Getting Help

### Collect Diagnostic Information

```bash
#!/bin/bash
# diagnostic-report.sh

PROJECT_ID=$1
SERVICE_NAME="marker-pdf-service"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT="diagnostic-report_${TIMESTAMP}.txt"

{
  echo "=== Diagnostic Report ==="
  echo "Timestamp: $(date)"
  echo "Project: $PROJECT_ID"
  echo ""
  
  echo "=== Cloud Run Status ==="
  gcloud run services describe $SERVICE_NAME 2>/dev/null || echo "Service not found"
  
  echo ""
  echo "=== Recent Logs (last 50 lines) ==="
  gcloud run services logs read $SERVICE_NAME --limit=50 2>/dev/null || echo "No logs"
  
  echo ""
  echo "=== GKE Cluster Status ==="
  gcloud container clusters list --project=$PROJECT_ID
  
  echo ""
  echo "=== Pod Status ==="
  kubectl get pods -A 2>/dev/null || echo "kubectl not configured"
  
  echo ""
  echo "=== Resource Usage ==="
  kubectl top pods -A 2>/dev/null || echo "Metrics not available"
  
  echo ""
  echo "=== Storage Buckets ==="
  gsutil ls 2>/dev/null || echo "No buckets found"
  
} | tee "$REPORT"

echo "Report saved to: $REPORT"
```

### Contact Support

- **Documentation**: [.gcp/GCP_SETUP_GUIDE.md]
- **GitHub Issues**: https://github.com/VikParuchuri/marker/issues
- **Discord Community**: https://discord.gg/KuZwXNGnfH
- **Commercial Support**: contact@datalab.to

---

**Last Updated**: January 2025
