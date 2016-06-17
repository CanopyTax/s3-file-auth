#!/usr/bin/env bash

gunicorn run:my_app --bind 0.0.0.0:8080 --worker-class aiohttp.worker.GunicornWebWorker -w 8