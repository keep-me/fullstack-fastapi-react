#!/bin/bash

echo "=== Docker Security Check ==="
echo "Date: $(date)"
echo

# 1. Image vulnerability scan
echo "1. Scanning images for vulnerabilities..."
for image in $(docker images --format "{{.Repository}}:{{.Tag}}" | grep -v "<none>"); do
    echo "Scanning $image..."
    trivy image --severity HIGH,CRITICAL --quiet $image | head -20
done

# 2. Check open ports
echo -e "\n2. Checking open ports..."
nmap -p 1-10000 localhost | grep open

# 3. Check privileged containers
echo -e "\n3. Checking privileged containers..."
docker ps --format "table {{.Names}}\t{{.Status}}" --filter "status=running"
docker inspect $(docker ps -q) | jq '.[] | select(.HostConfig.Privileged==true) | .Name'

# 4. Check resource usage
echo -e "\n4. Resource usage..."
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemPerc}}\t{{.NetIO}}"

# 5. Check logs for errors
echo -e "\n5. Checking logs for errors..."
for container in $(docker ps --format "{{.Names}}"); do
    errors=$(docker logs --since 1h $container 2>&1 | grep -i "error\|warning\|exception" | wc -l)
    if [ $errors -gt 0 ]; then
        echo "$container: $errors errors/warnings in last hour"
    fi
done

# 6. Check disk usage
echo -e "\n6. Disk usage..."
docker system df -v | head -10

echo -e "\n=== Security check completed ==="