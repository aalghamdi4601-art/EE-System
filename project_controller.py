# ==========================================
# Project Controller
# ==========================================
from database import DatabaseManager
from models.project import Project


class ProjectController:
    def __init__(self, db: DatabaseManager = None):
        if db is None:
            self.db = DatabaseManager()
            self._owns_db = True
        else:
            self.db = db
            self._owns_db = False

    def close(self):
        """Close the DB connection only if this controller owns it."""
        if self._owns_db:
            self.db.close()

    @staticmethod
    def _row_to_dict(row):
        """sqlite3.Row -> dict (or None if row is None)."""
        return dict(row) if row is not None else None

    # ------------------------------------------------------------------
    # Project management
    # ------------------------------------------------------------------

    def add_project(self, title, description, faculty_member,
                    specialization="", prerequisites=None,
                    max_students=3, facilities=None):
        """Add a new project after validating inputs."""
        if not Project.validate_project_data(title, description, faculty_member):
            return False, "Error: All fields are required."

        if self.is_title_duplicate(title):
            return False, "Error: Project title already exists."

        try:
            self.db.add_project(
                title=title,
                description=description,
                specialization=specialization,
                prerequisites=prerequisites or [],
                max_students=max_students,
                facilities=facilities or [],
                supervisor=faculty_member,
            )
            return True, "Project added successfully."
        except Exception as e:
            return False, f"Database Error: {e}"

    def update_project(self, project_id, title, description, faculty_member,
                       specialization="", prerequisites=None,
                       max_students=3, facilities=None):
        """Update an existing project without deleting it."""
        if not Project.validate_project_data(title, description, faculty_member):
            return False, "Error: All fields are required."

        current = self.get_project_by_id(project_id)
        if not current:
            return False, "Error: Project not found."

        # Check duplicate title only if title changed
        if current.get("title") != title and self.is_title_duplicate(title):
            return False, "Error: New title already exists."

        try:
            # Delete old prerequisites and facilities then re-add
            self.db.execute(
                "UPDATE projects SET title=?, description=?, specialization=?,"
                " max_students=?, supervisor=? WHERE project_id=?",
                (title, description, specialization,
                 max_students, faculty_member, project_id)
            )
            # Re-add prerequisites
            self.db.execute(
                "DELETE FROM project_prerequisites WHERE project_id=?",
                (project_id,)
            )
            for course in (prerequisites or []):
                self.db.add_project_prerequisite(project_id, course)

            # Re-add facilities
            self.db.execute(
                "DELETE FROM project_facilities WHERE project_id=?",
                (project_id,)
            )
            for facility in (facilities or []):
                self.db.add_project_facility(project_id, facility)

            return True, "Project updated successfully."
        except Exception as e:
            return False, f"Update Error: {e}"

    def delete_project(self, project_id):
        """Delete a project by ID."""
        try:
            self.db.delete_project(project_id)
            return True, "Project deleted successfully."
        except Exception as e:
            return False, f"Delete Error: {e}"

    def get_all_projects(self):
        """Return all projects as a list of dicts."""
        try:
            return [self._row_to_dict(r) for r in self.db.get_all_projects()]
        except Exception as e:
            print(f"Error: {e}")
            return []

    def get_project_by_id(self, project_id):
        """Return one project dict by ID, or None."""
        try:
            return self._row_to_dict(self.db.get_project_by_id(project_id))
        except Exception as e:
            print(f"Error: {e}")
            return None

    def is_title_duplicate(self, title):
        """Return True if a project with this title already exists."""
        for project in self.get_all_projects():
            if project.get("title", "").strip().lower() == title.strip().lower():
                return True
        return False
