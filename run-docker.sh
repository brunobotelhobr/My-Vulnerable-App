#/bin/bash

# Build
docker build -t brunobotelhobr/my-vulnerable-app:0.0.1 .

# Run & rm
docker run --rm --name my-vulnerable-app -d -p 8000:8000 brunobotelhobr/my-vulnerable-app:0.0.1

# Upload the image to Docker Hub (optional)
docker push brunobotelhobr/my-vulnerable-app:0.0.1

# Stop the container
docker stop my-vulnerable-app

# Remove the container
docker rm my-vulnerable-app

# Remove the image
docker rmi my-vulnerable-app