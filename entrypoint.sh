#!/bin/sh
python -c 'from app.main import app; from app.models import db; app.app_context().push(); db.create_all()'
exec gunicorn --bind 0.0.0.0:3000 --workers 2 --timeout 60 app.main:app