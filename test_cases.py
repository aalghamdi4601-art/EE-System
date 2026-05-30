import os
from database import DatabaseManager
from models import Student, Team, Project, Faculty
from validation import (
    check_team_size, check_specialization, check_prerequisites,
    check_slots, check_supervisor, validate_registration
)

# Delete old test database before each run
if os.path.exists("test.db"):
    os.remove("test.db")

# A function that prints the result of each test
def run_test(test_name, condition):
    if condition:
        print(f"✅ PASS — {test_name}")
    else:
        print(f"❌ FAIL — {test_name}")

# Initialize test database
db = DatabaseManager("test.db")

# Add test users
db.add_user("ali@uni.edu", "pass123", "student")
db.add_user("sara@uni.edu", "pass123", "student")
db.add_user("omar@uni.edu", "pass123", "student")

# Add test students
db.add_student("S001", "Ali", 3.5, "Computer", ["COE301", "COE310"])
db.add_student("S002", "Sara", 3.2, "Computer", ["COE301", "COE310"])
db.add_student("S003", "Omar", 3.7, "Computer", ["COE301", "COE310"])

# Add test project
project_id = db.add_project(
    title="Smart Home",
    description="IoT project",
    specialization="Computer",
    prerequisites=["COE301", "COE310"],
    max_students=3
)

# Create test team
team_id = db.create_team("Alpha Team")
db.add_team_member(team_id, "S001")
db.add_team_member(team_id, "S002")
db.add_team_member(team_id, "S003")

# Build objects for testing
student1 = Student("S001", "Ali", 3.5, "Computer", ["COE301", "COE310"])
student2 = Student("S002", "Sara", 3.2, "Computer", ["COE301", "COE310"])
student3 = Student("S003", "Omar", 3.7, "Computer", ["COE301", "COE310"])

valid_team = Team("Alpha Team", members=[student1, student2, student3], team_id=team_id)

valid_project = Project(
    title="Smart Home",
    description="IoT project",
    specialization="Computer",
    prerequisites=["COE301", "COE310"],
    max_students=3,
    project_id=project_id
)

valid_faculty = Faculty("F001", "Dr. Ahmed", "ECE", max_supervisions=3, current_supervisions=1)

# ── check_team_size ──────────────────────────────────────────
ok, msg = check_team_size(valid_team)
run_test("Team has 3 members", ok)

small_team = Team("Small Team", members=[student1, student2])
ok, msg = check_team_size(small_team)
run_test("Team has less than 3 members", not ok)

# ── check_specialization ─────────────────────────────────────
ok, msg = check_specialization(valid_team, valid_project)
run_test("Specialization matches project", ok)

wrong_student = Student("S004", "Nora", 3.0, "Power", ["COE301"])
wrong_team = Team("Wrong Team", members=[wrong_student, student2, student3])
ok, msg = check_specialization(wrong_team, valid_project)
run_test("Specialization does not match project", not ok)

# ── check_prerequisites ──────────────────────────────────────
ok, msg = check_prerequisites(valid_team, valid_project)
run_test("All members passed prerequisites", ok)

weak_student = Student("S005", "Weak", 3.0, "Computer", ["COE301"])
weak_team = Team("Weak Team", members=[weak_student, student2, student3])
ok, msg = check_prerequisites(weak_team, valid_project)
run_test("Member missing prerequisite", not ok)

# ── check_slots ──────────────────────────────────────────────
ok, msg = check_slots(db, project_id)
run_test("Project has available slots", ok)

# ── check_supervisor ─────────────────────────────────────────
ok, msg = check_supervisor(valid_faculty)
run_test("Supervisor is available", ok)

full_faculty = Faculty("F002", "Dr. Khaled", "ECE", max_supervisions=3, current_supervisions=3)
ok, msg = check_supervisor(full_faculty)
run_test("Supervisor is overloaded", not ok)

# ── validate_registration ────────────────────────────────────
ok, msg = validate_registration(
    valid_team, valid_project, valid_faculty, db, project_id, team_id
)
run_test("Valid registration passes all checks", ok)

db.close()
print("\nAll tests completed.")
