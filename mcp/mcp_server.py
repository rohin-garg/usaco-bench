from typing import Any
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse
import os
import time
import requests
from bs4 import BeautifulSoup

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

    print('recieved response', response.url, response.status_code)
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

            return {
                "status": "judged",
                "verdict": verdict,
                "date": date,
                "language": lang,
                "time": time_taken,
                "memory": memory
            }

        time.sleep(10)

    raise Exception("Submission timed out after 10 minutes.")

@mcp.custom_route("/startup", methods=["POST"])
async def startup(request: Request) -> PlainTextResponse:
    global submissions_left, start_time
    submissions_left = SUBMISSION_LIMIT
    start_time = time.time()
    return PlainTextResponse("OK")


@mcp.tool()
async def get_remaining_time_and_submissions() -> dict[str, int]:
    """Returns the remaining time (in minutes) and number of submissions for the problem"""
    return {
        "submissions_left": submissions_left,
        "time_left": TIME_LIMIT - (time.time() - start_time)
    }

@mcp.tool()
async def submit_solution(file_path: str) -> dict[str, Any]:
    """Submits c++ source code to the system, returns ...

    Args:
        file_path: the full path to the file that's being submitted
    """
    global submissions_left, start_time
    if submissions_left <= 0:
        raise Exception("No submissions left")
    if TIME_LIMIT - (time.time() - start_time) <= 0:
        raise Exception("No time left")
    submissions_left -= 1
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    return await submit_problem(file_bytes)

if __name__ == "__main__":
    mcp.run(
        transport='http',
        port=8001,
    )
