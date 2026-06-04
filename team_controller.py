# controllers/team_controller.py
# Member 3 - Team Formation
#
# This controller handles team-creation logic and student dashboard data
# for my part of the project (Member 3).
#
# It uses Member 1's DatabaseManager (from database.py) instead of writing
# raw SQL — this follows the rule from INTEGRATION_GUIDE.md:
#   "Do not write raw SQL directly inside GUI files."

from database import DatabaseManager


class TeamController:
    """
    Acts as the bridge between the student-facing views and the database.

    All methods return either:
        (True, data_or_message)   on success
        (False, error_message)    on failure
    or plain values (dicts/lists) for read-only queries.
    """

    def __init__(self, db: DatabaseManager = None):
        if db is None:
            self.db = DatabaseManager()
            self._owns_db = True
        else:
            self.db = db
            self._owns_db = False

    def close(self):
        """Close the DB connection (only if this controller owns it)."""
        if self._owns_db:
            self.db.close()

    @staticmethod
    def _row_to_dict(row):
        """sqlite3.Row -> dict (or None if row is None)."""
        return dict(row) if row is not None else None

    # ------------------------------------------------------------------
    # Student lookup
    # ------------------------------------------------------------------

    def get_student_by_id(self, student_id: str):
        """Returns a dict of student info, or None if not found."""
        row = self.db.get_student_by_id(student_id.strip())
        return self._row_to_dict(row)

    def validate_student_id(self, student_id: str):
        """Checks that the student ID exists in the system."""
        student_id = student_id.strip()
        if not student_id:
            return False, "Student ID cannot be empty."
        if not self.db.check_student_exists(student_id):
            return False, f"Student ID '{student_id}' was not found in the system."
        return True, "OK"

    def get_student_courses(self, student_id: str):
        """Returns the list of completed course codes for a student."""
        rows = self.db.get_student_courses(student_id.strip())
        return [row["course_code"] for row in rows]

    # ------------------------------------------------------------------
    # Team-membership checks
    # ------------------------------------------------------------------

    def is_student_in_a_team(self, student_id: str) -> bool:
        """Wrapper around db.check_student_already_in_team()."""
        return self.db.check_student_already_in_team(student_id.strip())

    def get_team_of_student(self, student_id: str):
        """Returns the team that the given student belongs to, or None."""
        student_id = student_id.strip()
        all_member_rows = self.db.get_team_members(None)

        for row in all_member_rows:
            if row["student_id"] == student_id:
                team_row = self.db.get_team_by_id(row["team_id"])
                return self._row_to_dict(team_row)
        return None

    def get_team_members(self, team_id: int):
        """Returns a list of student dicts who belong to team_id."""
        member_rows = self.db.get_team_members(team_id)
        details = []
        for row in member_rows:
            student = self.db.get_student_by_id(row["student_id"])
            if student is not None:
                details.append(dict(student))
        return details

    # ------------------------------------------------------------------
    # Team-name uniqueness
    # ------------------------------------------------------------------

    def is_team_name_taken(self, team_name: str) -> bool:
        """Returns True if a team with this name already exists."""
        target = team_name.strip().lower()
        for team in self.db.get_all_teams():
            if team["team_name"].strip().lower() == target:
                return True
        return False

    # ------------------------------------------------------------------
    # Create team
    # ------------------------------------------------------------------

    def create_team(self, team_name: str, member_ids: list):
        """
        Validates inputs and creates a team with its three members.

        Validations:
          1. Team name not empty.
          2. Team name not already taken.
          3. Exactly 3 student IDs provided.
          4. All 3 IDs are distinct.
          5. Each student ID exists in the database.
          6. No student is already in another team.
          7. All members must be from the same program.
        """
        team_name = team_name.strip()

        # 1 & 2 — team name checks
        if not team_name:
            return False, "Team name cannot be empty."
        if self.is_team_name_taken(team_name):
            return False, f"Team name '{team_name}' is already taken."

        # 3 — exactly three members
        if len(member_ids) != 3:
            return False, "A team must have exactly 3 members."

        member_ids = [sid.strip() for sid in member_ids]

        # 4 — IDs must be unique
        if len(set(member_ids)) != 3:
            return False, "Duplicate student IDs detected."

        # 5 & 6 — validate each student
        for sid in member_ids:
            valid, msg = self.validate_student_id(sid)
            if not valid:
                return False, msg

            if self.is_student_in_a_team(sid):
                existing = self.get_team_of_student(sid)
                team_ref = f"'{existing['team_name']}'" if existing else "another team"
                return False, f"Student {sid} is already a member of {team_ref}."

        # 7 — all members must be from the same program
        programs = set()
        for sid in member_ids:
            student = self.get_student_by_id(sid)
            programs.add(student["program"])

        if len(programs) > 1:
            return False, "All team members must be from the same program."

        # All checks passed — save to database
        try:
            new_team_id = self.db.create_team(team_name)

            for sid in member_ids:
                ok, msg = self.db.add_team_member(new_team_id, sid)
                if not ok:
                    return False, f"Failed to add student {sid}: {msg}"

            return True, f"Team '{team_name}' was created successfully!"

        except Exception as e:
            return False, f"An unexpected error occurred: {e}"

    # ------------------------------------------------------------------
    # Available projects
    # ------------------------------------------------------------------

    def get_available_projects(self, specialization: str = None):
        """Returns a list of open project dicts, filtered by specialization."""
        rows = self.db.get_open_projects()
        result = []

        for row in rows:
            proj = dict(row)

            if specialization and specialization != "All Programs":
                spec = proj.get("specialization", "")
                if spec != specialization and spec != "All":
                    continue

            facilities = self.db.get_project_facilities(proj["project_id"])
            proj["required_facilities"] = ", ".join(facilities) if facilities else ""
            proj["prerequisites"] = self.db.get_project_prerequisites(proj["project_id"])

            result.append(proj)

        return result

    def get_project_prerequisites(self, project_id: int):
        """Returns a list of required course codes for a project."""
        return self.db.get_project_prerequisites(project_id)
