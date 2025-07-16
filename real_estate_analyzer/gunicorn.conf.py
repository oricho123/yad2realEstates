"""Gunicorn configuration file for Real Estate Analyzer.

This file provides production-ready Gunicorn settings.
You can override any setting via environment variables.

Usage:
    gunicorn -c gunicorn.conf.py wsgi:application
"""

import os
import multiprocessing

# Server socket
bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = os.getenv('WORKER_CLASS', 'gevent')
worker_connections = int(os.getenv('WORKER_CONNECTIONS', '1000'))
max_requests = int(os.getenv('MAX_REQUESTS', '1000'))
max_requests_jitter = int(os.getenv('MAX_REQUESTS_JITTER', '50'))
timeout = int(os.getenv('TIMEOUT', '120'))
keepalive = int(os.getenv('KEEPALIVE', '2'))

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = os.getenv('ACCESS_LOG', '-')  # '-' means stdout
errorlog = os.getenv('ERROR_LOG', '-')    # '-' means stderr
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'real_estate_analyzer'

# Server mechanics
daemon = False
pidfile = os.getenv('PID_FILE', '/tmp/gunicorn.pid')
user = os.getenv('USER', None)
group = os.getenv('GROUP', None)
tmp_upload_dir = None

# SSL (uncomment for HTTPS)
# keyfile = os.getenv('SSL_KEYFILE', None)
# certfile = os.getenv('SSL_CERTFILE', None)

# Performance tuning
preload_app = True
reuse_port = True

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
