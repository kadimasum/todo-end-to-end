#!/bin/bash

# Complete deployment script for TodoApp
# This script handles the entire deployment process from infrastructure to application

set -e

# Configuration
ENVIRONMENT=${1:-production}
REGION=${2:-us-west-2}
SKIP_INFRASTRUCTURE=${3:-false}

echo "🚀 Starting TodoApp deployment..."
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "Skip Infrastructure: $SKIP_INFRASTRUCTURE"

# Check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    # Check if required tools are installed
    command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform is required but not installed. Aborting." >&2; exit 1; }
    command -v ansible >/dev/null 2>&1 || { echo "❌ Ansible is required but not installed. Aborting." >&2; exit 1; }
    command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI is required but not installed. Aborting." >&2; exit 1; }
    command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
    
    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        echo "❌ AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Deploy infrastructure
deploy_infrastructure() {
    if [ "$SKIP_INFRASTRUCTURE" = "true" ]; then
        echo "⏭️  Skipping infrastructure deployment"
        return
    fi
    
    echo "🏗️  Deploying infrastructure with Terraform..."
    
    cd terraform
    
    # Initialize Terraform
    terraform init
    
    # Validate configuration
    terraform validate
    
    # Plan deployment
    terraform plan -out=tfplan
    
    # Apply configuration
    terraform apply -auto-approve tfplan
    
    # Get outputs
    ALB_DNS_NAME=$(terraform output -raw alb_dns_name)
    RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
    REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)
    STATIC_BUCKET_NAME=$(terraform output -raw static_bucket_name)
    
    echo "✅ Infrastructure deployed successfully"
    echo "ALB DNS: $ALB_DNS_NAME"
    echo "RDS Endpoint: $RDS_ENDPOINT"
    echo "Redis Endpoint: $REDIS_ENDPOINT"
    echo "Static Bucket: $STATIC_BUCKET_NAME"
    
    cd ..
}

# Build and push Docker image
build_and_push_image() {
    echo "🐳 Building and pushing Docker image..."
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_REGISTRY="$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
    IMAGE_TAG=$(git rev-parse --short HEAD)
    
    # Login to ECR
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
    
    # Create ECR repository if it doesn't exist
    aws ecr describe-repositories --repository-names todoapp --region $REGION >/dev/null 2>&1 || \
    aws ecr create-repository --repository-name todoapp --region $REGION
    
    # Build and tag image
    docker build -t todoapp:$IMAGE_TAG .
    docker tag todoapp:$IMAGE_TAG $ECR_REGISTRY/todoapp:$IMAGE_TAG
    docker tag todoapp:$IMAGE_TAG $ECR_REGISTRY/todoapp:latest
    
    # Push image
    docker push $ECR_REGISTRY/todoapp:$IMAGE_TAG
    docker push $ECR_REGISTRY/todoapp:latest
    
    echo "✅ Docker image built and pushed successfully"
    echo "Image: $ECR_REGISTRY/todoapp:$IMAGE_TAG"
}

# Deploy application
deploy_application() {
    echo "🚀 Deploying application with Ansible..."
    
    cd ansible
    
    # Update inventory with actual values
    if [ -n "$ALB_DNS_NAME" ]; then
        sed -i "s/\${ALB_DNS_NAME}/$ALB_DNS_NAME/g" inventory/hosts.yml
    fi
    
    # Create vault file if it doesn't exist
    if [ ! -f vault.yml ]; then
        echo "Creating vault file..."
        cat > vault.yml << EOF
vault_django_secret_key: "$(openssl rand -base64 32)"
vault_db_name: "todoapp"
vault_db_user: "todoapp"
vault_db_password: "$(openssl rand -base64 32)"
vault_email_user: "admin@example.com"
vault_email_password: "email-password"
EOF
        echo "⚠️  Please update vault.yml with your actual values and encrypt it:"
        echo "   ansible-vault encrypt vault.yml"
        echo "   ansible-vault edit vault.yml"
    fi
    
    # Run deployment
    ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml \
        --extra-vars "@vault.yml" \
        --extra-vars "alb_dns_name=$ALB_DNS_NAME" \
        --extra-vars "rds_endpoint=$RDS_ENDPOINT" \
        --extra-vars "redis_endpoint=$REDIS_ENDPOINT" \
        --extra-vars "static_bucket_name=$STATIC_BUCKET_NAME" \
        --extra-vars "git_commit_short=$IMAGE_TAG" \
        --ask-vault-pass
    
    echo "✅ Application deployed successfully"
    
    cd ..
}

# Run health checks
health_check() {
    echo "🏥 Running health checks..."
    
    cd ansible
    
    ansible-playbook -i inventory/hosts.yml playbooks/health-check.yml
    
    echo "✅ Health checks passed"
    
    cd ..
}

# Main deployment flow
main() {
    echo "🎯 Starting TodoApp deployment process..."
    
    check_prerequisites
    deploy_infrastructure
    build_and_push_image
    deploy_application
    health_check
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "📋 Deployment Summary:"
    echo "   Environment: $ENVIRONMENT"
    echo "   Region: $REGION"
    echo "   Application URL: http://$ALB_DNS_NAME"
    echo "   Health Check: http://$ALB_DNS_NAME/health/"
    echo ""
    echo "🔧 Useful commands:"
    echo "   Health check: cd ansible && ./health-check.sh"
    echo "   View logs: cd ansible && ansible all -i inventory/hosts.yml -m shell -a 'docker-compose -f /opt/todoapp/docker-compose.prod.yml logs'"
    echo "   Rollback: cd ansible && ansible-playbook -i inventory/hosts.yml playbooks/rollback.yml"
}

# Run main function
main "$@"
