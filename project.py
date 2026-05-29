# ==========================================
# Project Model
# ==========================================
class Project:
    def __init__(self, project_id, title, description, faculty_member,
                 specialization="", prerequisites=None,
                 max_students=3, allocated_students=0,
                 required_facilities="", status="open"):
        self.project_id          = project_id
        self.title               = title
        self.description         = description
        self.faculty_member      = faculty_member
        self.specialization      = specialization
        self.prerequisites       = prerequisites or []
        self.max_students        = max_students
        self.allocated_students  = allocated_students
        self.required_facilities = required_facilities
        self.status              = status

    def is_full(self):
        """Return True if the project has no available slots."""
        return self.allocated_students >= self.max_students

    def check_eligibility(self, team):
        """
        Check if a team is eligible for this project.
        Returns (True, "") or (False, reason).
        """
        if self.is_full():
            return False, "Project is full."

        if self.status != "open":
            return False, "Project is closed."

        for member in team.members:
            if member.program != self.specialization:
                return False, f"Student {member.student_id} program does not match project specialization."

            for course in self.prerequisites:
                if course not in member.completed_courses:
                    return False, f"Student {member.student_id} has not completed {course}."

        return True, ""

    # Validate that fields are not empty
    @staticmethod
    def validate_project_data(title, description, faculty_member):
        if not title.strip() or not description.strip() or not faculty_member.strip():
            return False
        return True
