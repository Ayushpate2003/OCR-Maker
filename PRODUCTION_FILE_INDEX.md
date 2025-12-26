# Production Deployment - File Index

This document provides a complete index of all production-ready files and their purposes.

## 📋 Quick Navigation

- **[New Production README](README_PRODUCTION.md)** - Start here! Complete guide for all users
- **[GCP Setup Guide](.gcp/GCP_SETUP_GUIDE.md)** - Detailed GCP deployment instructions
- **[Production Checklist](PRODUCTION_CHECKLIST.md)** - Pre-deployment verification
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Solutions for common issues

## 🗂️ File Structure

```
marker/
├── README_PRODUCTION.md              ← NEW: Production guide (read first!)
├── PRODUCTION_CHECKLIST.md           ← NEW: Pre-deployment checklist
├── TROUBLESHOOTING.md                ← NEW: Troubleshooting guide
├── requirements-gcp-production.txt   ← NEW: GCP production dependencies
│
├── Dockerfile                        ← NEW: Multi-stage production Dockerfile
├── .dockerignore                     ← NEW: Docker build exclusions
│
├── .gcp/                             ← NEW: GCP-specific configurations
│   ├── README.md                     ← Setup overview
│   ├── GCP_SETUP_GUIDE.md           ← Complete setup guide (comprehensive!)
│   ├── deploy.sh                     ← Automated deployment script
│   ├── setup-project.sh              ← GCP project initialization
│   ├── health-check.sh               ← NEW: Health verification script
│   ├── app.yaml                      ← App Engine configuration
│   ├── cloud-build.yaml              ← Cloud Build pipeline
│   │
│   ├── terraform/
│   │   ├── main.tf                   ← Infrastructure as Code (IaC)
│   │   └── terraform.tfvars.example  ← Terraform variables template
│   │
│   └── kustomization/
│       ├── kustomization.yaml        ← Kustomize base configuration
│       ├── deployment.yaml           ← Kubernetes deployment manifest
│       ├── config.yaml               ← Application configuration
│       └── secrets-example.yaml      ← Secrets and RBAC configuration
│
├── .github/
│   └── workflows/
│       └── deploy.yml                ← GitHub Actions CI/CD pipeline
│
└── [existing files remain unchanged]
```

## 📄 File Descriptions

### Documentation Files

| File | Purpose | For Whom |
|------|---------|----------|
| [README_PRODUCTION.md](README_PRODUCTION.md) | Complete production guide with quick start | Everyone |
| [GCP_SETUP_GUIDE.md](.gcp/GCP_SETUP_GUIDE.md) | Detailed GCP deployment walkthrough | DevOps/Cloud Engineers |
| [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) | Pre-deployment verification checklist | Release Managers |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions | On-Call Support |
| [.gcp/README.md](.gcp/README.md) | Quick start for GCP setup | DevOps Engineers |

### Container Files

| File | Purpose |
|------|---------|
| [Dockerfile](Dockerfile) | Multi-stage Docker build for production |
| [.dockerignore](.dockerignore) | Exclude files from Docker context |

### Deployment Configuration

| File | Purpose | Platform |
|------|---------|----------|
| [cloud-build.yaml](.gcp/cloud-build.yaml) | Automated build and deploy pipeline | Google Cloud Build |
| [app.yaml](.gcp/app.yaml) | Cloud Run/App Engine config | Cloud Run/App Engine |
| [deployment.yaml](.gcp/kustomization/deployment.yaml) | Kubernetes pod spec | GKE |
| [kustomization.yaml](.gcp/kustomization/kustomization.yaml) | Kubernetes configuration overlay | GKE |
| [config.yaml](.gcp/kustomization/config.yaml) | Application configuration | GKE |
| [secrets-example.yaml](.gcp/kustomization/secrets-example.yaml) | RBAC and secrets templates | GKE |

### Infrastructure as Code

| File | Purpose |
|------|---------|
| [terraform/main.tf](.gcp/terraform/main.tf) | Complete GCP infrastructure definition |
| [terraform/terraform.tfvars.example](.gcp/terraform/terraform.tfvars.example) | Terraform variables template |

### CI/CD Pipeline

| File | Purpose |
|------|---------|
| [.github/workflows/deploy.yml](.github/workflows/deploy.yml) | Automated testing and deployment |

### Scripts

| File | Purpose | Usage |
|------|---------|-------|
| [deploy.sh](.gcp/deploy.sh) | Main deployment orchestrator | `bash deploy.sh [env] [region] [action]` |
| [setup-project.sh](.gcp/setup-project.sh) | GCP project initialization | `bash setup-project.sh [project-id]` |
| [health-check.sh](.gcp/health-check.sh) | Health verification | `bash health-check.sh [project-id]` |

### Dependencies

| File | Purpose |
|------|---------|
| [requirements-gcp-production.txt](requirements-gcp-production.txt) | Production Python dependencies |

## 🚀 Getting Started

### 1. First Time Setup (5 minutes)

```bash
# Read the production guide
cat README_PRODUCTION.md

# Initialize GCP project
export GCP_PROJECT_ID="your-project-id"
bash .gcp/setup-project.sh $GCP_PROJECT_ID us-central1 production

# Deploy service
bash .gcp/deploy.sh production us-central1 deploy
```

### 2. Verify Deployment (1 minute)

```bash
# Run health checks
bash .gcp/health-check.sh $GCP_PROJECT_ID us-central1

# View logs
bash .gcp/deploy.sh production us-central1 logs
```

