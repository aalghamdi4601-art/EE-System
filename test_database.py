"""
Member 1 Database Test Suite

This file verifies the updated database schema and logic in database.py.
It covers the new relational tables, user authentication support, team registration
logic, and duplicate-prevention checks.

Expected coverage:
- users
- students
- faculty
- courses
- student_courses
- projects
- project_prerequisites
- facilities
- project_facilities
- teams
- team_members
- registrations

Run this script directly to confirm that the Member 1 database layer is ready.
"""

from database import DatabaseManager


def assert_equal(actual, expected, message=None):
    if actual != expected:
        raise AssertionError(message or f"Expected {expected!r}, got {actual!r}")


def assert_true(value, message=None):
    if not value:
        raise AssertionError(message or f"Expected True, got {value!r}")


def assert_false(value, message=None):
    if value:
        raise AssertionError(message or f"Expected False, got {value!r}")


def run_test(name, fn):
    try:
        fn()
        print(f"PASS {name}")
    except Exception as exc:
        print(f"FAIL {name}: {exc}")
        raise


def test_database_initialization():
    # TC-01: Verify that all required tables are created by DatabaseManager.
    db = DatabaseManager(":memory:")
    tables = db.get_table_names()
    required = {
        "users",
        "students",
        "courses",
        "projects",
        "student_courses",
        "project_prerequisites",
        "facilities",
        "project_facilities",
        "faculty",
        "teams",
        "team_members",
        "registrations",
    }
    for table_name in required:
        assert_true(table_name in tables, f"Missing table: {table_name}")
    db.close()


def test_add_user():
    # TC-02: Validate user creation and reject invalid roles.
    db = DatabaseManager(":memory:")
    user_id = db.add_user("alice@test.com", "hashed_pw", "student")
    assert_true(user_id is not None, "Valid user should return an ID")
    user = db.get_user_by_email("alice@test.com")
    assert_true(user is not None, "User should be retrievable")
    assert_equal(user["email"], "alice@test.com")
    invalid_user_id = db.add_user("bad@test.com", "hashed_pw", "unknown_role")
    assert_false(invalid_user_id, "Invalid role should not create a user")
    db.close()


def test_add_student_linked_to_user():
    # TC-03: Create a student and link it to an existing user account.
    db = DatabaseManager(":memory:")
    db.add_user("s001@test.com", "pw", "student")
    db.add_student("S001", "Alice", 3.8, "Computer", user_email="s001@test.com")
    student = db.get_student_by_id("S001")
    assert_true(student is not None, "Student should be created")
    assert_equal(student["name"], "Alice")
    assert_true(student["user_id"] is not None, "Student should be linked to a user")
    db.close()


def test_add_faculty_linked_to_user():
    # TC-04: Create a faculty record and link it to an existing user account.
    db = DatabaseManager(":memory:")
    db.add_user("f001@test.com", "pw", "faculty")
    db.add_faculty("F001", "Dr. Ahmed", "Engineering", "AI", user_email="f001@test.com")
    faculty = db.get_faculty_by_id("F001")
    assert_true(faculty is not None, "Faculty should be created")
    assert_equal(faculty["name"], "Dr. Ahmed")
    assert_true(faculty["user_id"] is not None, "Faculty should be linked to a user")
    db.close()


def test_add_course_and_student_course():
    # TC-05: Add a course and attach it relationally to a student.
    # Duplicate student-course entries should be ignored.
    db = DatabaseManager(":memory:")
    db.add_course("COE301", "Data Structures")
    db.add_student("S001", "Alice", 3.8, "Computer")
    db.add_student_course("S001", "COE301")
    courses = db.get_student_courses("S001")
    assert_true(any(row["course_code"] == "COE301" for row in courses), "Course should be linked to student")
    db.add_student_course("S001", "COE301")
    assert_true(len([row for row in db.get_student_courses("S001") if row["course_code"] == "COE301"]) == 1,
                "Duplicate student course should be ignored")
    db.close()


def test_add_project_without_text_prerequisites():
    # TC-06: Ensure projects do not store prerequisites as a TEXT column.
    db = DatabaseManager(":memory:")
    project_id = db.add_project(
        title="Smart IoT",
        description="IoT project",
        specialization="Computer",
        prerequisites=None,
        max_students=3,
        facilities=None,
        supervisor="F001"
    )
    project = db.get_project_by_id(project_id)
    assert_true(project is not None, "Project should be created")
    assert_false("prerequisites" in project.keys(), "Project row should not contain a text prerequisites column")
    db.close()


