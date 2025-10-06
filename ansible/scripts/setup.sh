#!/bin/bash

# Ansible setup script for TodoApp deployment

set -e

echo "Setting up Ansible environment for TodoApp deployment..."

# Check if Ansible is installed
if ! command -v ansible &> /dev/null; then
    echo "Installing Ansible..."
    pip install ansible
fi

# Install Ansible collections and roles
echo "Installing Ansible collections and roles..."
ansible-galaxy install -r requirements.yml

# Create necessary directories
mkdir -p inventory/group_vars
mkdir -p inventory/host_vars
mkdir -p logs
mkdir -p backups

# Set up SSH key if not exists
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "Generating SSH key..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    echo "SSH key generated. Add the public key to your EC2 instances:"
    cat ~/.ssh/id_rsa.pub
fi

# Create vault file template
if [ ! -f vault.yml ]; then
    echo "Creating vault file template..."
    cat > vault.yml << EOF
# Ansible Vault file for sensitive data
# Encrypt this file with: ansible-vault encrypt vault.yml
# Edit with: ansible-vault edit vault.yml

vault_django_secret_key: "your-django-secret-key-here"
vault_db_name: "todoapp"
vault_db_user: "todoapp"
vault_db_password: "your-database-password-here"
vault_email_user: "your-email@example.com"
vault_email_password: "your-email-password-here"
EOF
    echo "Vault file created. Please edit vault.yml with your sensitive data and encrypt it."
fi

# Create deployment script
cat > deploy.sh << 'EOF'
#!/bin/bash

# TodoApp deployment script

set -e

ENVIRONMENT=${1:-production}
BACKUP_ID=${2:-}

echo "Deploying TodoApp to $ENVIRONMENT environment..."

# Check if vault file exists and is encrypted
if [ ! -f vault.yml ]; then
    echo "Error: vault.yml not found. Please create and encrypt it first."
    exit 1
fi

# Run deployment playbook
if [ -n "$BACKUP_ID" ]; then
    echo "Rolling back to backup: $BACKUP_ID"
    ansible-playbook -i inventory/hosts.yml playbooks/rollback.yml \
        --extra-vars "@vault.yml" \
        --extra-vars "rollback_backup_id=$BACKUP_ID" \
        --ask-vault-pass
else
    echo "Deploying application..."
    ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml \
        --extra-vars "@vault.yml" \
        --ask-vault-pass
fi

echo "Deployment completed successfully!"
EOF

chmod +x deploy.sh

# Create health check script
cat > health-check.sh << 'EOF'
#!/bin/bash

# TodoApp health check script

set -e

echo "Running health check..."

ansible-playbook -i inventory/hosts.yml playbooks/health-check.yml

echo "Health check completed!"
EOF

chmod +x health-check.sh

echo "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit vault.yml with your sensitive data"
echo "2. Encrypt vault.yml: ansible-vault encrypt vault.yml"
echo "3. Update inventory/hosts.yml with your server details"
echo "4. Run deployment: ./deploy.sh"
echo "5. Check health: ./health-check.sh"
