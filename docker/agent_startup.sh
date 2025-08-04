#!/bin/bash

# Start the MCP server in the background
python3 /server/mcp_server.py &

# Wait for MCP server to be ready
echo "Waiting for MCP server to be ready..."
for i in $(seq 1 10); do
    resp=$(curl -s -X POST http://127.0.0.1:8001/startup || true)
    if [ "$resp" = "OK" ]; then
        echo "MCP server startup successful."
        break
    fi
    echo "Waiting for MCP server to be ready... (attempt $i)"
    sleep 3
    if [ $i -eq 10 ]; then
        echo "MCP server did not respond with OK after 10 attempts."
        exit 1
    fi
done

# Initialize opencode
echo "Initializing opencode..."
# Attempt to run /init non-interactively.
# This may need adjustment based on opencode's behavior.
(cd /workspace/agent && echo "/init" | opencode)

# Start bash session for the user
bash