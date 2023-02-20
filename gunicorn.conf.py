import multiprocessing

bind = "0.0.0.0:80"
workers = multiprocessing.cpu_count()
accesslog = "/tmp/translate.access.log"
wsgi_app  = "translate:app"