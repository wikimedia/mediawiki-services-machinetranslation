import os

bind = "0.0.0.0:8989"
workers = os.getenv("GUNICORN_WORKERS", 1)
accesslog = "/tmp/translate.access.log"
wsgi_app = "translate:app"

# Metrics logging to statsd exporter
statsd_prefix = os.getenv("STATSD_PREFIX", "machinetranslation")
statsd_host = f"{os.getenv('STATSD_HOST', 'localhost')}:{os.getenv('STATSD_PORT', 8125)}"
logconfig = "logging.conf"

# The maximum number of requests a worker will process before restarting.
# This is a simple method to help limit the damage of memory leaks.if any
max_requests = 1000
# The maximum jitter to add to the max_requests setting.
# This is intended to stagger worker restarts to avoid all workers restarting at the same time.
max_requests_jitter = 50
