#### Installation instructions after cloning repo
```
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

#### Run a job
Create a `.env` file in the `docker/` directory with the necessary environment variables:
```
USACO_SERVER_SUBMISSION = '<USACO_SERVER_SUBMISSION_URL>'
USACO_SERVER_BASE = '<USACO_SERVER_BASE_URL>'
USACO_SERVER_RESULTS = '<USACO_SERVER_RESULTS_URL>'
COOKIE_SESS_ID = '<YOUR_COOKIE_SESSION_ID>'
SUBMISSION_LIMIT = <SUBMISSION_LIMIT>
TIME_LIMIT = <TIME_LIMIT>
MODEL_PROVIDER_API_KEY = '<YOUR_MODEL_PROVIDER_API_KEY>'
```

Run the bash script to build and run the image.
```
bash run_image.sh 1355 # PID of the image
```