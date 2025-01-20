# NGINX Manager

This project provides a Python-based automation tool for managing NGINX configurations on a load balancer.

## Setup

1. Run the initial setup script:
   ```bash
   bash scripts/setup.sh
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Use the Python script to manage NGINX:
   ```bash
   python3 nginx.py setup
   python3 nginx.py addserver
   python3 nginx.py removeserver
   python3 nginx.py list
   ```

## Version Control

Changes to NGINX configurations are tracked in the `nginx_config_backup/` directory.