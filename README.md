# Programming Problem Benchmarking Framework

This framework provides a sandboxed Docker environment for testing AI coding agents (specifically OpenCode) against competitive programming problems. The system can work with any programming problem source - either local problem files or online judge systems.

## System Architecture

The framework consists of:
- **MCP Server**: Provides submission tools to the AI agent via Model Context Protocol
- **OpenCode Agent**: AI agent that solves programming problems
- **Docker Environment**: Sandboxed execution environment
- **Problem Source**: Local directory or online judge system (configurable)

## Installation and Setup

### Prerequisites
- Docker must be installed and running
- Internet connection (if using online judge submissions)

### Configuration

Create a `.env` file in the `docker/` directory with the following environment variables:

```bash
# MCP Server Configuration (for online judge integration)
BASE_URL='<YOUR_JUDGE_BASE_URL>'
SUBMISSION_URL='<YOUR_JUDGE_SUBMISSION_URL>'
RESULTS_URL='<YOUR_JUDGE_RESULTS_URL>'
PHPSESSID='<YOUR_SESSION_ID>'

# Submission Limits
SUBMISSION_LIMIT=50
TIME_LIMIT=30

# AI Model Configuration
MODEL_PROVIDER_API_KEY='<YOUR_OPENROUTER_API_KEY>'
MODEL='<MODEL_NAME>'  # e.g., 'anthropic/claude-3.5-sonnet'

# Problem Selection (for online judge)
PID=<PROBLEM_ID>
```

**Note**: Online judge configuration is optional. You can run the framework with local problem files without these settings.

## Running the System

### Basic Usage

1. Navigate to the docker directory:
   ```bash
   cd docker
   ```

2. **Option A - Local Problem Files**: Run with a local directory containing problem files:
   ```bash
   ./run_single_problem.sh /path/to/problem/files MODEL_NAME API_KEY
   ```

3. **Option B - Online Judge**: Run with online judge integration (requires .env configuration):
   ```bash
   ./run_single_problem.sh
   ```

### What Happens When You Run:

1. **Docker Build**: Creates container with OpenCode agent and MCP server
2. **MCP Server Startup**: Background server provides submission tools to agent
3. **Agent Initialization**: OpenCode agent starts with access to MCP tools
4. **Interactive Session**: You get a bash shell inside the container
5. **Problem Access**: Agent can read problem statements and submit solutions

### Available MCP Tools

Inside the agent environment, OpenCode has access to:
- `submit_solution(file_path)`: Submit C++ solution to online judge (if configured)
- `get_remaining_time_and_submissions()`: Check remaining resources

## Problem File Structure

For local problem files, organize them as:
```
problem_files/
├── problem_statement.html
├── input.txt (optional)
├── output.txt (optional)
└── [other attachments...]
```

## Development Notes

- The framework is designed for research and benchmarking purposes
- Resource limits (time/submissions) are enforced when using online judge integration
- The system supports any competitive programming problem format
- Web scraping integration is optional and configurable
