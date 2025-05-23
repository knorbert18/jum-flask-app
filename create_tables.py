from app import app, db  # or your app module path

with app.app_context():
    db.create_all()
    print("Tables created!")
