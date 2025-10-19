"""Gunicorn configuration for production deployment.

This configuration uses Uvicorn workers for async FastAPI support.
Workers are calculated based on CPU cores for optimal performance.
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000  # Restart workers after 1000 requests (prevents memory leaks)
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once
timeout = 60  # Workers silent for more than this are killed
graceful_timeout = 30  # Time to wait for workers to finish serving requests on reload
keepalive = 5  # Time to wait for requests on a Keep-Alive connection

# Process naming
proc_name = "urlshortener-api"

# Server mechanics
daemon = False  # Run in foreground (Docker handles daemonization)
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
loglevel = os.getenv("LOG_LEVEL", "info")
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'

# Preload application
preload_app = True  # Load application code before worker processes are forked

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting Gunicorn server...")


def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading Gunicorn server...")


def when_ready(server):
    """Called just after the server is started."""
    server.log.info(f"Gunicorn server is ready. Workers: {workers}, Worker class: {worker_class}")


def worker_int(worker):
    """Called just after a worker has been killed by a SIGINT or SIGQUIT signal."""
    worker.log.info(f"Worker {worker.pid} was interrupted")


def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info(f"Worker {worker.pid} received SIGABRT signal")


def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")


def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info(f"Worker {worker.pid} initialized")


def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info(f"Worker {worker.pid} exited")


def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed."""
    server.log.info(f"Number of workers changed from {old_value} to {new_value}")


def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("Shutting down Gunicorn server...")


# SSL (if using Gunicorn for SSL termination - prefer Nginx)
# keyfile = None
# certfile = None
# ssl_version = ssl.PROTOCOL_TLS
# cert_reqs = ssl.CERT_NONE
# ca_certs = None
# suppress_ragged_eofs = True
# do_handshake_on_connect = False
# ciphers = None

# Environment variables
raw_env = [
    f"ENVIRONMENT={os.getenv('ENVIRONMENT', 'production')}",
]
