#!/bin/bash

# Update system
yum update -y

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
yum install -y git

# Install Python and pip
yum install -y python3 python3-pip

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Create application directory
mkdir -p /opt/todoapp
cd /opt/todoapp

# Clone the repository (this will be updated by Ansible)
# git clone https://github.com/yourusername/django-todo-app.git .

# Create environment file
cat > .env << EOF
DEBUG=False
SECRET_KEY=${secret_key}
DATABASE_URL=postgresql://${db_username}:${db_password}@${db_host}:5432/${db_name}
REDIS_URL=redis://${redis_host}:6379/0
ALLOWED_HOSTS=*
STATIC_URL=https://s3.amazonaws.com/your-static-bucket/
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media
ENVIRONMENT=${environment}
EOF

# Create docker-compose.prod.yml
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn todo_project.wsgi:application --bind 0.0.0.0:8000"
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
    env_file:
      - .env
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web
    restart: unless-stopped

volumes:
  static_volume:
  media_volume:
EOF

# Create nginx configuration
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    upstream django {
        server web:8000;
    }

    server {
        listen 80;
        server_name _;
        client_max_body_size 20M;

        location /static/ {
            alias /app/staticfiles/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /app/media/;
            expires 1y;
            add_header Cache-Control "public";
        }

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
        }

        location /health/ {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF

# Set proper permissions
chown -R ec2-user:ec2-user /opt/todoapp

# Create systemd service for the application
cat > /etc/systemd/system/todoapp.service << EOF
[Unit]
Description=TodoApp Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/todoapp
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0
User=ec2-user

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
systemctl enable todoapp.service

# Create log directory
mkdir -p /var/log/todoapp
chown ec2-user:ec2-user /var/log/todoapp

# Install CloudWatch agent for logging
yum install -y amazon-cloudwatch-agent

# Create CloudWatch agent configuration
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << 'EOF'
{
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/todoapp/*.log",
                        "log_group_name": "/aws/ec2/todoapp",
                        "log_stream_name": "{instance_id}"
                    }
                ]
            }
        }
    }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
    -s

# Signal that the user data script has completed
echo "User data script completed at $(date)" >> /var/log/user-data.log
