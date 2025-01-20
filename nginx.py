import os
import shutil
import argparse
from tabulate import tabulate
import logging
from jinja2 import Template

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the current directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to the current directory
NGINX_CONFIG_PATH = os.path.join(SCRIPT_DIR, "sites-enabled")
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "templates", "site.template")
BACKUP_PATH = os.path.join(SCRIPT_DIR, "nginx_config_backup")
UPSTREAM_CONFIG_PATH = os.path.join(SCRIPT_DIR, "nginx.conf.template")

def setup_nginx():
    """Sets up NGINX and necessary directories."""
    logging.info("Setting up NGINX load balancer...")
    os.system("sudo apt update && sudo apt install -y nginx")
    if not os.path.exists(NGINX_CONFIG_PATH):
        os.makedirs(NGINX_CONFIG_PATH)
    if not os.path.exists(BACKUP_PATH):
        os.makedirs(BACKUP_PATH)
    logging.info("NGINX setup completed successfully.")

def add_server():
    """Adds a new server configuration to NGINX."""
    server_name = input("Enter the server name (e.g., example.com): ")
    logging.info(f"Adding server configuration for {server_name}...")

    # Prompt for upstream server configuration
    config_type = int(input("Choose configuration type (1: HA, 2: Primary/Backup): "))
    
    # Get the port number for the server block
    port = input("Enter the port number for the server (default is 80): ") or "80"

    upstream_name = f"{server_name.replace('.', '_')}_backend"
    upstream_servers = []

    if config_type == 1:  # HA configuration
        for i in range(2):  # Always two servers for HA
            upstream_server = input(f"Enter upstream server {i + 1} (e.g., on-prem.example.com:port): ")
            if ':' not in upstream_server:
                upstream_server = f"{upstream_server}:{port}"  # Use the same port for HA
            upstream_servers.append(upstream_server)  # Append without 'server' keyword

    elif config_type == 2:  # Primary/Backup configuration
        primary_server = input("Enter primary upstream server (e.g., on-prem.example.com:port): ")
        if ':' not in primary_server:
            primary_server = f"{primary_server}:{port}"  # Use the specified port
        upstream_servers.append(f"{primary_server} max_fails=3 fail_timeout=10s")

        backup_server = input("Enter backup upstream server (e.g., on-prem.example.com:port): ")
        if ':' not in backup_server:
            backup_server = f"{backup_server}:{port}"  # Use the specified port
        upstream_servers.append(f"{backup_server} backup")

    # Load the configuration template
    with open(TEMPLATE_PATH, "r") as template_file:
        template_content = template_file.read()

    # Render the configuration using Jinja2
    template = Template(template_content)
    config = template.render(
        UPSTREAM_NAME=upstream_name,
        UPSTREAM_SERVERS=upstream_servers,
        SERVER_NAME=server_name,
        PORT=port
    )

    # Log the generated configuration
    logging.info(f"Generated configuration for {server_name}:\n{config}")

    # Write to the appropriate file in /etc/nginx/sites-available
    config_path = os.path.join("/etc/nginx/sites-available", f"{server_name}.conf")
    with open(config_path, "w") as conf_file:
        conf_file.write(config)

    # Create a symbolic link in /etc/nginx/sites-enabled
    os.system(f"sudo ln -s {config_path} /etc/nginx/sites-enabled/{server_name}.conf")

    logging.info(f"Server {server_name} added successfully.")
    os.system("sudo nginx -t && sudo systemctl reload nginx")
    logging.info(f"Configuration for {server_name} has been applied.")

def remove_server():
    """Removes a server configuration from NGINX."""
    server_name = input("Enter the server name to remove: ")
    logging.info(f"Removing server configuration for {server_name}...")

    config_path = os.path.join("/etc/nginx/sites-available", f"{server_name}.conf")
    symlink_path = os.path.join("/etc/nginx/sites-enabled", f"{server_name}.conf")

    if os.path.exists(config_path):
        # Remove the symbolic link
        if os.path.exists(symlink_path):
            os.remove(symlink_path)
            logging.info(f"Removed symbolic link for {server_name} from /etc/nginx/sites-enabled.")
        
        # Move the config file to backup
        shutil.move(config_path, os.path.join(BACKUP_PATH, f"{server_name}.conf"))
        logging.info(f"Server {server_name} removed and backed up.")
        os.system("sudo nginx -t && sudo systemctl reload nginx")
        logging.info(f"Configuration for {server_name} has been removed.")
    else:
        logging.warning("Server not found.")

def list_servers():
    """Lists all configured servers and their upstream connectors with status and metrics."""
    logging.info("Listing all configured servers and upstream connectors:")
    server_data = []

    for config_file in os.listdir("/etc/nginx/sites-enabled"):
        if config_file.endswith(".conf"):
            server_name = None
            upstreams = []
            port = "80"  # Default port for HTTP
            with open(os.path.join("/etc/nginx/sites-enabled", config_file), "r") as f:
                for line in f:
                    if "server_name" in line:
                        server_name = line.split()[1].strip().rstrip(';')
                    if "proxy_pass" in line:
                        # Extract upstream and port
                        upstream = line.split()[1].strip().rstrip(';')
                        upstreams.append(upstream)
                    if "listen" in line:
                        # Extract the port from the listen directive
                        port = line.split()[1].strip().rstrip(';')

            if server_name and upstreams:
                for upstream in upstreams:
                    # Split upstream to get the host and port if specified
                    if ':' in upstream:
                        host, upstream_port = upstream.split(':')
                    else:
                        host, upstream_port = upstream, "80"  # Default port for HTTP

                    # Here we can simulate the status and metrics for demonstration
                    status = "active"  # This would be determined by actual health checks
                    metrics = "100ms"  # Placeholder for actual metrics

                    # Append the data in the new format
                    server_data.append([f"{server_name}:{port}", f"{host}:{upstream_port}", status, metrics])

    # Print the table using tabulate
    print(tabulate(server_data, headers=["Site:Port", "Upstream:Port", "Status", "Metrics"], tablefmt="grid"))
    logging.info(f"Total servers configured: {len(server_data)}")

def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(description="NGINX Automation Tool")
    parser.add_argument("action", choices=["setup", "addserver", "removeserver", "list"], help="Action to perform")

    args = parser.parse_args()

    if args.action == "setup":
        setup_nginx()
    elif args.action == "addserver":
        add_server()
    elif args.action == "removeserver":
        remove_server()
    elif args.action == "list":
        list_servers()

if __name__ == "__main__":
    main()