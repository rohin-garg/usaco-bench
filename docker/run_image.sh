#!/bin/bash
if [ -f .env ]; then
  source .env
fi

PID = $1

# important to run the server so that the problem data can get donwnloaded
python ../usaco-camp-parser/server/server_cache.py.py --cookie NULL
docker build -t --build-arg PID=$PID usaco-bench-env .
docker run -it --env-file .env usaco-bench-env 
