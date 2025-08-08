#!/bin/bash
set -e

# Find and source .env from either current dir or docker/.env
ENV_PATH=""
if [ -f .env ]; then
  ENV_PATH=".env"
elif [ -f docker/.env ]; then
  ENV_PATH="docker/.env"
fi

if [ -n "$ENV_PATH" ]; then
  echo "Loading environment from $ENV_PATH"
  # shellcheck disable=SC1090
  source "$ENV_PATH"
fi

PROBLEM_SOURCE=$1
MODEL=$2
MODEL_PROVIDER_API_KEY=$3

# Prepare build context for local problem files (match Dockerfile expectation)
mkdir -p docker/problem_files

if [ -n "$PROBLEM_SOURCE" ] && [[ $PROBLEM_SOURCE != http* ]]; then
  if [ -d "$PROBLEM_SOURCE" ]; then
    echo "Copying problem files from $PROBLEM_SOURCE"
    rm -rf docker/problem_files/*
    cp -r "$PROBLEM_SOURCE"/* docker/problem_files/
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
  .

# Clean up copied problem files
rm -rf docker/problem_files

# Calculate timeout (TIME_LIMIT + 1 minute, default to 31 minutes if not set)
TIMEOUT_MINUTES=$((${TIME_LIMIT:-30} + 1))
TIMEOUT_SECONDS=$((TIMEOUT_MINUTES * 60))

echo "Starting container with ${TIMEOUT_MINUTES} minute timeout..."

# Generate a unique container name
CONTAINER_NAME="usaco-bench-$(date +%s)-$$"

# Determine timeout command (macOS uses gtimeout from coreutils)
TIMEOUT_CMD=""
if command -v timeout >/dev/null 2>&1; then
  TIMEOUT_CMD="timeout"
elif command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_CMD="gtimeout"
else
  echo "Warning: Neither 'timeout' nor 'gtimeout' found. Running without a hard timeout."
fi

# Run the Docker container with timeout when available
ENV_FILE_ARG=""
if [ -n "$ENV_PATH" ]; then
  # If the env file looks like a plain KEY=VALUE file, pass it directly.
  # Otherwise (contains bashisms like `export` or `.`), we'll pass vars explicitly.
  if grep -qE '^\s*(export|\.)\b' "$ENV_PATH"; then
    echo "Warning: $ENV_PATH contains bash-specific syntax; passing envs explicitly."
  else
    ENV_FILE_ARG="--env-file $ENV_PATH"
  fi
fi
# Always forward model envs as runtime envs so opencode can read them
if [ -n "$MODEL_PROVIDER_API_KEY" ]; then
  ENV_FILE_ARG="$ENV_FILE_ARG -e MODEL_PROVIDER_API_KEY=$MODEL_PROVIDER_API_KEY"
fi
if [ -n "$MODEL" ]; then
  ENV_FILE_ARG="$ENV_FILE_ARG -e MODEL=$MODEL"
fi
# Also forward MCP/time-limit related vars explicitly if set
FORWARD_VARS=(BASE_URL SUBMISSION_URL RESULTS_URL PHPSESSID PID SUBMISSION_LIMIT TIME_LIMIT)
for var in "${FORWARD_VARS[@]}"; do
  if [ -n "${!var}" ]; then
    ENV_FILE_ARG="$ENV_FILE_ARG -e $var=${!var}"
  fi
done
if [ -n "$TIMEOUT_CMD" ]; then
  $TIMEOUT_CMD ${TIMEOUT_SECONDS}s docker run -it --name "$CONTAINER_NAME" $ENV_FILE_ARG usaco-bench-env
else
  docker run -it --name "$CONTAINER_NAME" $ENV_FILE_ARG usaco-bench-env
fi

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

if [ -n "$TIMEOUT_CMD" ] && [ $DOCKER_EXIT_CODE -eq 124 ]; then
    echo "Container was terminated due to timeout after ${TIMEOUT_MINUTES} minutes"
else
    echo "Container completed normally"
fi