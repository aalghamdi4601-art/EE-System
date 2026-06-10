# add_test_user.py
from database import DatabaseManager
from auth import hash_password

db = DatabaseManager()

# Faculty
db.add_user("faculty@uni.edu", hash_password("Password1"), "faculty")
db.add_faculty("F001", "Dr. Khalid Al-Rashidi", "ECE", user_email="faculty@uni.edu")

# Computer Engineering
db.add_user("s001@uni.edu", hash_password("Password1"), "student")
db.add_student("S001", "Nasser Al-Otaibi", 4.2, "Computer",
    ["EE301", "EE360", "EE250", "EE300"],
    user_email="s001@uni.edu")

db.add_user("s002@uni.edu", hash_password("Password1"), "student")
db.add_student("S002", "Badr Al-Qahtani", 3.8, "Computer",
    ["EE301", "EE300", "EE367", "EE250"],
    user_email="s002@uni.edu")

db.add_user("s003@uni.edu", hash_password("Password1"), "student")
db.add_student("S003", "Rayan Al-Zahrani", 3.9, "Computer",
    ["EE301", "EE360", "EE250", "EE321"],
    user_email="s003@uni.edu")

# Communications
db.add_user("s004@uni.edu", hash_password("Password1"), "student")
db.add_student("S004", "Faisal Al-Harbi", 3.8, "Communications",
    ["EE301", "EE321", "EE421", "EE250"],
    user_email="s004@uni.edu")

# Power
db.add_user("s005@uni.edu", hash_password("Password1"), "student")
db.add_student("S005", "Tariq Al-Shehri", 4.1, "Power",
    ["EE301", "EE351", "EE451", "EE250"],
    user_email="s005@uni.edu")

# Biomedical
db.add_user("s006@uni.edu", hash_password("Password1"), "student")
db.add_student("S006", "Hamad Al-Dosari", 3.4, "Biomedical",
    ["EE301", "EE370", "EE471", "EE250"],
    user_email="s006@uni.edu")

# Projects
p1 = db.add_project(
    title="Smart Home Automation",
    description="Design a smart home system using IoT and embedded controllers",
    specialization="Computer",
    prerequisites=["EE301", "EE250"],
    max_students=3,
    facilities=["Computer Lab"],
    supervisor="F001"
)

p2 = db.add_project(
    title="5G Network Simulation",
    description="Simulate and analyze 5G network performance",
    specialization="Communications",
    prerequisites=["EE301", "EE321"],
    max_students=3,
    facilities=["Communications Lab"],
    supervisor="F001"
)

p3 = db.add_project(
    title="Solar Energy Management",
    description="Design an energy management system for solar power",
    specialization="Power",
    prerequisites=["EE301", "EE351"],
    max_students=3,
    facilities=["Power Lab"],
    supervisor="F001"
)

p4 = db.add_project(
    title="ECG Signal Processing",
    description="Process and analyze ECG signals for heart monitoring",
    specialization="Biomedical",
    prerequisites=["EE301", "EE370"],
    max_students=3,
    facilities=["Biomedical Lab"],
    supervisor="F001"
)

print("Done!")
db.close()
