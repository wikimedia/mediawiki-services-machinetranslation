import multiprocessing
import os

bind = "0.0.0.0:8989"
workers = multiprocessing.cpu_count()
accesslog = "/tmp/translate.access.log"
wsgi_app  = "translate:app"

# Metrics logging to statsd exporter
statsd_prefix = os.getenv('STATSD_PREFIX', "machinetranslation")
statsd_host = f"{os.getenv('STATSD_HOST', 'localhost')}:{os.getenv('STATSD_PORT', 8125)}"
logconfig = "logging.conf"
