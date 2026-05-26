# views/student_dashboard.py
# Member 3 - Student Dashboard
#
# Main window shown to a logged-in student after Member 4's login system
# hands them off.  Shows:
#   * Their academic profile.
#   * Their current team status (or a prompt to create one).
#   * Buttons to create a team or browse available projects.
#
# Member 4 passes in `current_student` as a dict from the auth layer.

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy, QMessageBox,
    QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from controllers.team_controller import TeamController
from views.team_form import TeamFormView
from views.available_projects_view import AvailableProjectsView


# ---------------------------------------------------------------------------
# Shared colour palette (used across all my views)
# ---------------------------------------------------------------------------
PRIMARY_COLOR   = "#1A3C6E"
ACCENT_COLOR    = "#2E7D32"
LIGHT_BG        = "#F4F6F8"
CARD_BG         = "#FFFFFF"
TEXT_PRIMARY    = "#1C1C1E"
TEXT_SECONDARY  = "#6B7280"
DANGER_COLOR    = "#C62828"
SUCCESS_COLOR   = "#2E7D32"
BORDER_COLOR    = "#E0E0E0"


def make_label(text: str, font_size: int = 11, bold: bool = False,
               color: str = TEXT_PRIMARY) -> QLabel:
    """Small helper to quickly create a styled QLabel."""
    lbl = QLabel(text)
    font = QFont("Segoe UI", font_size)
    font.setBold(bold)
    lbl.setFont(font)
    lbl.setStyleSheet(f"color: {color};")
    return lbl


