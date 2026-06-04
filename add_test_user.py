# add_test_user.py
from database import DatabaseManager
from auth import hash_password

db = DatabaseManager()
db.add_user("test@uni.edu", hash_password("Password1"), "student")
db.add_student("S001", "Test Student", 3.5, "Computer", ["COE301"], user_email="test@uni.edu")
print("Done!")