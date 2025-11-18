import multiprocessing

# Server socket
bind = "unix:/home/larfef/symp-templates-dev/gunicorn.sock"
# Alternative: bind = '127.0.0.1:8000'

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/home/larfef/symp-templates-dev/logs/gunicorn-access.log"
errorlog = "/home/larfef/symp-templates-dev/logs/gunicorn-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "myproject"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
