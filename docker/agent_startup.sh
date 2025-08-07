#!/bin/bash

# Start the MCP server only if required environment is present
REQUIRED_VARS=(BASE_URL SUBMISSION_URL RESULTS_URL PHPSESSID PID)
MISSING_VAR=false
for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var}" ]; then
    MISSING_VAR=true
  fi
done

if [ "$MISSING_VAR" = false ]; then
  echo "Starting MCP server..."
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
          # Don't exit; proceed to shell so user can still work locally
          break
      fi
  done
else
  echo "MCP server env not fully configured; skipping MCP startup."
fi

# Initialize opencode
echo "Initializing opencode..."
# Start OpenCode in the agent workspace; if it exits, continue to shell
(cd /workspace/agent && opencode || true)

# Start bash session for the user
bash