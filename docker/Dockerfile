FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_VERSION=22

# Install base dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    jq \
    python3-pip \
    unzip \
    build-essential \
    g++ \
    git \
  && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - &&     apt-get install -y nodejs

# Set up the server
WORKDIR /server
COPY agent_files/mcp_server.py .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set up the agent
WORKDIR /workspace/agent

ARG MODEL
ARG MODEL_PROVIDER_API_KEY

# Copy and modify the opencode config
COPY agent_files/opencode_config.json /tmp/opencode_config.json
RUN mkdir -p /root/.config/opencode && \
    jq --arg model "$MODEL" --arg apikey "$MODEL_PROVIDER_API_KEY" \
      '. + {model: $model} | .providers.openrouter.apiKey = $apikey' \
      /tmp/opencode_config.json > /root/.config/opencode/opencode.json

# copy instructions file
COPY agent_files/INSTRUCTIONS.md /INSTRUCTIONS.md

# use opencode agent
RUN npm i -g opencode-ai@latest

# Download or copy problem files
ARG PROBLEM_SOURCE
# Always copy any local problem files prepared by the runner into the image (may be empty)
COPY docker/problem_files/ /workspace/agent/problem_files/

# If a URL is provided, download and unzip it. Otherwise, if local problem files exist, copy them into the working directory
RUN set -e; \
    if [ -n "$PROBLEM_SOURCE" ] && echo "$PROBLEM_SOURCE" | grep -qE '^https?://'; then \
      echo "Downloading problem from URL: $PROBLEM_SOURCE"; \
      curl -L -o /workspace/agent/problem.zip "$PROBLEM_SOURCE" && \
      unzip -o /workspace/agent/problem.zip -d /workspace/agent && \
      rm /workspace/agent/problem.zip; \
    else \
      if [ -d /workspace/agent/problem_files ] && [ "$(ls -A /workspace/agent/problem_files 2>/dev/null)" ]; then \
        echo "Copying local problem files into workspace"; \
        cp -r /workspace/agent/problem_files/* /workspace/agent/; \
      else \
        echo "No local problem files provided"; \
      fi; \
    fi

# Copy the startup script
COPY docker/agent_startup.sh /agent_startup.sh
RUN chmod +x /agent_startup.sh

# Create log directory and ensure it's accessible
RUN mkdir -p /tmp && chmod 777 /tmp

CMD ["/agent_startup.sh"]