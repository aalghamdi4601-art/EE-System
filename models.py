class Student:
    """Represents a student who can join a graduation project team."""

    def __init__(self, student_id, name, gpa, program, completed_courses=None):
        self.student_id = student_id
        self.name = name
        self.gpa = gpa
        self.program = program
        self.completed_courses = completed_courses or []

    def __repr__(self):
        return (
            f"Student(student_id={self.student_id!r}, name={self.name!r}, "
            f"gpa={self.gpa!r}, program={self.program!r})"
        )


class Team:
    """Represents a student team applying for a graduation project."""

    def __init__(self, team_name, members=None, team_id=None):
        self.team_id = team_id
        self.team_name = team_name
        self.members = members or []

    def __repr__(self):
        return (
            f"Team(team_id={self.team_id!r}, team_name={self.team_name!r}, "
            f"members={self.members!r})"
        )


class Faculty:
    """Represents a faculty member who can supervise projects."""

    def __init__(self, faculty_id, name, department, specialization=None,max_supervisions=3,current_supervisions=0):
        self.faculty_id = faculty_id
        self.name = name
        self.department = department
        self.specialization = specialization
        self.max_supervisions = max_supervisions
        self.current_supervisions = current_supervisions

    def __repr__(self):
        return (
            f"Faculty(faculty_id={self.faculty_id!r}, name={self.name!r}, "
            f"department={self.department!r})"
        )


class Facility:
    """Represents a facility or lab needed by a graduation project."""

    def __init__(self, facility_id, name, location=None, availability=True):
        self.facility_id = facility_id
        self.name = name
        self.location = location
        self.availability = availability

    def __repr__(self):
        return (
            f"Facility(facility_id={self.facility_id!r}, name={self.name!r}, "
            f"availability={self.availability!r})"
        )
