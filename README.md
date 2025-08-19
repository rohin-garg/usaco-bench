# Programming Problem Benchmarking Framework

Sandboxed Docker environment to benchmark AI coding agents (OpenCode) on competitive programming problems, using either local problem files or an online judge via an MCP server.

## Components
- **OpenCode Agent**: AI agent running inside the container
- **MCP Server**: Optional. Exposes `submit_solution` and `get_remaining_time_and_submissions` to the agent
- **Docker Environment**: Reproducible, isolated workspace
- **Problem Source**: Local directory or downloadable archive URL

## Requirements
- Docker running on your machine
- Internet connection (for online judge submissions or URL sources)
- macOS users: the run script uses `timeout`. If your OS doesn’t provide it, either install coreutils (`brew install coreutils` and alias `timeout` to `gtimeout`) or remove the timeout wrapper in the script.

## Configuration (.env)
Create `docker/.env` when using an online judge or to set defaults:

```bash
# MCP Server Configuration (you must specify this. currently only works with confidential USACO judge)
BASE_URL='<YOUR_JUDGE_BASE_URL>'
SUBMISSION_URL='<YOUR_JUDGE_SUBMISSION_URL>'
RESULTS_URL='<YOUR_JUDGE_RESULTS_URL>'
PHPSESSID='<YOUR_SESSION_ID>'
PID='<PROBLEM_ID>'

# Submission/time limits (minutes)
SUBMISSION_LIMIT=50
TIME_LIMIT=30

# Model configuration (can also be passed as args)
MODEL_PROVIDER_API_KEY='<YOUR_OPENROUTER_API_KEY>'
MODEL='anthropic/claude-3.5-sonnet'
```

Notes:
- `MODEL` and `MODEL_PROVIDER_API_KEY` can be passed to the build via script arguments.

## Quick Start
1) Navigate to the docker directory:
```bash
cd docker
```

2) Run it on a single problem
```bash
./run_single_problem.sh /absolute/path/to/problem_dir "anthropic/claude-3.5-sonnet" "<OPENROUTER_API_KEY>"
```

### What the script does
1. Builds the image from repo root with arguments for model/API key and optional problem source (URL or local path)
2. Stages local problem files into the build context so the image can COPY them
3. Runs the container with a timeout of `TIME_LIMIT + 1 minute` (unless your OS lacks `timeout`)
4. Extracts the submission log to the host as `submission_log_<timestamp>.json`
5. Cleans up the container

## Problem Sources
- **Local directory**: Pass an absolute or relative path to a folder that contains `problem_statement.html` and optional assets (samples, images). These files are copied into `/workspace/agent/` in the container.
- **URL**: Pass a URL to a .zip archive. The archive is downloaded and extracted into `/workspace/agent/` during the build.

Recommended local structure:
```
problem_dir/
├── problem_statement.html
├── input.txt (optional)
├── output.txt (optional)
└── <attachments>
```

## Inside the Container
- Working directory for the agent: `/workspace/agent`
- MCP server (if configured) listens on `http://127.0.0.1:8001`
- You’ll drop into an interactive bash session after initialization
- OpenCode config: `/workspace/opencode_config.json` (synced at startup/build to `/root/.config/opencode/opencode.json`; the `MODEL` env can override the model in this config)

### MCP Tools available to the agent
- `submit_solution(file_path)`: Submits a C++ solution to the online judge
- `get_remaining_time_and_submissions()`: Returns remaining submissions and remaining time in seconds

## Logs
The MCP server records submission results at `/tmp/submission_log.json` (inside the container). The run script automatically copies it to the host as `submission_log_<timestamp>.json` after the container exits or times out.

### Log schema
The log is a JSON object with three top-level arrays:

- `events`: chronological list of lifecycle and tool-call events
- `submissions`: one entry per judged submission with detailed metadata
- `results`: simplified time/points view for quick charting

Example:

```json
{
  "events": [
    {
      "timestamp": 1731012345.12,
      "human_timestamp": "2025-07-09 12:34:56",
      "type": "startup",
      "details": { "submission_limit": 50, "time_limit_minutes": 30, "pid": "1912" }
    },
    {
      "timestamp": 1731012350.45,
      "human_timestamp": "2025-07-09 12:35:50",
      "type": "tool_call",
      "tool": "get_remaining_time_and_submissions",
      "output": { "submissions_left": 49, "time_left": 1753.4 }
    },
    {
      "timestamp": 1731012401.02,
      "human_timestamp": "2025-07-09 12:36:41",
      "type": "tool_call",
      "tool": "submit_solution",
      "args": { "file_path": "/workspace/agent/solution.cpp" },
      "context": { "submission_number": 1 }
    }
  ],
  "submissions": [
    {
      "timestamp": 1731012460.88,
      "human_timestamp": "2025-07-09 12:37:40",
      "submission_number": 1,
      "verdict": "Accepted (100/100)",
      "points_earned": 100,
      "points_total": 100,
      "elapsed_time_seconds": 100.3,
      "time_taken": "0.12s",
      "memory": "64MB"
    }
  ],
  "results": [
    { "time": 100.3, "time_human": "2025-07-09 12:37:40", "points": 100 }
  ]
}
```

Notes:
- `events.type` can be `startup`, `tool_call`, or `tool_error`.
- For `tool_call`, `args` includes non-sensitive inputs and `output` includes the return payload when small.
- `tool_error` entries contain an `error` field instead of `output`.
- `results` is derived from `submissions` and is intended for plotting points-over-time.

## Troubleshooting
- `timeout: command not found` on macOS: `brew install coreutils` and either symlink or replace `timeout` with `gtimeout` in `docker/run_single_problem.sh`.
- MCP server didn’t start: Ensure `.env` contains `BASE_URL`, `SUBMISSION_URL`, `RESULTS_URL`, `PHPSESSID`, and `PID`. If absent, MCP is intentionally skipped for local-only runs.
- No problem files found: Verify your local path or URL points to valid content. The local directory must exist when invoking the script.

## Notes
- The environment includes g++ and typical build tools for compiling C++ solutions.
- The system is designed for autonomous benchmarking; human input inside the container is optional.
