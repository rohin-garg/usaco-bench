from typing import Any
from fastmcp import FastMCP, Client
from starlette.requests import Request
from starlette.responses import PlainTextResponse
import os
import time
import requests
from bs4 import BeautifulSoup
import json
import re
import asyncio

mcp = FastMCP("usaco-server")

# Constants
USACO_SERVER_BASE = os.getenv('BASE_URL', None)
USACO_SERVER_SUBMISSION = os.getenv('SUBMISSION_URL', None)
USACO_SERVER_RESULTS = os.getenv('RESULTS_URL', None)
COOKIE_SESS_ID = os.getenv('PHPSESSID', None)
SUBMISSION_LIMIT = int(os.getenv('SUBMISSION_LIMIT', 50))
TIME_LIMIT = int(os.getenv('TIME_LIMIT', 30))
pid = os.getenv('PID', None)
assert USACO_SERVER_BASE is not None, "BASE_URL must be specified"
assert USACO_SERVER_SUBMISSION is not None, "SUBMISSION_URL must be specified"
assert USACO_SERVER_RESULTS is not None, "RESULTS_URL must be specified"
assert COOKIE_SESS_ID is not None, "PHPSESSID must be specified"
assert pid is not None, "PID must be specified"

cookies = {
    'PHPSESSID' : COOKIE_SESS_ID
}

submissions_left = SUBMISSION_LIMIT
start_time = -1

# Logging setup
LOG_FILE = "/tmp/submission_log.json"

def _read_log_file() -> dict:
    """Read the log JSON, ensuring required keys exist."""
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as file_handle:
                data = json.load(file_handle)
        except Exception:
            # If the file is corrupted, start fresh
            data = {}
    else:
        data = {}

    if "events" not in data:
        data["events"] = []
    if "submissions" not in data:
        data["submissions"] = []
    if "results" not in data:
        data["results"] = []
    return data

def _write_log_file(data: dict) -> None:
    with open(LOG_FILE, 'w') as file_handle:
        json.dump(data, file_handle, indent=2)

def ensure_log_initialized() -> None:
    """Create the log file with the expected structure if it doesn't exist."""
    data = _read_log_file()
    _write_log_file(data)

def log_event(event: dict) -> None:
    """Append an event to the log under the 'events' list."""
    try:
        data = _read_log_file()
        data["events"].append(event)
        _write_log_file(data)
    except Exception as e:
        print(f"Failed to log event: {e}")

def log_submission(submission_data: dict) -> None:
    """Log a judged submission and update the simple results view."""
    try:
        data = _read_log_file()
        data["submissions"].append(submission_data)
        # Maintain a simplified results list of {time, points}
        data["results"].append({
            "time": submission_data.get("elapsed_time_seconds"),
            "time_human": submission_data.get("human_timestamp"),
            "points": submission_data.get("points_earned"),
        })
        _write_log_file(data)
    except Exception as e:
        print(f"Failed to log submission: {e}")

def extract_points_from_verdict(verdict):
    """Extract points from verdict string"""
    # Look for patterns like "100/100", "50/100", etc.
    match = re.search(r'(\d+)/(\d+)', verdict)
    if match:
        return int(match.group(1)), int(match.group(2))
    
    # Look for patterns like "Accepted", "Wrong Answer", etc.
    if 'accepted' in verdict.lower() or '100/' in verdict:
        return 100, 100  # Assume full points for accepted
    
    return 0, 100  # Default to 0 points

