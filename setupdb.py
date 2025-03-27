from foodtracker import create_app, db
from foodtracker.models import Food, Log  # Import all models

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")
