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
COPY agent_files/test_mcp_server.py .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set up the agent
WORKDIR /workspace/agent

ARG MODEL

# Copy and modify the opencode config (place in workspace and user config)
COPY agent_files/opencode_config.json /workspace/opencode_config.json
RUN mkdir -p /root/.config/opencode && \
    if [ -n "$MODEL" ]; then \
      if echo "$MODEL" | grep -q '^openrouter/'; then \
        FULL_MODEL="$MODEL"; SHORT_MODEL="${MODEL#openrouter/}"; \
      else \
        FULL_MODEL="openrouter/$MODEL"; SHORT_MODEL="$MODEL"; \
      fi; \
      tmpfile=$(mktemp); \
      jq --arg short "$SHORT_MODEL" --arg full "$FULL_MODEL" \
        '.provider.openrouter.models = {($short): {}} | .model = $full' \
        /workspace/opencode_config.json > "$tmpfile" && mv "$tmpfile" /workspace/opencode_config.json; \
    fi && \
    cp /workspace/opencode_config.json /root/.config/opencode/opencode.json

# copy instructions file
COPY agent_files/INSTRUCTIONS.md /INSTRUCTIONS.md

# use opencode agent
RUN npm i -g opencode-ai@latest

# Download or copy problem files
ARG PROBLEM_SOURCE
# Stage any local problem files prepared by the runner (may be empty)
COPY docker/problem_files/ /docker_problem_files/

# If a URL is provided, download and unzip it. Otherwise, if local problem files exist, copy them into the working directory
RUN set -e; \
    if [ -n "$PROBLEM_SOURCE" ] && echo "$PROBLEM_SOURCE" | grep -qE '^https?://'; then \
      echo "Downloading problem from URL: $PROBLEM_SOURCE"; \
      curl -L -o /workspace/agent/problem.zip "$PROBLEM_SOURCE" && \
      unzip -o /workspace/agent/problem.zip -d /workspace/agent && \
      rm /workspace/agent/problem.zip; \
    elif [ -d /docker_problem_files ] && [ "$(ls -A /docker_problem_files 2>/dev/null)" ]; then \
      echo "Copying staged local problem files into workspace"; \
      cp -r /docker_problem_files/* /workspace/agent/; \
    else \
      echo "No problem files provided"; \
    fi; \
    rm -rf /docker_problem_files

# Copy the startup script
COPY docker/agent_startup.sh /agent_startup.sh
RUN chmod +x /agent_startup.sh

# Create log directory and ensure it's accessible
RUN mkdir -p /tmp && chmod 777 /tmp

CMD ["/agent_startup.sh"]