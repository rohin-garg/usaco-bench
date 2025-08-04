#!/bin/bash
if [ -f .env ]; then
  source .env
fi

PROBLEM_SOURCE=$1
MODEL=$2
MODEL_PROVIDER_API_KEY=$3

# If the problem source is a local path, copy it to the build context
if [[ $PROBLEM_SOURCE != http* ]]; then
    if [ -d "$PROBLEM_SOURCE" ]; then
        echo "Copying problem files from $PROBLEM_SOURCE"
        cp -r "$PROBLEM_SOURCE" problem_files
        PROBLEM_SOURCE=problem_files
    else
        echo "Error: Local path $PROBLEM_SOURCE not found."
        exit 1
    fi
fi

# Build the Docker image
docker build -t usaco-bench-env --build-arg PROBLEM_SOURCE="$PROBLEM_SOURCE" --build-arg MODEL="$MODEL" --build-arg MODEL_PROVIDER_API_KEY="$MODEL_PROVIDER_API_KEY" .

# Clean up copied problem files
if [[ $PROBLEM_SOURCE == problem_files ]]; then
    rm -rf problem_files
fi

# Run the Docker container
docker run -it --rm --env-file .env usaco-bench-env