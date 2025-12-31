from app.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

def create_admin():
    db = SessionLocal()

    admin_email = "admin@example.com"

    existing = db.query(User).filter(User.email == admin_email).first()
    if existing:
        print("Admin already exists")
        return

    admin = User(
        name="System Admin",
        email=admin_email,
        password_hash=hash_password("admin1234"),
        role="admin"
    )

    db.add(admin)
    db.commit()
    db.close()

    print("Admin user created")

if __name__ == "__main__":
    create_admin()
