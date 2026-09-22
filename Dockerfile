FROM node:18-bullseye-slim AS node
FROM python:3.10-slim

COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    fonts-dejavu-core \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app/

RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt

CMD ["python3", "app.py"]
