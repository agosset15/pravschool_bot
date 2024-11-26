#!/bin/sh

python alembic upgrade head

exec "$@"