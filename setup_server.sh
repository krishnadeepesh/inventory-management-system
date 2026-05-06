#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting Server Setup..."

# Update system packages
apt update && apt upgrade -y

# Install essential dependencies: Python, MySQL, Nginx, and build tools
apt install -y python3-venv python3-pip python3-dev default-libmysqlclient-dev build-essential pkg-config mysql-server nginx git

# Setup MySQL Database and User
# Note: AWS Ubuntu doesn't always set a root password, we set it to match your local settings
mysql -e "CREATE DATABASE IF NOT EXISTS inventory_db;"
# Create user (ignoring error if it already exists)
mysql -e "CREATE USER IF NOT EXISTS 'root'@'localhost' IDENTIFIED BY 'root';" || true
# Alternatively, alter user if it already exists to set the password
mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';" || true
mysql -e "GRANT ALL PRIVILEGES ON inventory_db.* TO 'root'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

# Change ownership of the project directory to ubuntu user
chown -R ubuntu:ubuntu /home/ubuntu/inventory

# Setup Python Virtual Environment (Run as ubuntu user)
sudo -u ubuntu bash -c "python3 -m venv /home/ubuntu/inventory/venv"
sudo -u ubuntu bash -c "source /home/ubuntu/inventory/venv/bin/activate && pip install -r /home/ubuntu/inventory/requirements.txt"

# Run Django Migrations and Collect Static Files
sudo -u ubuntu bash -c "source /home/ubuntu/inventory/venv/bin/activate && python3 /home/ubuntu/inventory/manage.py makemigrations"
sudo -u ubuntu bash -c "source /home/ubuntu/inventory/venv/bin/activate && python3 /home/ubuntu/inventory/manage.py migrate"
sudo -u ubuntu bash -c "source /home/ubuntu/inventory/venv/bin/activate && python3 /home/ubuntu/inventory/manage.py collectstatic --noinput"

# Setup Gunicorn Systemd Service
cat <<EOF > /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/inventory
ExecStart=/home/ubuntu/inventory/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/inventory/inventory_system.sock inventory_system.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Start and Enable Gunicorn
systemctl daemon-reload
systemctl start gunicorn
systemctl enable gunicorn

# Setup Nginx Configuration
cat <<EOF > /etc/nginx/sites-available/inventory
server {
    listen 80;
    server_name _;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/ubuntu/inventory;
    }

    location /media/ {
        root /home/ubuntu/inventory;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/inventory/inventory_system.sock;
    }
}
EOF

# Enable Nginx config and remove default
ln -sf /etc/nginx/sites-available/inventory /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Restart Nginx
systemctl restart nginx

echo "======================================================"
echo "Deployment Complete!"
echo "Your application should now be accessible via the AWS public IP address."
echo "======================================================"
