import multiprocessing

bind = "0.0.0.0:80"
workers = multiprocessing.cpu_count()
accesslog = "/tmp/translate.access.log"
wsgi_app  = "translate:app"

# Metrics logging to statsd exporter
statsd_prefix = "machinetranslation"
statsd_host = "statsd.eqiad.wmnet:8125"
logconfig = "logging.conf"

def worker_exit(server, worker):
    from prometheus_client import multiprocess

    multiprocess.mark_process_dead(worker.pid)