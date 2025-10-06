# TodoApp Deployment Guide

This guide covers the complete deployment process for the TodoApp Django application using Docker, Terraform, Ansible, and GitHub Actions.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub        │    │   AWS           │    │   Application   │
│   Actions       │───▶│   Infrastructure│───▶│   Deployment    │
│   CI/CD         │    │   (Terraform)   │    │   (Ansible)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Code Quality  │    │   VPC, RDS,     │    │   Docker        │
│   Testing       │    │   ElastiCache   │    │   Containers    │
│   Security      │    │   ALB, ASG      │    │   Nginx         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

### Local Development
- Python 3.8+
- Docker & Docker Compose
- Git
- AWS CLI configured
- Terraform 1.0+
- Ansible 2.9+

### AWS Resources
- AWS Account with appropriate permissions
- S3 bucket for Terraform state
- Route 53 hosted zone (optional, for custom domain)

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd django-server-devops
```

### 2. Configure Environment
```bash
# Copy example environment file
cp terraform/terraform.tfvars.example terraform/terraform.tfvars

# Edit with your values
vim terraform/terraform.tfvars
```

### 3. Deploy Everything
```bash
# Make scripts executable
chmod +x scripts/deploy.sh

# Deploy (this will create infrastructure and deploy app)
./scripts/deploy.sh production us-west-2
```

## 🔧 Manual Deployment Steps

### Step 1: Infrastructure Deployment (Terraform)

```bash
cd terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file="terraform.tfvars"

# Deploy infrastructure
terraform apply -var-file="terraform.tfvars"

# Get outputs
terraform output
```

### Step 2: Application Deployment (Ansible)

```bash
cd ansible

# Setup Ansible environment
./scripts/setup.sh

# Create and encrypt vault file
ansible-vault create vault.yml

# Update inventory with actual server details
vim inventory/hosts.yml

# Deploy application
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --ask-vault-pass
```

### Step 3: Health Check

```bash
cd ansible
ansible-playbook -i inventory/hosts.yml playbooks/health-check.yml
```

## 🐳 Docker Deployment

### Local Development
```bash
# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production
```bash
# Build production image
docker build -t todoapp:latest .

# Run with production settings
docker run -d \
  -p 8000:8000 \
  -e DEBUG=False \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  todoapp:latest
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The CI/CD pipeline includes:

1. **Code Quality Checks**
   - Linting (flake8, black, isort)
   - Security scanning (Trivy, Bandit)
   - Test coverage reporting

2. **Testing**
   - Unit tests with pytest
   - Integration tests
   - Database and Redis testing

3. **Build & Deploy**
   - Docker image building
   - ECR push
   - Infrastructure deployment
   - Application deployment

4. **Health Checks**
   - Application health verification
   - Performance monitoring

### Required GitHub Secrets

```yaml
AWS_ACCESS_KEY_ID: your-aws-access-key
AWS_SECRET_ACCESS_KEY: your-aws-secret-key
DB_PASSWORD: your-database-password
SECRET_KEY: your-django-secret-key
SSH_PRIVATE_KEY: your-ec2-private-key
S3_BUCKET: your-s3-bucket-name
DB_NAME: todoapp
DB_USER: todoapp
EMAIL_USER: your-email@example.com
EMAIL_PASSWORD: your-email-password
```

## 📊 Monitoring and Logging

### Application Logs
```bash
# View application logs
docker-compose logs -f web

# View nginx logs
docker-compose logs -f nginx

# View all logs
docker-compose logs -f
```

### System Monitoring
```bash
# Check system resources
htop

# Check disk usage
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep todoapp
```

### Health Endpoints
- Application Health: `http://your-domain/health/`
- Load Balancer Health: Check AWS ALB target group health

## 🔒 Security Considerations

### Infrastructure Security
- VPC with private subnets for application servers
- Security groups with minimal required access
- RDS in private subnets
- ElastiCache in private subnets

### Application Security
- HTTPS enforcement (configure SSL certificates)
- Security headers via Nginx
- Rate limiting for API endpoints
- CSRF protection
- SQL injection prevention

### Secrets Management
- Use Ansible Vault for sensitive data
- Store secrets in GitHub Secrets
- Rotate secrets regularly
- Use AWS Secrets Manager for production

## 🚨 Troubleshooting

### Common Issues

#### 1. Terraform State Lock
```bash
# If state is locked
terraform force-unlock <lock-id>
```

#### 2. Ansible Connection Issues
```bash
# Test connection
ansible all -i inventory/hosts.yml -m ping

# Check SSH key
ssh -i ~/.ssh/id_rsa ec2-user@your-server-ip
```

#### 3. Docker Build Failures
```bash
# Check Docker daemon
sudo systemctl status docker

# Clean up Docker
docker system prune -a
```

#### 4. Application Not Starting
```bash
# Check container logs
docker logs <container-id>

# Check systemd service
sudo systemctl status todoapp

# Check application logs
tail -f /var/log/todoapp/django.log
```

### Debug Commands

```bash
# Check Ansible inventory
ansible-inventory -i inventory/hosts.yml --list

# Test Ansible playbook
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --check

# Check Terraform plan
terraform plan -detailed-exitcode

# Check AWS resources
aws ec2 describe-instances --filters "Name=tag:Project,Values=todoapp"
```

## 📈 Scaling

### Horizontal Scaling
- Auto Scaling Group automatically scales based on CPU/memory
- Load Balancer distributes traffic across instances
- Database read replicas for read-heavy workloads

### Vertical Scaling
- Increase instance types in Terraform variables
- Scale RDS instance class
- Increase ElastiCache node type

### Database Scaling
```bash
# Create read replica
aws rds create-db-instance-read-replica \
  --db-instance-identifier todoapp-read-replica \
  --source-db-instance-identifier todoapp-db
```

## 🔄 Backup and Recovery

### Database Backups
- Automated daily backups via RDS
- Point-in-time recovery available
- Cross-region backup replication

### Application Backups
```bash
# Manual backup
ansible-playbook -i inventory/hosts.yml playbooks/backup.yml

# Restore from backup
ansible-playbook -i inventory/hosts.yml playbooks/restore.yml --extra-vars "backup_id=backup-123"
```

### Disaster Recovery
1. Infrastructure: Recreate with Terraform
2. Database: Restore from RDS snapshots
3. Application: Redeploy with Ansible
4. Data: Restore from S3 backups

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review application logs
3. Check GitHub Issues
4. Contact the development team

---

**Happy Deploying! 🚀**
