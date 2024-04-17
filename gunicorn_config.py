# gunicorn_config.py

bind = "0.0.0.0:80"
module = "config.wsgi:application"

workers = 4  # Adjust based on your server's resources
worker_connections = 1000
threads = 4

accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
capture_output = False
loglevel = "info"