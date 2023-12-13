import os

bind = "0.0.0.0:8989"
workers = os.getenv("GUNICORN_WORKERS", 1)
accesslog = "/tmp/translate.access.log"
wsgi_app = "translate:app"
worker_class = "uvicorn.workers.UvicornWorker"
logconfig = "logging.conf"

# The maximum number of requests a worker will process before restarting.
# This is a simple method to help limit the damage of memory leaks.if any
max_requests = 1000
# The maximum jitter to add to the max_requests setting.
# This is intended to stagger worker restarts to avoid all workers restarting at the same time.
max_requests_jitter = 50
