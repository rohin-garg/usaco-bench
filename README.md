#### Installation instructions after cloning repo
```
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```


#### Docker Commands in docker/ dir
```
docker build -t --e OPENAI_API_KEY="your-api-key-here" usaco-bench-env .
docker run -it usaco-bench-env
```

#### TODO:
- set up MCP server/client correctly
- add auth to the parser server w/ API key, add that to the instantiation scripts
    - update MCP server to handle auth correctly, query the right public URL (deploy server?)
- figure out how to properly set up openai codex cli with MCP servers/prompt it through the docker 
