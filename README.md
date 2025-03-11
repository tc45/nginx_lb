# NGINX Manager

A robust Python-based automation tool for managing NGINX load balancer configurations. This tool simplifies the process of setting up and managing NGINX servers with support for both High Availability (HA) and Primary/Backup configurations.

## Features

- **Easy Setup**: Automated NGINX installation and configuration
- **Flexible Load Balancing**:
  - High Availability (HA) configuration with multiple active servers
  - Primary/Backup configuration with failover support
- **Server Management**:
  - Add new server configurations with custom domains and ports
  - Remove existing server configurations with automatic backup
  - List all configured servers with their status and metrics
- **Configuration Backup**: Automatic backup of removed configurations
- **Health Monitoring**: Track server status and response metrics
- **Template-based Configuration**: Uses Jinja2 templates for consistent server configurations

## Prerequisites

- Linux-based system with sudo privileges
- Python 3.x
- NGINX

## Setup

1. Clone this repository and navigate to the project directory

2. Run the initial setup script:
   ```bash
   bash scripts/setup.sh
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

## Usage

The tool provides several commands for managing your NGINX configuration:

### Initial Setup
```bash
python3 nginx.py setup
```
This command installs NGINX and creates necessary directories for configuration management.

### Adding a New Server
```bash
python3 nginx.py addserver
```
Interactive prompts will guide you through:
- Server name configuration (e.g., example.com)
- Configuration type selection:
  1. High Availability (HA) - Two active servers
  2. Primary/Backup - One primary with failover backup
- Port configuration
- Upstream server details

### Removing a Server
```bash
python3 nginx.py removeserver
```
Removes a server configuration while automatically creating a backup in the `nginx_config_backup/` directory.

### Listing Servers
```bash
python3 nginx.py list
```
Displays a table of all configured servers showing:
- Site name and port
- Upstream server configurations
- Current status
- Performance metrics

## Configuration Backup

All removed server configurations are automatically backed up to the `nginx_config_backup/` directory, allowing for easy restoration if needed.

## Directory Structure

- `sites-enabled/` - Active NGINX server configurations
- `templates/` - Jinja2 templates for server configuration
- `nginx_config_backup/` - Backup storage for removed configurations

## Error Handling

The tool includes comprehensive error handling and logging to help troubleshoot any issues that may arise during configuration management.