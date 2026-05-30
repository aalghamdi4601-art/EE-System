
# Login window for the Graduation Project Registration System.
# Uses AuthManager from auth.py to verify credentials.
# Redirects to the correct dashboard based on the user's role.

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database import DatabaseManager
from auth import AuthManager

# Colour palette (matches student_dashboard.py) 
PRIMARY_COLOR   = "#1A3C6E"
ACCENT_COLOR    = "#2E7D32"
LIGHT_BG        = "#F4F6F8"
CARD_BG         = "#FFFFFF"
TEXT_PRIMARY    = "#1C1C1E"
TEXT_SECONDARY  = "#6B7280"
BORDER_COLOR    = "#E0E0E0"


class LoginWindow(QWidget):
    """Login screen — entry point for all user roles."""

    def __init__(self):
        super().__init__()
        # Initialise database and auth manager
        self.db   = DatabaseManager()
        self.auth = AuthManager(self.db)

        self.setWindowTitle("ECE Graduation Project System — Login")
        self.setFixedSize(420, 480)
        self.setStyleSheet(f"background-color: {LIGHT_BG};")

        self._build_ui()

    # UI construction 

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header bar
        root.addWidget(self._build_header())

        # Card in the centre
        card_wrapper = QVBoxLayout()
        card_wrapper.setContentsMargins(40, 30, 40, 30)
        card_wrapper.addWidget(self._build_card())
        root.addLayout(card_wrapper)

    def _build_header(self) -> QFrame:
        """Blue top bar with system title."""
        header = QFrame()
        header.setFixedHeight(72)
        header.setStyleSheet(f"background-color: {PRIMARY_COLOR}; border: none;")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 0, 30, 0)

        title = QLabel("🎓  ECE Graduation Project Registration System")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        return header

    def _build_card(self) -> QFrame:
        """White card containing the login form."""
        card = QFrame()
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 12px;
                border: 1px solid {BORDER_COLOR};
            }}
            """
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        # Title
        title = QLabel("Sign In")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY_COLOR}; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Enter your credentials to continue")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; border: none;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        # Email field
        layout.addWidget(self._field_label("Email"))
        self.email_input = self._make_input("student@university.edu")
        layout.addWidget(self.email_input)

        # Password field
        layout.addWidget(self._field_label("Password"))
        self.password_input = self._make_input("••••••••", password=True)
        layout.addWidget(self.password_input)

        # Allow pressing Enter to log in
        self.password_input.returnPressed.connect(self._on_login)

        layout.addSpacing(8)

        # Login button
        self.btn_login = QPushButton("Login")
        self.btn_login.setFixedHeight(44)
        self.btn_login.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover   {{ background-color: #25518C; }}
            QPushButton:pressed {{ background-color: #122A4E; }}
            """
        )
        self.btn_login.clicked.connect(self._on_login)
        layout.addWidget(self.btn_login)

        return card

    # Helper widgets 

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        return lbl

    def _make_input(self, placeholder: str, password: bool = False) -> QLineEdit:
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedHeight(40)
        field.setFont(QFont("Segoe UI", 10))
        if password:
            field.setEchoMode(QLineEdit.EchoMode.Password)
        field.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 0 12px;
                background: {LIGHT_BG};
                color: {TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border: 2px solid {PRIMARY_COLOR};
                background: white;
            }}
            """
        )
        return field

    # Login logic 

    def _on_login(self):
        """Called when the user presses Login or hits Enter."""
        email    = self.email_input.text().strip()
        password = self.password_input.text()

        # Attempt authentication
        ok, result = self.auth.login(email, password)

        if not ok:
            # Show error message
            QMessageBox.warning(self, "Login Failed", result)
            self.password_input.clear()
            return

        # result is the role: "student" / "faculty" / "admin"
        role = result
        self._open_dashboard(role)

    def _open_dashboard(self, role: str):
        """Open the correct dashboard and close the login window."""
        if role == "student":
            self._open_student_dashboard()
        elif role == "faculty":
            self._open_faculty_dashboard()
        

    def _open_student_dashboard(self):
        """Build the student dict and open StudentDashboard."""
        from student_dashboard import StudentDashboard

        # Get the logged-in student's full record from the database
        email = self.email_input.text().strip()

        # Build the dict that StudentDashboard expects
        row = self.db.cursor.execute(
            """
            SELECT s.student_id, s.name, s.gpa, s.program, u.email
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            WHERE u.email = ?
            """,
            (email,)
        ).fetchone()

        if row:
            current_student = {
                "student_id": row["student_id"],
                "name":       row["name"],
                "gpa":        row["gpa"],
                "program":    row["program"],
                "email":      row["email"],
            }
        else:
            QMessageBox.warning(self, "Error", "Student record not found.")
            return

        self.dashboard = StudentDashboard(current_student=current_student)
        self.dashboard.show()
        self.close()

    def _open_faculty_dashboard(self):
        """Open FacultyDashboardWindow."""
        from faculty_dashboard import FacultyDashboardWindow
        self.dashboard = FacultyDashboardWindow(db=self.db)
        self.dashboard.show()
        self.close()