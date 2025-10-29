#!/bin/bash
# start the Flask app with gunicorn for production hosting
exec gunicorn app:app --bind 0.0.0.0:$PORT
