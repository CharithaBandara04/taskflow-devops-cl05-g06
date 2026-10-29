#!/bin/sh
set -eu

attempt=1
max_attempts=20

echo "Initializing TaskFlow database..."

until flask --app run init-db; do
    if [ "$attempt" -ge "$max_attempts" ]; then
        echo "Database initialization failed." >&2
        exit 1
    fi

    echo "Database not ready. Retrying in 3 seconds..."
    attempt=$((attempt + 1))
    sleep 3
done

echo "Database initialized. Starting TaskFlow..."
exec "$@"