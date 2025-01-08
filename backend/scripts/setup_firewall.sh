# backend/scripts/setup_firewall.sh
#!/bin/bash

# Basic UFW Firewall Configuration Script for Pintar Ekspor

echo "Setting up basic firewall rules..."

# Reset UFW to default
sudo ufw --force reset

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (port 22)
sudo ufw allow ssh

# Allow HTTP/HTTPS (ports 80, 443)
sudo ufw allow http
sudo ufw allow https

# Allow PostgreSQL only from localhost
sudo ufw allow from 127.0.0.1 to any port 5432

# Allow application port (8000) only through nginx
sudo ufw allow 8000/tcp

# Basic rate limiting for SSH
sudo ufw limit ssh/tcp

# Enable UFW
sudo ufw --force enable

echo "Firewall configuration completed!"
echo "Current UFW status:"
sudo ufw status verbose