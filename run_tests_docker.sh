#!/usr/bin/env bash
set -e

echo "=== Running WSQLite Unit Tests inside Docker ==="

IMAGE_NAME="wsqlite-test-runner"

docker build -t "$IMAGE_NAME" -f - . <<'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir .[dev]
CMD ["pytest", "test/unit/"]
EOF

docker run --rm "$IMAGE_NAME"
echo "=== Docker Tests Completed Successfully ==="