### 3. Troubleshoot Issues

```bash
# Consult troubleshooting guide
cat TROUBLESHOOTING.md

# Check specific error in guide
# Follow recommended solutions
```

## 📊 Deployment Options

Choose your deployment method based on your needs:

### Option 1: Cloud Run (Recommended for most)
- **Best for**: Variable workloads, rapid deployment
- **Setup time**: 5 minutes
- **Cost**: Pay-per-use, scale 0-100 instances
- **Files used**: `cloud-build.yaml`, `Dockerfile`, `app.yaml`
- **Steps**: Read [GCP_SETUP_GUIDE.md](.gcp/GCP_SETUP_GUIDE.md#option-a-cloud-run-recommended-for-startups)

### Option 2: GKE (Recommended for scale)
- **Best for**: High volume, complex requirements
- **Setup time**: 10-15 minutes
- **Cost**: Managed Kubernetes, reserved capacity available
- **Files used**: `deployment.yaml`, `kustomization.yaml`, all configs
- **Steps**: Read [GCP_SETUP_GUIDE.md](.gcp/GCP_SETUP_GUIDE.md#option-b-google-kubernetes-engine-gke-recommended-for-scale)

### Option 3: Terraform (Infrastructure as Code)
- **Best for**: Enterprise, IaC-first approach
- **Setup time**: 10 minutes
- **Cost**: Declarative, version-controlled
- **Files used**: `terraform/main.tf`, `terraform/terraform.tfvars.example`
- **Steps**: Read [GCP_SETUP_GUIDE.md](.gcp/GCP_SETUP_GUIDE.md#3-infrastructure-setup-terraform)

### Option 4: GitHub Actions (Automated)
- **Best for**: Continuous deployment pipeline
- **Setup time**: Configure secrets, then automatic on push
- **Cost**: Integrated with your deployment option
- **Files used**: `.github/workflows/deploy.yml`
- **Steps**: Configure GitHub Secrets, push to branch

## 🔐 Security Features

All production files include:

✅ **Non-root execution** - Container runs as unprivileged user  
✅ **Secret management** - Google Secret Manager integration  
✅ **RBAC** - Role-based access control in Kubernetes  
✅ **Network security** - Service isolation and firewall rules  
✅ **TLS/SSL** - Automatic certificate management  
✅ **Audit logging** - Cloud Audit Logs enabled  
✅ **Input validation** - Request/response validation  
✅ **Rate limiting** - Built-in protection  

See [GCP_SETUP_GUIDE.md](.gcp/GCP_SETUP_GUIDE.md#security-best-practices) for details.

## 📈 Scaling Configuration

### Cloud Run Auto-scaling
- Min instances: 2
- Max instances: 100
- Concurrency: 100 req/instance
- Adjust: See `cloud-build.yaml`

### GKE Auto-scaling (HPA)
- Min replicas: 3
- Max replicas: 10
- CPU target: 70%
- Memory target: 80%
- Adjust: See `deployment.yaml`

## 🔍 Monitoring

### Logs
- Cloud Run: `gcloud run services logs read`
- GKE: `kubectl logs deployment/marker-pdf-service`
- Centralized: Cloud Logging dashboard

### Metrics
- CPU, memory, request rate
- Custom application metrics at `/metrics`
- Dashboards in Cloud Monitoring

### Alerts
Configured for:
- High error rate (>1%)
- High latency (>5s)
- High CPU/memory usage
- Service unavailability

## 💰 Cost Estimation

| Workload | Cloud Run | GKE |
|----------|-----------|-----|
| 1,000 docs/month | ~$5 | ~$50 |
| 100,000 docs/month | ~$400 | ~$150 |
| 1M+ docs/month | ~$3,000 | ~$200 |

See [GCP_SETUP_GUIDE.md](.gcp/GCP_SETUP_GUIDE.md#cost-optimization) for optimization tips.

## 📞 Support Resources

- **Documentation**: This guide and linked documents
- **API Reference**: [API_REFERENCE.md](API_REFERENCE.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Community**: [Discord](https://discord.gg/KuZwXNGnfH)
- **Issues**: [GitHub Issues](https://github.com/VikParuchuri/marker/issues)
- **Enterprise**: contact@datalab.to

## ✅ Pre-Deployment Checklist

Before deploying to production, ensure:

- [ ] Read [README_PRODUCTION.md](README_PRODUCTION.md)
- [ ] Reviewed [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
- [ ] GCP project with billing enabled
- [ ] Required CLI tools installed
- [ ] Security requirements understood
- [ ] Monitoring/alerting configured
- [ ] Team trained on runbooks
- [ ] Backup procedures documented

## 📝 Version Information

- **Created**: January 2025
- **Status**: Production-Ready ✅
- **Last Updated**: January 2025
- **Docker**: Multi-stage, optimized for production
- **Kubernetes**: 1.24+
- **Python**: 3.10+
- **GCP APIs**: All required APIs enabled by setup scripts

## 🔄 Next Steps

1. **Read** → Start with [README_PRODUCTION.md](README_PRODUCTION.md)
2. **Setup** → Run [setup-project.sh](.gcp/setup-project.sh)
3. **Deploy** → Use [deploy.sh](.gcp/deploy.sh)
4. **Verify** → Run [health-check.sh](.gcp/health-check.sh)
5. **Monitor** → Check Cloud Console dashboards
6. **Maintain** → Follow [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)

---

**Questions?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or visit our [Discord community](https://discord.gg/KuZwXNGnfH)!
