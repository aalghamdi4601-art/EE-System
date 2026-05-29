# ==========================================
# Project Controller
# ==========================================

from database import DatabaseManager
from models.project import Project

class ProjectController:
    def __init__(self, db: DatabaseManager = None):
        if db is None:
            self.db = DatabaseManager()
            self._owns_db = True  # We made it, we close it
        else:
            self.db = db
            self._owns_db = False  # Someone else manages this connection

    def close(self):
        """Close the DB connection (only if this controller owns it)."""
        if self._owns_db:
            self.db.close()

    # ----------------------------------------------------------------------
    # Helpers - convert sqlite3.Row to plain dict for easier use in views
    # ----------------------------------------------------------------------
    @staticmethod
    def _row_to_dict(row):
        """sqlite3.Row -> dict (or None if row is None)."""
        return dict(row) if row is not None else None

    # ----------------------------------------------------------------------
    # Project management
    # ----------------------------------------------------------------------
    def add_project(self, title, description, faculty_member):
        if not Project.validate_project_data(title, description, faculty_member):
            return "Error: All fields are required!"
        if self.is_title_duplicate(title):
            return "Error: Project title already exists!"
        try:
            self.db.add_project(title, description, faculty_member)
            return "Project added successfully!"
        except Exception as error:
            return f"Database Error: {str(error)}"

    def update_project(self, project_id, title, description, faculty_member):
        if not Project.validate_project_data(title, description, faculty_member):
            return "Error: All fields are required!"
        current_project = self.get_project_by_id(project_id)
        if not current_project:
            return "Error: Project not found!"
        if current_project.get('title') != title and self.is_title_duplicate(title):
            return "Error: New title already exists!"
        try:
            self.db.delete_project(project_id)
            self.db.add_project(title, description, faculty_member)
            return "Project updated successfully!"
        except Exception as error:
            return f"Update Error: {str(error)}"

    def delete_project(self, project_id):
        try:
            self.db.delete_project(project_id)
            return "Project deleted successfully!"
        except Exception as error:
            return f"Delete Error: {str(error)}"

    def get_all_projects(self):
        projects_list = []
        try:
            raw_data = self.db.get_all_projects()
            for row in raw_data:
                projects_list.append(self._row_to_dict(row))
        except Exception as error:
            print(f"Error: {error}")
        return projects_list

    def get_project_by_id(self, project_id):
        try:
            row = self.db.get_project_by_id(project_id)
            return self._row_to_dict(row)
        except Exception as error:
            print(f"Error: {error}")
        return None

    def is_title_duplicate(self, title):
        all_projects = self.get_all_projects()
        for project in all_projects:
            if project.get('title', '').strip().lower() == title.strip().lower():
                return True
        return False
