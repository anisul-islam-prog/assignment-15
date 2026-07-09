from app.main import app
from app.models import db

with app.app_context():
    db.create_all()
    print("✅ Database tables created")

import subprocess
import sys

# Start gunicorn only if DB init succeeded
sys.exit(subprocess.call([
    "gunicorn", "--bind", "0.0.0.0:3000",
    "--workers", "2", "--timeout", "60",
    "app.main:app"
]))