class StudentDashboard(QWidget):
    """
    The main dashboard for a logged-in student.

    Parameters:
        current_student : dict — keys: student_id, name, email, program, gpa
                                  (provided by Member 4's auth system)
        parent          : QWidget or None
    """

    def __init__(self, current_student: dict, parent=None):
        super().__init__(parent)
        self.current_student = current_student

        # One controller for the dashboard's lifetime.  Sub-windows
        # (team form, projects view) create their own — that's fine,
        # SQLite handles multiple connections to the same file.
        self.controller = TeamController()

        # Keep references so PyQt doesn't garbage-collect the sub-windows
        self.team_form_window = None
        self.projects_window  = None

        self.setWindowTitle("Student Dashboard — Graduation Project Registration")
        self.setMinimumSize(850, 600)
        self.setStyleSheet(f"background-color: {LIGHT_BG};")

        self._build_ui()
        self._load_team_status()  # populate the team section on startup

    # ------------------------------------------------------------------
    # Close-event override — make sure we release the DB connection
    # ------------------------------------------------------------------

    def closeEvent(self, event):
        self.controller.close()
        super().closeEvent(event)

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Top navy banner
        root_layout.addWidget(self._build_header())

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {LIGHT_BG};")
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(30, 24, 30, 30)
        self.content_layout.setSpacing(20)

        self.content_layout.addWidget(self._build_info_card())
        self.team_status_card = self._build_team_status_card()
        self.content_layout.addWidget(self.team_status_card)
        self.content_layout.addWidget(self._build_action_buttons())
        self.content_layout.addStretch()

        scroll.setWidget(content_widget)
        root_layout.addWidget(scroll)

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setStyleSheet(f"background-color: {PRIMARY_COLOR}; border: none;")
        header.setFixedHeight(72)

        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(30, 0, 30, 0)

        title = QLabel("🎓  ECE Graduation Project Registration System")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: white;")

        name = self.current_student.get("name", "Student")
        greeting = QLabel(f"Welcome,  {name}")
        greeting.setFont(QFont("Segoe UI", 11))
        greeting.setStyleSheet("color: rgba(255,255,255,0.85);")
        greeting.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        h_layout.addWidget(title)
        h_layout.addStretch()
        h_layout.addWidget(greeting)
        return header

    def _build_info_card(self) -> QFrame:
        """A card that shows the student's basic academic info."""
        card = QFrame()
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 10px;
                border: 1px solid {BORDER_COLOR};
            }}
            """
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        layout.addWidget(make_label("My Academic Profile", 13, bold=True, color=PRIMARY_COLOR))
        layout.addWidget(self._divider())

        grid = QHBoxLayout()
        grid.setSpacing(40)

        s = self.current_student
        info_items = [
            ("Student ID",  str(s.get("student_id", "—"))),
            ("Program",     str(s.get("program",    "—"))),
            ("GPA",         str(s.get("gpa",        "—"))),
            ("Email",       str(s.get("email",      "—"))),
        ]

        for label, value in info_items:
            col = QVBoxLayout()
            col.addWidget(make_label(label, 9, color=TEXT_SECONDARY))
            col.addWidget(make_label(value, 11, bold=True))
            grid.addLayout(col)

        grid.addStretch()
        layout.addLayout(grid)
        return card

    def _build_team_status_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("teamStatusCard")
        card.setStyleSheet(
            f"""
            QFrame#teamStatusCard {{
                background-color: {CARD_BG};
                border-radius: 10px;
                border: 1px solid {BORDER_COLOR};
            }}
            """
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        layout.addWidget(make_label("My Team", 13, bold=True, color=PRIMARY_COLOR))
        layout.addWidget(self._divider())

        # _load_team_status() fills the rest of this card dynamically
        self.team_status_layout = layout
        return card

    def _build_action_buttons(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        self.btn_create_team = self._make_button(
            "➕  Create a Team", primary=True,
            tooltip="Form a new team of 3 students"
        )
        self.btn_create_team.clicked.connect(self._open_team_form)

        btn_projects = self._make_button(
            "📋  Browse Available Projects", primary=False,
            tooltip="View all open graduation projects"
        )
        btn_projects.clicked.connect(self._open_available_projects)

        layout.addWidget(self.btn_create_team)
        layout.addWidget(btn_projects)
        layout.addStretch()
        return container

    # ------------------------------------------------------------------
    # Dynamic: team status card content
    # ------------------------------------------------------------------

    def _load_team_status(self):
        """
        Looks up the student's team via the controller and rebuilds the
        team status card based on whether they're in a team or not.
        """
        student_id = self.current_student.get("student_id")
        team_info  = self.controller.get_team_of_student(student_id) if student_id else None

        # Clear previous content (keep the title + divider at index 0 and 1)
        while self.team_status_layout.count() > 2:
            item = self.team_status_layout.takeAt(2)
            if item is None:
                continue
            w = item.widget()
            if w is not None:
                w.deleteLater()
            else:
                # It's a layout — recursively clear it
                self._clear_layout(item.layout())

        if team_info is None:
            # Not in a team yet
            no_team_lbl = make_label(
                "You are not currently in a team.",
                11, color=TEXT_SECONDARY
            )
            no_team_lbl.setAlignment(Qt.AlignCenter)
            self.team_status_layout.addWidget(no_team_lbl)

            hint = make_label(
                "Use the 'Create a Team' button below to get started.",
                10, color=ACCENT_COLOR
            )
            hint.setAlignment(Qt.AlignCenter)
            self.team_status_layout.addWidget(hint)

            self.btn_create_team.setEnabled(True)
            self.btn_create_team.setToolTip("Form a new team of 3 students")

        else:
            # Already in a team — show team details
            team_id   = team_info["team_id"]
            team_name = team_info["team_name"]
            members   = self.controller.get_team_members(team_id)

            self.team_status_layout.addWidget(
                make_label(f"Team Name:  {team_name}", 12, bold=True, color=PRIMARY_COLOR)
            )

            self.team_status_layout.addWidget(
                make_label("Members:", 10, color=TEXT_SECONDARY)
            )

            for m in members:
                m_row = QHBoxLayout()
                m_row.addWidget(make_label(f"  • {m.get('name', '?')}", 11))
                m_row.addWidget(make_label(f"({m.get('student_id', '?')})",
                                            10, color=TEXT_SECONDARY))
                m_row.addWidget(make_label(f"— {m.get('program', '?')}",
                                            10, color=TEXT_SECONDARY))
                m_row.addStretch()
                self.team_status_layout.addLayout(m_row)

            self.btn_create_team.setEnabled(False)
            self.btn_create_team.setToolTip("You are already in a team.")

    def _clear_layout(self, layout):
        """Helper to recursively delete a sub-layout's widgets."""
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            elif item.layout() is not None:
                self._clear_layout(item.layout())

    # ------------------------------------------------------------------
    # Button actions
    # ------------------------------------------------------------------

    def _open_team_form(self):
        self.team_form_window = TeamFormView(
            current_student=self.current_student,
            on_success_callback=self._on_team_created
        )
        self.team_form_window.show()

    def _on_team_created(self):
        """Called by TeamFormView after a successful team creation."""
        self._load_team_status()  # refresh

    def _open_available_projects(self):
        specialization = self.current_student.get("program")
        self.projects_window = AvailableProjectsView(specialization=specialization)
        self.projects_window.show()

    # ------------------------------------------------------------------
    # Utility widget builders
    # ------------------------------------------------------------------

    def _divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color: {BORDER_COLOR};")
        return line

    def _make_button(self, text: str, primary: bool = True,
                     tooltip: str = "") -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(42)
        btn.setMinimumWidth(200)
        btn.setFont(QFont("Segoe UI", 10, QFont.Bold if primary else QFont.Normal))
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)

        if primary:
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {PRIMARY_COLOR};
                    color: white;
                    border-radius: 8px;
                    border: none;
                    padding: 0 18px;
                }}
                QPushButton:hover  {{ background-color: #25518C; }}
                QPushButton:pressed{{ background-color: #122A4E; }}
                QPushButton:disabled {{
                    background-color: #AAAAAA; color: #EEEEEE;
                }}
                """
            )
        else:
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {CARD_BG};
                    color: {PRIMARY_COLOR};
                    border-radius: 8px;
                    border: 2px solid {PRIMARY_COLOR};
                    padding: 0 18px;
                }}
                QPushButton:hover  {{ background-color: #EBF0FF; }}
                QPushButton:pressed{{ background-color: #D0DBFF; }}
                """
            )
        return btn


# ---------------------------------------------------------------------------
# Standalone test — pretend a student is already logged in.
# Member 4 will replace this with real auth output.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    test_student = {
        "student_id": "S001",          # Must exist in the DB for testing
        "name":       "Test Student",
        "email":      "test@test.edu",
        "program":    "Computer",
        "gpa":        3.75,
    }

    dashboard = StudentDashboard(current_student=test_student)
    dashboard.show()
    sys.exit(app.exec_())