def test_add_project_prerequisite_relational():
    # TC-07: Store project prerequisites relationally in project_prerequisites.
    db = DatabaseManager(":memory:")
    project_id = db.add_project(
        title="Smart IoT",
        description="IoT project",
        specialization="Computer",
        prerequisites=None,
        max_students=3,
        facilities=None,
        supervisor="F001"
    )
    db.add_course("COE350", "Embedded Systems")
    db.add_project_prerequisite(project_id, "COE350")
    prereqs = db.get_project_prerequisites(project_id)
    assert_true("COE350" in prereqs, "Project prerequisite should be stored relationally")
    db.close()


def test_add_facility_and_link_to_project():
    # TC-08: Add a facility and link it to a project via project_facilities.
    db = DatabaseManager(":memory:")
    project_id = db.add_project(
        title="Smart IoT",
        description="IoT project",
        specialization="Computer",
        prerequisites=None,
        max_students=3,
        facilities=None,
        supervisor="F001"
    )
    db.add_facility("Embedded Systems Lab", capacity=2)
    db.add_project_facility(project_id, "Embedded Systems Lab")
    facilities = db.get_project_facilities(project_id)
    assert_true("Embedded Systems Lab" in facilities, "Facility should be linked to project")
    db.close()


def test_prevent_duplicate_student_in_same_team():
    # TC-09: Prevent adding the same student to the same team twice.
    db = DatabaseManager(":memory:")
    db.add_student("S001", "Alice", 3.8, "Computer")
    team_id = db.create_team("Alpha Team")
    result, message = db.add_team_member(team_id, "S001")
    assert_true(result, "First add_team_member call should succeed")
    result2, message2 = db.add_team_member(team_id, "S001")
    assert_false(result2, "Duplicate student should not be added to the same team")
    db.close()


def test_register_team_uses_actual_member_count():
    # TC-10: register_team() should count real team members, not add a hardcoded +3.
    db = DatabaseManager(":memory:")
    db.add_student("S001", "Alice", 3.8, "Computer")
    db.add_student("S002", "Bob", 3.4, "Computer")
    db.add_student("S003", "Carol", 3.5, "Computer")
    team_id = db.create_team("Beta Team")
    assert_true(db.add_team_member(team_id, "S001")[0])
    assert_true(db.add_team_member(team_id, "S002")[0])
    assert_true(db.add_team_member(team_id, "S003")[0])
    project_id = db.add_project(
        title="AI Project",
        description="desc",
        specialization="Computer",
        prerequisites="COE301",
        max_students=3,
        facilities="AI Lab",
        supervisor="F001"
    )
    count = db.register_team(team_id, project_id)
    assert_equal(count, 3)
    project = db.get_project_by_id(project_id)
    assert_equal(project["allocated_students"], 3)
    db.close()


def test_prevent_duplicate_registration():
    # TC-11: Prevent the same team from registering to the same project twice.
    db = DatabaseManager(":memory:")
    db.add_student("S001", "Alice", 3.8, "Computer")
    db.add_student("S002", "Bob", 3.4, "Computer")
    team_id = db.create_team("Gamma Team")
    assert_true(db.add_team_member(team_id, "S001")[0])
    assert_true(db.add_team_member(team_id, "S002")[0])
    project_id = db.add_project(
        title="AI Project",
        description="desc",
        specialization="Computer",
        prerequisites="COE301",
        max_students=3,
        facilities="AI Lab",
        supervisor="F001"
    )
    first = db.register_team(team_id, project_id)
    assert_true(first == 2, "First registration should return actual member count")
    second = db.register_team(team_id, project_id)
    assert_false(second, "Duplicate registration should fail")
    db.close()


def main():
    run_test("TC-01 Database Initialization", test_database_initialization)
    run_test("TC-02 Add User", test_add_user)
    run_test("TC-03 Add Student Linked to User", test_add_student_linked_to_user)
    run_test("TC-04 Add Faculty Linked to User", test_add_faculty_linked_to_user)
    run_test("TC-05 Add Course and Student Course", test_add_course_and_student_course)
    run_test("TC-06 Add Project Without TEXT Prerequisites", test_add_project_without_text_prerequisites)
    run_test("TC-07 Add Project Prerequisite Relational", test_add_project_prerequisite_relational)
    run_test("TC-08 Add Facility and Link to Project", test_add_facility_and_link_to_project)
    run_test("TC-09 Prevent Duplicate Student in Same Team", test_prevent_duplicate_student_in_same_team)
    run_test("TC-10 register_team() Uses Actual Member Count", test_register_team_uses_actual_member_count)
    run_test("TC-11 Prevent Duplicate Registration", test_prevent_duplicate_registration)
    print("\nAll tests completed.")


if __name__ == "__main__":
    main()
