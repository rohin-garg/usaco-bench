FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_VERSION=22

RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs

# use opencode agent
RUN npm i -g opencode-ai@latest

ARG PID
RUN curl -J -O "http://127.0.0.1:8000/problems/${PID}"

WORKDIR /workspace

# eventually move over to just running opencode
CMD ["bash"]
