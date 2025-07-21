#!/bin/bash
if [ -f .env ]; then
  source .env
fi

# usage bash run_image.sh 1355
PID = $1

# TODO: figure out how to do the github submodule stuff so this command acutally works, cookie not needed because not submitting anything
python server_cache.py --cookie NULL


docker build -t --build-arg PID=$PID usaco-bench-env .
docker run -it --env-file .env usaco-bench-env 
