import os
import shutil
import argparse
from tabulate import tabulate

# Get the current directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to the current directory
NGINX_CONFIG_PATH = os.path.join(SCRIPT_DIR, "sites-enabled")
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "templates", "site.template")
BACKUP_PATH = os.path.join(SCRIPT_DIR, "nginx_config_backup")

def setup_nginx():
    """Sets up NGINX and necessary directories."""
    print("Setting up NGINX load balancer...")
    os.system("sudo apt update && sudo apt install -y nginx")
    if not os.path.exists(NGINX_CONFIG_PATH):
        os.makedirs(NGINX_CONFIG_PATH)
    if not os.path.exists(BACKUP_PATH):
        os.makedirs(BACKUP_PATH)
    print("NGINX setup completed.")

def add_server():
    """Adds a new server configuration to NGINX."""
    server_name = input("Enter the server name (e.g., example.com): ")
    upstream = input("Enter the upstream backend (e.g., on-prem.example.com): ")
    backup = input("Enter the backup backend (e.g., cloud.example.com): ")

    with open(TEMPLATE_PATH, "r") as template_file:
        config = template_file.read().replace("{{SERVER_NAME}}", server_name) \
                                    .replace("{{UPSTREAM}}", upstream) \
                                    .replace("{{BACKUP}}", backup)

    config_path = os.path.join(NGINX_CONFIG_PATH, f"{server_name}.conf")
    with open(config_path, "w") as conf_file:
        conf_file.write(config)

    print(f"Server {server_name} added successfully.")
    os.system("sudo nginx -t && sudo systemctl reload nginx")

def remove_server():
    """Removes a server configuration from NGINX."""
    server_name = input("Enter the server name to remove: ")
    config_path = os.path.join(NGINX_CONFIG_PATH, f"{server_name}.conf")

    if os.path.exists(config_path):
        shutil.move(config_path, os.path.join(BACKUP_PATH, f"{server_name}.conf"))
        print(f"Server {server_name} removed and backed up.")
        os.system("sudo nginx -t && sudo systemctl reload nginx")
    else:
        print("Server not found.")

def list_servers():
    """Lists all configured servers and their upstream connectors with status and metrics."""
    print("Listing all configured servers and upstream connectors:")
    server_data = []

    for config_file in os.listdir(NGINX_CONFIG_PATH):
        if config_file.endswith(".conf"):
            server_name = None
            upstreams = []
            port = "80"  # Default port for HTTP
            with open(os.path.join(NGINX_CONFIG_PATH, config_file), "r") as f:
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
    print(f"\nTotal servers configured: {len(server_data)}")

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