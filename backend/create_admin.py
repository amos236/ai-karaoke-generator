from database import SessionLocal
from models import User

db = SessionLocal()

# ==============================
# Admin Details
# ==============================

USERNAME = "admin"
EMAIL = "admin@karaoke.com"
PASSWORD = "admin123"

# ==============================
# Check Existing Admin
# ==============================

existing = db.query(User).filter(
    User.username == USERNAME
).first()

if existing:

    print("✅ Admin already exists.")

else:

    admin = User(

        username=USERNAME,

        email=EMAIL,

        password=PASSWORD,

        role="admin",

        subscription_status="active"

    )

    db.add(admin)

    db.commit()

    print("✅ Admin created successfully!")

db.close()