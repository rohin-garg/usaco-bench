### USACO Benchmarking Framework

This framework provides a sandboxed environment for testing AI coding agents against USACO problems.

#### Installation and Setup

1.  **Prerequisites:**
    *   Docker must be installed and running.

2.  **Configuration:**
    *   Create a `.env` file in the `docker/` directory with the following environment variables:

        ```
        USACO_SERVER_SUBMISSION='<USACO_SERVER_SUBMISSION_URL>'
        USACO_SERVER_BASE='<USACO_SERVER_BASE_URL>'
        USACO_SERVER_RESULTS='<USACO_SERVER_RESULTS_URL>'
        COOKIE_SESS_ID='<YOUR_COOKIE_SESSION_ID>'
        SUBMISSION_LIMIT=<SUBMISSION_LIMIT>
        TIME_LIMIT=<TIME_LIMIT>
        MODEL_PROVIDER_API_KEY='<YOUR_MODEL_PROVIDER_API_KEY>'
        MODEL='<YOUR_MODEL_NAME>'
        PID=<PROBLEM_ID>
        ```

#### Running a Job

1.  **Navigate to the `docker` directory:**

    ```bash
    cd docker
    ```

2.  **Run the execution script:**

    ```bash
    ./run_image.sh
    ```

    This script will:
    *   Build the server and agent Docker images.
    *   Start the server container in the background.
    *   Start the agent container and provide you with an interactive `bash` shell.

    Inside the agent container, the `opencode` agent will be initialized, and the problem specified by the `PID` in your `.env` file will be downloaded and ready for you to work on.
