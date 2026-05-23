# Integration Guide

## Purpose

This guide explains how other team members should use the Member 1 database layer in the EE202 Graduation Project Registration System.

Member 1 provides `DatabaseManager`, which should be used as the main interface between the application and the SQLite database.

## Importing DatabaseManager

Use this import in other Python files:

```python
from database import DatabaseManager
```

Create a database manager object:

```python
db = DatabaseManager()
```

Close the connection when finished:

```python
db.close()
```

## Student Examples

Get all students:

```python
students = db.get_all_students()
print(students)
```

Get one student by ID:

```python
student = db.get_student_by_id("2023001")
print(student)
```

Check if a student exists:

```python
if db.check_student_exists("2023001"):
    print("Student exists")
else:
    print("Student not found")
```

## Project Examples

Get open projects:

```python
open_projects = db.get_open_projects()
print(open_projects)
```

Get one project by ID:

```python
project = db.get_project_by_id(1)
print(project)
```

Check if a project has available capacity:

```python
if db.check_project_capacity(1):
    print("Project has capacity")
else:
    print("Project is full or does not exist")
```

## Team Examples

Create a team:

```python
team_id = db.create_team("Team Alpha")
print(team_id)
```

Add a student to a team:

```python
db.add_team_member(team_id, "2023001")
```

Check if a student is already in any team:

```python
if db.check_student_already_in_team("2023001"):
    print("Student is already assigned to a team")
else:
    print("Student can be added to a team")
```

## Registration Examples

Register a team for a project:

```python
db.register_team(team_id, 1)
```

Check if a team is already registered:

```python
if db.check_team_registered(team_id):
    print("Team is already registered")
else:
    print("Team is not registered yet")
```

## Course and Prerequisite Examples

Add or ensure a course exists:

```python
db.add_course("COE310", "Data Structures")
```

Add a complete course record for a student:

```python
db.add_student_course("2023001", "COE310", "A")
```

Get a student's completed courses:

```python
completed = db.get_student_courses("2023001")
print(completed)
```

Link a prerequisite to a project:

```python
db.add_project_prerequisite(project_id, "COE310")
```

Get a project prerequisites list:

```python
prereqs = db.get_project_prerequisites(project_id)
print(prereqs)
```

## Facility Examples

Create or get a facility by name:

```python
facility_id = db.add_facility("AI Lab", capacity=2)
```

Link a facility to a project:

```python
db.add_project_facility(project_id, facility_id)
```

List facilities for a project:

```python
facility_ids = db.get_project_facilities(project_id)
print(facility_ids)
```

## User Authentication Examples

Add a user record for login or role management:

```python
user_id = db.add_user("student@example.com", "hashed_password", "student")
```

Find a user by email:

```python
user = db.get_user_by_email("student@example.com")
print(user)
```

## Notes on `add_student` and `add_project`

The `add_student()` method now supports optional completed courses as a comma-separated string or a list. For example:

```python
db.add_student("2023001", "Ali", 3.5, "Computer", "COE310,COE320")
```

This stores completed courses in the relational `student_courses` table instead of a text field.

The `add_project()` method now saves prerequisites and facilities in relational tables rather than storing them as comma-separated text.

## Important Instructions

- Do not write raw SQL directly inside GUI files.
- Use `DatabaseManager` methods when reading from or writing to the database.
- Keep GUI files focused on screens, buttons, forms, and displaying results.
- Large validation rules should be added later in the Registration Logic part.
- Examples of later validation include checking prerequisites, team size, project capacity, and registration rules.
- If another team member needs a new database operation, add it as a method in `DatabaseManager` instead of duplicating SQL in multiple files.

## Suggested Flow for GUI Integration

1. Import `DatabaseManager`.
2. Create one `DatabaseManager` object when the screen or application starts.
3. Call helper methods to load students, projects, teams, or registrations.
4. Display returned data in the GUI.
5. Call add or register methods when the user submits a form.
6. Close the database connection when the application exits.