# solution code should be a string of bytes
async def submit_problem(solution_code: str):
    submit_url = f'{USACO_SERVER_SUBMISSION}?pid={pid}'
    files = {
        'solution': ('solution.cpp', solution_code, 'text/x-c++src'),
    }
    data = {
        'language': 'C++17',
        'file_io': 'std',
    }
    headers = {
        'Origin': USACO_SERVER_BASE,
        'Referer': submit_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    try:
        # This part still needs to talk to the internet
        response = requests.post(submit_url, files=files, data=data, cookies=cookies, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to submit solution: {e}")

    print('received response', response.url, response.status_code)
    time.sleep(10)

    subs_url = f'{USACO_SERVER_RESULTS}?pid={pid}'

    for _ in range(60):
        try:
            response = requests.get(subs_url, cookies=cookies)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch {subs_url}: {e}")

        sub_table = soup.find('table', class_='subtable')
        if not sub_table:
            time.sleep(10)
            continue

        rows = sub_table.find_all('tr')
        if len(rows) < 2:
            time.sleep(10)
            continue

        latest_sub_row = rows[1]
        cells = latest_sub_row.find_all('td')
        if len(cells) < 5:
            time.sleep(10)
            continue

        verdict = cells[2].get_text().strip()

        if 'judged' in verdict or 'error' in verdict.lower() or 'failed' in verdict.lower() or '100/' in verdict:
            date = cells[0].get_text().strip()
            lang = cells[1].get_text().strip()
            time_taken = cells[3].get_text().strip()
            memory = cells[4].get_text().strip()

            # Extract points from verdict
            points_earned, points_total = extract_points_from_verdict(verdict)

            result = {
                "status": "judged",
                "verdict": verdict,
                "date": date,
                "language": lang,
                "time": time_taken,
                "memory": memory,
                "points_earned": points_earned,
                "points_total": points_total
            }

            # Log this submission
            log_entry = {
                "timestamp": time.time(),
                "human_timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "submission_number": SUBMISSION_LIMIT - submissions_left + 1,
                "verdict": verdict,
                "points_earned": points_earned,
                "points_total": points_total,
                "elapsed_time_seconds": time.time() - start_time,
                "time_taken": time_taken,
                "memory": memory
            }
            log_submission(log_entry)

            return result

        time.sleep(10)

    raise Exception("Submission timed out after 10 minutes.")

@mcp.custom_route("/startup", methods=["POST"])
async def startup(request: Request) -> PlainTextResponse:
    global submissions_left, start_time
    submissions_left = SUBMISSION_LIMIT
    start_time = time.time()
    # Ensure log file exists and record startup event
    ensure_log_initialized()
    log_event({
        "timestamp": time.time(),
        "human_timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "type": "startup",
        "details": {
            "submission_limit": SUBMISSION_LIMIT,
            "time_limit_minutes": TIME_LIMIT,
            "pid": pid,
        }
    })
    return PlainTextResponse("OK")

@mcp.tool()
async def get_remaining_time_and_submissions() -> dict[str, int]:
    """Returns the remaining time (in seconds) and number of submissions for the problem"""
    result = {
        "submissions_left": submissions_left,
        "time_left": round((TIME_LIMIT * 60) - (time.time() - start_time))
    }
    # Log tool invocation
    log_event({
        "timestamp": time.time(),
        "human_timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "type": "tool_call",
        "tool": "get_remaining_time_and_submissions",
        "output": result,
    })
    return result

@mcp.tool()
async def submit_solution(file_path: str) -> dict[str, Any]:
    """Submit a C++17 source file to the configured judge and return the final verdict.

    Args:
        file_path: Absolute path to the local C++ source file to submit.

    Returns:
        A dict containing:
        - status: "judged"
        - verdict: e.g., "100/100", "Accepted", "Wrong Answer", etc.
        - date: timestamp string reported by the judge
        - language: language reported by the judge
        - time: runtime reported by the judge
        - memory: memory usage reported by the judge
        - points_earned: integer points parsed from the verdict (best-effort)
        - points_total: integer total points parsed from the verdict (best-effort)

    """
    global submissions_left, start_time
    if submissions_left <= 0:
        log_event({
            "timestamp": time.time(),
            "human_timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "type": "tool_error",
            "tool": "submit_solution",
            "error": "No submissions left"
        })
        raise Exception("No submissions left")
    if (TIME_LIMIT * 60) - (time.time() - start_time) <= 0:
        log_event({
            "timestamp": time.time(),
            "human_timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "type": "tool_error",
            "tool": "submit_solution",
            "error": "No time left"
        })
        raise Exception("No time left")
    submissions_left -= 1
    # Log tool invocation (do not log file contents)
    log_event({
        "timestamp": time.time(),
        "human_timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "type": "tool_call",
        "tool": "submit_solution",
        "args": {"file_path": file_path},
        "context": {
            "submission_number": SUBMISSION_LIMIT - submissions_left,
        }
    })
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    return await submit_problem(file_bytes)

if __name__ == "__main__":
    mcp.run(
        transport='sse',
        port=8001,
    )