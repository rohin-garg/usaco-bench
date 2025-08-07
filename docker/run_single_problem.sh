#!/bin/bash
if [ -f .env ]; then
  source .env
fi

PROBLEM_SOURCE=$1
MODEL=$2
MODEL_PROVIDER_API_KEY=$3

# Prepare build context for local problem files
mkdir -p problem_files

if [ -n "$PROBLEM_SOURCE" ] && [[ $PROBLEM_SOURCE != http* ]]; then
  if [ -d "$PROBLEM_SOURCE" ]; then
    echo "Copying problem files from $PROBLEM_SOURCE"
    rm -rf problem_files/*
    cp -r "$PROBLEM_SOURCE"/* problem_files/
  else
    echo "Error: Local path $PROBLEM_SOURCE not found."
    exit 1
  fi
fi

# Build the Docker image from repo root so Dockerfile can COPY files reliably
docker build \
  -f docker/Dockerfile \
  -t usaco-bench-env \
  --build-arg PROBLEM_SOURCE="$PROBLEM_SOURCE" \
  --build-arg MODEL="$MODEL" \
  --build-arg MODEL_PROVIDER_API_KEY="$MODEL_PROVIDER_API_KEY" \
  .

# Clean up copied problem files
rm -rf problem_files

# Calculate timeout (TIME_LIMIT + 1 minute, default to 31 minutes if not set)
TIMEOUT_MINUTES=$((${TIME_LIMIT:-30} + 1))
TIMEOUT_SECONDS=$((TIMEOUT_MINUTES * 60))

echo "Starting container with ${TIMEOUT_MINUTES} minute timeout..."

# Generate a unique container name
CONTAINER_NAME="usaco-bench-$(date +%s)-$$"

# Run the Docker container with timeout
ENV_FILE_ARG=""
if [ -f .env ]; then
  ENV_FILE_ARG="--env-file .env"
fi
timeout ${TIMEOUT_SECONDS}s docker run --name "$CONTAINER_NAME" $ENV_FILE_ARG usaco-bench-env

# Capture the exit code
DOCKER_EXIT_CODE=$?

echo "Container finished with exit code: $DOCKER_EXIT_CODE"

# Copy the log file from the container (whether it finished normally or timed out)
echo "Extracting log file..."
LOG_FILENAME="submission_log_$(date +%Y%m%d_%H%M%S).json"

if docker cp "$CONTAINER_NAME":/tmp/submission_log.json "./$LOG_FILENAME" 2>/dev/null; then
    echo "Log file saved as: $LOG_FILENAME"
else
    echo "Warning: Could not extract log file (container may not have created one)"
fi

# Force kill and remove the container
echo "Cleaning up container..."
docker kill "$CONTAINER_NAME" 2>/dev/null
docker rm "$CONTAINER_NAME" 2>/dev/null

if [ $DOCKER_EXIT_CODE -eq 124 ]; then
    echo "Container was terminated due to timeout after ${TIMEOUT_MINUTES} minutes"
else
    echo "Container completed normally"
fi