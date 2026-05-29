# ==========================================
# Project Model
# ==========================================

class Project:
    def __init__(self, project_id, title, description, faculty_member):
        self.project_id = project_id
        self.title = title
        self.description = description
        self.faculty_member = faculty_member

    # Validate that fields are not empty
    @staticmethod
    def validate_project_data(title, description, faculty_member):
        if not title.strip() or not description.strip() or not faculty_member.strip():
            return False
        return True
