import multiprocessing

bind = "0.0.0.0:8989"
workers = multiprocessing.cpu_count()
accesslog = "/tmp/translate.access.log"
wsgi_app  = "translate:app"

# Metrics logging to statsd exporter
statsd_prefix = "machinetranslation"
statsd_host = "localhost:8125"
logconfig = "logging.conf"
