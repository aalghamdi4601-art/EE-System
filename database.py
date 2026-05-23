import sqlite3


class DatabaseManager:
    """Handles SQLite storage for the graduation project registration system."""

    def __init__(self, db_name="graduation_system.db"):
        """Open a database connection and create the required tables."""
        # Use a Row factory so query results can be accessed by column name.
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create all database tables if they do not already exist."""

        # =========================
        # 1. Users Table
        # =========================
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'faculty', 'admin')),
            created_at TEXT DEFAULT (datetime('now'))
        )
        """)

        # =========================
        # 2. Students Table
        # =========================
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            gpa REAL,
            program TEXT,
            user_id INTEGER REFERENCES users(user_id)
        )
        """)

        # =========================
        # 3. Courses Table
        # =========================
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            course_name TEXT
        )
        """)

        # =========================
        # 4. Projects Table
        # =========================
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            description TEXT,
            specialization TEXT,
            max_students INTEGER,
            allocated_students INTEGER DEFAULT 0,
            supervisor TEXT,
            status TEXT DEFAULT 'open'
        )
        """)

        # =========================
        # 5. Student Courses Table
        # =========================
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_courses (
            student_id TEXT NOT NULL,
            course_code TEXT NOT NULL,
            grade TEXT,
            PRIMARY KEY (student_id, course_code),
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_code) REFERENCES courses(course_id)
        )
        """)

        # =========================
        # 6. Project Prerequisites Table
        # =========================
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_prerequisites (
            project_id INTEGER NOT NULL,
            course_code TEXT NOT NULL,
            PRIMARY KEY (project_id, course_code),
            FOREIGN KEY (project_id) REFERENCES projects(project_id),
            FOREIGN KEY (course_code) REFERENCES courses(course_id)
        )
        """)

        # =========================
        # 7. Facilities Table
        # =========================
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS facilities (
            facility_id INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_name TEXT NOT NULL UNIQUE,
            capacity INTEGER DEFAULT 1,
            booked_slots INTEGER DEFAULT 0
        )
        """)

        # =========================
        # 8. Project Facilities Link Table
        # =========================
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_facilities (
            project_id INTEGER NOT NULL,
            facility_id INTEGER NOT NULL,
            PRIMARY KEY (project_id, facility_id),
            FOREIGN KEY (project_id) REFERENCES projects(project_id),
            FOREIGN KEY (facility_id) REFERENCES facilities(facility_id)
        )
        """)

        # =========================
        # 9. Faculty Table
        # =========================
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            faculty_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            specialization TEXT,
            user_id INTEGER REFERENCES users(user_id)
        )
        """)

        # =========================
        # 10. Teams Table
        # =========================
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL
        )
        """)

        # =========================
        # 11. Team Members Table
        # =========================
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            student_id TEXT NOT NULL,
            UNIQUE (team_id, student_id),
            FOREIGN KEY (team_id) REFERENCES teams(team_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """)

        # =========================
        # 12. Registrations Table
        # =========================
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER,
            project_id INTEGER,
            UNIQUE (team_id, project_id),
            FOREIGN KEY (team_id) REFERENCES teams(team_id),
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        )
        """)

        self.conn.commit()

    # =========================
    # Student Operations
    # =========================
    def add_student(self, s_id, name, gpa, program, courses=None, user_id=None, user_email=None):
        """Add a new student record."""
        # Allow linking the student record to an existing user account.
        if user_email and user_id is None:
            user_row = self.get_user_by_email(user_email)
            user_id = user_row["user_id"] if user_row else None

        self.cursor.execute(
            "INSERT INTO students (student_id, name, gpa, program, user_id) VALUES (?, ?, ?, ?, ?)",
            (s_id, name, gpa, program, user_id)
        )
        # Save completed courses in the relational student_courses table.
        if courses:
            course_codes = [c.strip() for c in courses.split(",")] if isinstance(courses, str) else courses
            for course_code in course_codes:
                if course_code:
                    self.add_course(course_code, None)
                    self.add_student_course(s_id, course_code)
        self.conn.commit()

    def get_all_students(self):
        """Return all students."""
        self.cursor.execute("SELECT * FROM students")
        return self.cursor.fetchall()

    def get_student_by_id(self, student_id):
        """Return one student by ID, or None if the student does not exist."""
        self.cursor.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        )
        return self.cursor.fetchone()

    def check_student_exists(self, student_id):
        """Return True if a student exists."""
        return self.get_student_by_id(student_id) is not None

    def add_course(self, course_id, course_name=None):
        """Add a course record without failing if it already exists."""
        # INSERT OR IGNORE keeps the operation idempotent when the same course is added twice.
        self.cursor.execute(
            "INSERT OR IGNORE INTO courses (course_id, course_name) VALUES (?, ?)",
            (course_id, course_name)
        )
        self.conn.commit()

    def get_all_courses(self):
        """Return all courses."""
        self.cursor.execute("SELECT * FROM courses")
        return self.cursor.fetchall()

    def get_table_names(self):
        """Return all table names in the current database."""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row["name"] for row in self.cursor.fetchall()]

    def add_user(self, email, password, role):
        """Add a new authenticated user record."""
        # Role must be one of the allowed values; invalid roles are rejected by the table CHECK.
        try:
            self.cursor.execute(
                "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
                (email, password, role)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_user_by_email(self, email):
        """Return a user row by email."""
        self.cursor.execute(
            "SELECT * FROM users WHERE email = ?", (email,))
        return self.cursor.fetchone()

    def add_faculty(self, faculty_id, name, department, specialization=None, user_id=None, user_email=None):
        """Add a faculty record linked to a user account."""
        # Support linking a faculty row to an existing user by email or user_id.
        if user_email:
            user_row = self.get_user_by_email(user_email)
            user_id = user_row["user_id"] if user_row else None
        self.cursor.execute(
            "INSERT INTO faculty (faculty_id, name, department, specialization, user_id) VALUES (?, ?, ?, ?, ?)",
            (faculty_id, name, department, specialization, user_id)
        )
        self.conn.commit()
        return faculty_id

    def get_faculty_by_id(self, faculty_id):
        """Return a faculty row by ID."""
        self.cursor.execute(
            "SELECT * FROM faculty WHERE faculty_id = ?", (faculty_id,))
        return self.cursor.fetchone()

    def add_student_course(self, student_id, course_code, grade=None):
        """Record a student's completed course."""
        # Ensure the course exists before creating the student-course link.
        self.add_course(course_code)
        self.cursor.execute(
            "INSERT OR IGNORE INTO student_courses (student_id, course_code, grade) VALUES (?, ?, ?)",
            (student_id, course_code, grade)
        )
        self.conn.commit()

    def get_student_courses(self, student_id):
        """Return all completed courses for a student."""
        self.cursor.execute(
            "SELECT course_code, grade FROM student_courses WHERE student_id = ?", (student_id,)
        )
        return self.cursor.fetchall()

    def add_project_prerequisite(self, project_id, course_code):
        """Link a prerequisite course to a project."""
        # Ensure the referenced course is present in the courses table.
        self.add_course(course_code)
        self.cursor.execute(
            "INSERT OR IGNORE INTO project_prerequisites (project_id, course_code) VALUES (?, ?)",
            (project_id, course_code)
        )
        self.conn.commit()

    def get_project_prerequisites(self, project_id):
        """Return prerequisite course codes for a project."""
        self.cursor.execute(
            "SELECT course_code FROM project_prerequisites WHERE project_id = ?", (project_id,)
        )
        return [row[0] for row in self.cursor.fetchall()]

    def add_facility(self, facility_name, capacity=1):
        """Add a facility record or return the existing facility if already present."""
        # Facilities are unique by name, so repeated inserts are ignored.
        self.cursor.execute(
            "INSERT OR IGNORE INTO facilities (facility_name, capacity) VALUES (?, ?)",
            (facility_name, capacity)
        )
        self.cursor.execute(
            "SELECT facility_id FROM facilities WHERE facility_name = ?", (facility_name,)
        )
        facility_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return facility_id

    def get_all_facilities(self):
        """Return all facilities."""
        self.cursor.execute("SELECT * FROM facilities")
        return self.cursor.fetchall()

    def add_project_facility(self, project_id, facility_reference):
        """Link a facility to a project by facility ID or facility name."""
        # Accept either a facility name or a facility_id.
        if isinstance(facility_reference, str):
            facility_id = self.add_facility(facility_reference)
        else:
            facility_id = facility_reference

        self.cursor.execute(
            "INSERT OR IGNORE INTO project_facilities (project_id, facility_id) VALUES (?, ?)",
            (project_id, facility_id)
        )
        self.conn.commit()

    def get_project_facilities(self, project_id):
        """Return facility names linked to a project."""
        self.cursor.execute(
            "SELECT f.facility_name FROM facilities f "
            "JOIN project_facilities pf ON f.facility_id = pf.facility_id "
            "WHERE pf.project_id = ?", (project_id,)
        )
        return [row["facility_name"] for row in self.cursor.fetchall()]

    def get_all_teams(self):
        """Return all teams."""
        self.cursor.execute("SELECT * FROM teams")
        return self.cursor.fetchall()

    def get_team_members(self, team_id=None):
        """Return all team members, or members for one team when team_id is given."""
        if team_id is None:
            self.cursor.execute("SELECT * FROM team_members")
        else:
            self.cursor.execute(
                "SELECT * FROM team_members WHERE team_id = ?", (team_id,)
            )
        return self.cursor.fetchall()

    def get_all_registrations(self):
        """Return all project registrations."""
        self.cursor.execute("SELECT * FROM registrations")
        return self.cursor.fetchall()

    # =========================
    # Project Operations
    # =========================
    def add_project(
        self,
        title,
        description,
        specialization,
        prerequisites=None,
        max_students=3,
        facilities=None,
        supervisor=None,
    ):
        """
        Add a new graduation project.

        Args:
            title (str): Unique project title.
            description (str): Project description.
            specialization (str): Project specialization or program.
            prerequisites (list[str] | str | None): Required course codes.
                Pass a list like ["COE301", "COE350"] or a comma-separated string.
                Use None if there are no prerequisites.
            max_students (int): Maximum allowed students for the project.
            facilities (list[str] | str | None): Required facility names.
                Pass a list like ["AI Lab"] or a comma-separated string.
                Use None if no facilities are required.
            supervisor (str | None): Supervisor faculty ID.

        Returns:
            int: The created project_id.
        """
        # Insert the project row first, then add relational prerequisites and facilities.
        self.cursor.execute("""
        INSERT INTO projects 
        (title, description, specialization, max_students, supervisor)
        VALUES (?, ?, ?, ?, ?)
        """, (title, description, specialization, max_students, supervisor))
        project_id = self.cursor.lastrowid

        # Add prerequisites as a relational mapping.
        if prerequisites:
            prerequisites_list = [p.strip() for p in prerequisites.split(",")] if isinstance(prerequisites, str) else prerequisites
            for course_code in prerequisites_list:
                if course_code:
                    self.add_project_prerequisite(project_id, course_code)

        # Add required facilities through the facilities table.
        if facilities:
            facility_names = [f.strip() for f in facilities.split(",")] if isinstance(facilities, str) else facilities
            for facility_name in facility_names:
                if facility_name:
                    facility_id = self.add_facility(facility_name)
                    self.add_project_facility(project_id, facility_id)

        self.conn.commit()
        return project_id

    def get_all_projects(self):
        """Return all projects."""
        self.cursor.execute("SELECT * FROM projects")
        return self.cursor.fetchall()

    def get_project_by_id(self, project_id):
        """Return one project by ID, or None if the project does not exist."""
        self.cursor.execute(
            "SELECT * FROM projects WHERE project_id = ?", (project_id,)
        )
        return self.cursor.fetchone()

    def get_open_projects(self):
        """Return projects that are currently open for registration."""
        self.cursor.execute("SELECT * FROM projects WHERE status = 'open'")
        return self.cursor.fetchall()

    def check_project_capacity(self, project_id):
        """Return True if the project has available student capacity."""
        project = self.get_project_by_id(project_id)
        if project is None:
            return False

        # Access by column name so schema changes do not break this logic.
        max_students = project["max_students"]
        allocated_students = project["allocated_students"]
        return allocated_students < max_students

    def delete_project(self, p_id):
        """Delete a project by ID."""
        self.cursor.execute("DELETE FROM projects WHERE project_id = ?", (p_id,))
        self.conn.commit()

    # =========================
    # Team Operations
    # =========================
    def create_team(self, team_name):
        """Create a team and return its generated ID."""
        self.cursor.execute("INSERT INTO teams (team_name) VALUES (?)", (team_name,))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_team_by_id(self, team_id):
        """Return one team by ID, or None if the team does not exist."""
        self.cursor.execute("SELECT * FROM teams WHERE team_id = ?", (team_id,))
        return self.cursor.fetchone()

    def add_team_member(self, team_id, student_id):
        """Add a student to a team."""
        # Prevent duplicate membership via UNIQUE constraint.
        try:
            self.cursor.execute("""
            INSERT INTO team_members (team_id, student_id)
            VALUES (?, ?)
            """, (team_id, student_id))
            self.conn.commit()
            return True, None
        except sqlite3.IntegrityError as exc:
            message = str(exc)
            if "UNIQUE constraint failed" in message:
                return False, "Student already in this team."
            if "FOREIGN KEY constraint failed" in message:
                return False, "Invalid team or student ID."
            return False, message

    def check_student_already_in_team(self, student_id):
        """Return True if a student is already assigned to any team."""
        self.cursor.execute(
            "SELECT 1 FROM team_members WHERE student_id = ? LIMIT 1",
            (student_id,)
        )
        return self.cursor.fetchone() is not None

    # =========================
    # Registration
    # =========================
    def register_team(self, team_id, project_id):
        """Register a team for a project and update the allocated student count."""
        # Calculate actual team size from team_members table.
        self.cursor.execute(
            "SELECT COUNT(*) FROM team_members WHERE team_id = ?", (team_id,)
        )
        actual_count = self.cursor.fetchone()[0]

        try:
            self.cursor.execute("""
            INSERT INTO registrations (team_id, project_id)
            VALUES (?, ?)
            """, (team_id, project_id))

            self.cursor.execute("""
            UPDATE projects 
            SET allocated_students = allocated_students + ?
            WHERE project_id = ?
            """, (actual_count, project_id))

            self.conn.commit()
            return actual_count
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False

    def check_team_registered(self, team_id):
        """Return True if a team already has a project registration."""
        self.cursor.execute(
            "SELECT 1 FROM registrations WHERE team_id = ? LIMIT 1",
            (team_id,)
        )
        return self.cursor.fetchone() is not None

    # =========================
    # Close connection
    # =========================
    def close(self):
        """Close the database connection."""
        self.conn.close()