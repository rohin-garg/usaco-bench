FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_VERSION=22

RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs

# eventaully move to rust install
RUN npm install -g @openai/codex

ARG PID
RUN curl -J -O "http://127.0.0.1:8000/problems/${PID}" # downloads the problem into the current directory

WORKDIR /workspace

RUN codex --help

CMD ["bash"]
