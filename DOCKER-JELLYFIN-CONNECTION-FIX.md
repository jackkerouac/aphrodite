# Troubleshooting Jellyfin Connection in Docker

This guide addresses common issues with the Jellyfin connection test when running Aphrodite in Docker.

## Problem

When clicking the "Test Connection" button on the Settings API tab, you receive a 400 BAD REQUEST error.

## Solutions

### Solution 1: Update to the Latest Docker Configuration

1. Use the improved Dockerfile and docker-compose files included in this update:
   - `Dockerfile.improved` 
   - `docker-compose.improved.yml`

2. Run the application using the provided scripts:
   - On Linux/Mac: `./run-docker.sh`
   - On Windows: `run-docker.bat`

### Solution 2: Check Jellyfin Server Accessibility

1. Make sure your Jellyfin server URL is accessible from within the Docker container:

   - If using `localhost` or `127.0.0.1` in your URL, change it to your machine's actual IP address on your network, as `localhost` in the container refers to the container itself, not your host machine.
   
   - For example, change `http://localhost:8096` to `http://192.168.1.100:8096` (using your actual IP address)

2. If your Jellyfin server is also running in Docker:

   - Make sure both containers are on the same Docker network
   - Use the container name as the hostname (e.g., `http://jellyfin:8096`)

### Solution 3: Check Firewall Rules

Ensure your firewall is not blocking access from the Docker container to your Jellyfin server:

- Windows Firewall: Add an inbound rule for the Jellyfin port (typically 8096)
- Router Firewall: If applicable, make sure internal traffic is allowed

### Solution 4: Verify API Key and User ID

1. Double-check that your Jellyfin API key and User ID are correct
2. Generate a new API key in Jellyfin if necessary

### Solution 5: Check Docker Logs for Specific Errors

```bash
docker-compose -f docker-compose.improved.yml logs -f aphrodite
```

Look for specific error messages that might indicate the source of the problem.

## Additional Debugging Tips

### Test Direct Connection from Inside Container

```bash
# Access the container shell
docker exec -it aphrodite-app bash

# Install curl if needed
apt-get update && apt-get install -y curl

# Test connection to Jellyfin
curl -H "X-Emby-Token: your-api-key" "http://your-jellyfin-url:8096/System/Info"
```

### Verify Network Configuration

```bash
# Check what networks the container can access
docker exec -it aphrodite-app ping your-jellyfin-server-ip

# If that doesn't work, try a public DNS
docker exec -it aphrodite-app ping 8.8.8.8
```

If you continue to experience issues after trying these solutions, please open an issue on the GitHub repository with the complete error logs from the Docker container.
