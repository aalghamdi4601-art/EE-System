# views/available_projects_view.py
# Member 3 - Available Projects Browser

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QLineEdit, QScrollArea, QSizePolicy,
    QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from team_controller import TeamController
from validation import validate_registration
from models import Student, Team, Project, Faculty

PRIMARY_COLOR    = "#1A3C6E"
ACCENT_COLOR     = "#2E7D32"
LIGHT_BG         = "#F4F6F8"
CARD_BG          = "#FFFFFF"
TEXT_PRIMARY     = "#1C1C1E"
TEXT_SECONDARY   = "#6B7280"
BORDER_COLOR     = "#E0E0E0"
DANGER_COLOR     = "#C62828"
TAG_BG           = "#E8EEF9"
TAG_TEXT         = "#1A3C6E"
SLOTS_OK_COLOR   = "#2E7D32"
SLOTS_LOW_COLOR  = "#E65100"
SLOTS_FULL_COLOR = "#C62828"

PROGRAM_OPTIONS = ["All Programs", "Computer", "Communications", "Power", "Biomedical"]


def make_tag(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI", 8))
    lbl.setStyleSheet(
        f"background-color: {TAG_BG}; color: {TAG_TEXT}; "
        f"border-radius: 10px; padding: 2px 8px;"
    )
    lbl.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    return lbl


def make_label(text: str, size: int = 10, bold: bool = False,
               color: str = TEXT_PRIMARY, wrap: bool = False) -> QLabel:
    lbl = QLabel(text)
    f = QFont("Segoe UI", size)
    f.setBold(bold)
    lbl.setFont(f)
    lbl.setStyleSheet(f"color: {color};")
    lbl.setWordWrap(wrap)
    return lbl


class ProjectCard(QFrame):
    def __init__(self, project: dict, current_student: dict = None,
                 team_controller: TeamController = None, parent=None):
        super().__init__(parent)
        self.project         = project
        self.current_student = current_student
        self.team_controller = team_controller
        self.expanded        = False

        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 10px;
                border: 1px solid {BORDER_COLOR};
            }}
            QFrame:hover {{ border: 1px solid #AABDE0; }}
            """
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._build_ui()

    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 14, 20, 14)
        self.main_layout.setSpacing(0)

        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        left_col = QVBoxLayout()
        left_col.setSpacing(4)
        left_col.addWidget(
            make_label(self.project.get("title", "Untitled"),
                       size=12, bold=True, color=PRIMARY_COLOR)
        )

        tags_row = QHBoxLayout()
        tags_row.setSpacing(6)
        tags_row.addWidget(make_tag(self.project.get("specialization", "General")))
        if self.project.get("supervisor"):
            tags_row.addWidget(make_tag(f"👤 {self.project['supervisor']}"))
        tags_row.addStretch()
        left_col.addLayout(tags_row)
        header_row.addLayout(left_col, stretch=4)

        right_col = QVBoxLayout()
        right_col.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        right_col.setSpacing(4)
        right_col.addWidget(self._slots_label(),
                            alignment=Qt.AlignmentFlag.AlignRight)
        self.arrow_lbl = make_label("▼", size=9, color=TEXT_SECONDARY)
        right_col.addWidget(self.arrow_lbl,
                            alignment=Qt.AlignmentFlag.AlignRight)
        header_row.addLayout(right_col, stretch=1)
        self.main_layout.addLayout(header_row)

        self.detail_widget = QWidget()
        d = QVBoxLayout(self.detail_widget)
        d.setContentsMargins(0, 12, 0, 4)
        d.setSpacing(10)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {BORDER_COLOR};")
        d.addWidget(line)

        if self.project.get("description"):
            d.addWidget(make_label("Description", 9, bold=True, color=TEXT_SECONDARY))
            d.addWidget(make_label(self.project["description"], 10,
                                   color=TEXT_PRIMARY, wrap=True))

        d.addWidget(make_label("Prerequisites", 9, bold=True, color=TEXT_SECONDARY))
        prereqs = self.project.get("prerequisites") or []
        if prereqs:
            prereq_row = QHBoxLayout()
            prereq_row.setSpacing(6)
            for code in prereqs:
                prereq_row.addWidget(make_tag(code))
            prereq_row.addStretch()
            d.addLayout(prereq_row)
        else:
            d.addWidget(make_label("None required", 10, color=TEXT_SECONDARY))

        facilities_str = self.project.get("required_facilities", "") or ""
        if facilities_str.strip():
            d.addWidget(make_label("Required Facilities", 9,
                                   bold=True, color=TEXT_SECONDARY))
            d.addWidget(make_label(f"🔬  {facilities_str}", 10,
                                   color=TEXT_PRIMARY, wrap=True))

        max_s   = self.project.get("max_students", 3) or 3
        alloc_s = self.project.get("allocated_students", 0) or 0
        left    = max_s - alloc_s
        d.addWidget(make_label("Availability", 9, bold=True, color=TEXT_SECONDARY))
        d.addWidget(make_label(
            f"  {alloc_s} / {max_s} slots filled  —  {left} slot(s) remaining",
            10,
            color=SLOTS_OK_COLOR if left > 0 else SLOTS_FULL_COLOR
        ))

        d.addWidget(make_label(
            f"Project ID: {self.project.get('project_id', '—')}",
            9, color=TEXT_SECONDARY
        ))

        # Register button
        if self.current_student:
            btn_register = QPushButton("📝  Register for this Project")
            btn_register.setFixedHeight(38)
            btn_register.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {PRIMARY_COLOR};
                    color: white;
                    border-radius: 7px;
                    font-weight: bold;
                    border: none;
                }}
                QPushButton:hover {{ background-color: #25518C; }}
                """
            )
            btn_register.clicked.connect(self._register)
            d.addWidget(btn_register)

        self.detail_widget.setVisible(False)
        self.main_layout.addWidget(self.detail_widget)

    def _slots_label(self) -> QLabel:
        max_s   = self.project.get("max_students", 3) or 3
        alloc_s = self.project.get("allocated_students", 0) or 0
        left    = max_s - alloc_s

        if left <= 0:
            color, text = SLOTS_FULL_COLOR, "FULL"
        elif left == 1:
            color, text = SLOTS_LOW_COLOR, "1 slot left"
        else:
            color, text = SLOTS_OK_COLOR, f"{left} slots open"

        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl.setStyleSheet(
            f"color: {color}; background-color: transparent; "
            f"border: 1px solid {color}; border-radius: 8px; padding: 2px 8px;"
        )
        return lbl

    def _register(self):
        """Validate and register the team for this project."""
        if not self.current_student or not self.team_controller:
            return

        student_id = self.current_student.get("student_id")
        team_info  = self.team_controller.get_team_of_student(student_id)

        if not team_info:
            QMessageBox.warning(self, "No Team",
                                "You must be in a team before registering.")
            return

        # Build objects for validation
        team_id    = team_info["team_id"]
        members_data = self.team_controller.get_team_members(team_id)

        members = [
            Student(
                m["student_id"], m["name"], m["gpa"], m["program"],
                [r["course_code"] for r in
                 self.team_controller.db.get_student_courses(m["student_id"])]
            )
            for m in members_data
        ]

        team = Team(team_info["team_name"], members=members, team_id=team_id)

        project = Project(
            title=self.project.get("title"),
            description=self.project.get("description"),
            specialization=self.project.get("specialization"),
            prerequisites=self.project.get("prerequisites") or [],
            max_students=self.project.get("max_students", 3),
            allocated_students=self.project.get("allocated_students", 0),
            project_id=self.project.get("project_id"),
        )

        faculty = Faculty("F001", "Dr. Khalid", "ECE",
                          max_supervisions=3, current_supervisions=0)

        db = self.team_controller.db
        ok, msg = validate_registration(
            team, project, faculty, db,
            self.project.get("project_id"), team_id
        )

        if ok:
            db.register_team(team_id, self.project.get("project_id"))
            QMessageBox.information(self, "Success",
                                    f"✅ Registered for '{project.title}'!")
        else:
            QMessageBox.warning(self, "Registration Failed", msg)

    def mousePressEvent(self, event):
        self.expanded = not self.expanded
        self.detail_widget.setVisible(self.expanded)
        self.arrow_lbl.setText("▲" if self.expanded else "▼")
        self.adjustSize()


class AvailableProjectsView(QWidget):
    def __init__(self, specialization: str = None,
                 current_student: dict = None, parent=None):
        super().__init__(parent)
        self.controller         = TeamController()
        self.initial_filter     = specialization
        self.current_student    = current_student
        self.all_projects       = []
        self.displayed_projects = []

        self.setWindowTitle("Available Graduation Projects")
        self.setMinimumSize(780, 620)
        self.setStyleSheet(f"background-color: {LIGHT_BG};")

        self._build_ui()
        QTimer.singleShot(0, self._load_projects)

    def closeEvent(self, event):
        self.controller.close()
        super().closeEvent(event)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_controls())

        self.results_label = make_label("Loading projects...", 10, color=TEXT_SECONDARY)
        self.results_label.setContentsMargins(28, 6, 28, 2)
        root.addWidget(self.results_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        self.list_container = QWidget()
        self.list_container.setStyleSheet(f"background-color: {LIGHT_BG};")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(24, 8, 24, 24)
        self.list_layout.setSpacing(12)
        self.list_layout.addStretch()

        self.scroll_area.setWidget(self.list_container)
        root.addWidget(self.scroll_area)

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setStyleSheet(f"background-color: {PRIMARY_COLOR}; border: none;")
        header.setFixedHeight(64)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(28, 0, 28, 0)

        title = QLabel("📋  Available Graduation Projects")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setFixedSize(90, 30)
        refresh_btn.setFont(QFont("Segoe UI", 9))
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255,255,255,0.15);
                color: white; border-radius: 6px;
                border: 1px solid rgba(255,255,255,0.4);
            }
            QPushButton:hover { background-color: rgba(255,255,255,0.25); }
            """
        )
        refresh_btn.clicked.connect(self._load_projects)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(refresh_btn)
        return header

    def _build_controls(self) -> QWidget:
        container = QFrame()
        container.setStyleSheet(
            f"background-color: {CARD_BG}; border-bottom: 1px solid {BORDER_COLOR};"
        )
        layout = QHBoxLayout(container)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(14)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "🔍  Search by title, supervisor, or facility..."
        )
        self.search_input.setFixedHeight(36)
        self.search_input.setFont(QFont("Segoe UI", 10))
        self.search_input.setStyleSheet(
            f"border: 1px solid {BORDER_COLOR}; border-radius: 8px; "
            f"padding: 0 10px; background: {LIGHT_BG};"
        )

        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._apply_filters)
        self.search_input.textChanged.connect(
            lambda: self._search_timer.start(300)
        )

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(PROGRAM_OPTIONS)
        self.filter_combo.setFixedHeight(36)
        self.filter_combo.setMinimumWidth(160)
        self.filter_combo.setFont(QFont("Segoe UI", 10))
        self.filter_combo.setStyleSheet(
            f"""
            QComboBox {{
                border: 1px solid {BORDER_COLOR}; border-radius: 8px;
                padding: 0 10px; background: {LIGHT_BG}; color: {TEXT_PRIMARY};
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background: {CARD_BG};
                selection-background-color: {TAG_BG};
                selection-color: {TEXT_PRIMARY};
            }}
            """
        )
        if self.initial_filter and self.initial_filter in PROGRAM_OPTIONS:
            self.filter_combo.setCurrentText(self.initial_filter)
        self.filter_combo.currentIndexChanged.connect(self._apply_filters)

        layout.addWidget(self.search_input, stretch=3)
        layout.addWidget(self.filter_combo, stretch=1)
        return container

    def _load_projects(self):
        self.results_label.setText("Loading...")
        self.all_projects = self.controller.get_available_projects()
        self._apply_filters()

    def _apply_filters(self):
        keyword = self.search_input.text().strip().lower()
        program = self.filter_combo.currentText()

        filtered = []
        for proj in self.all_projects:
            if program != "All Programs":
                spec = proj.get("specialization", "") or ""
                if spec != program and spec != "All":
                    continue
            if keyword:
                searchable = " ".join([
                    str(proj.get("title", "")),
                    str(proj.get("supervisor", "")),
                    str(proj.get("required_facilities", "")),
                    str(proj.get("description", "")),
                ]).lower()
                if keyword not in searchable:
                    continue
            filtered.append(proj)

        self.displayed_projects = filtered
        self._render_project_list()

    def _render_project_list(self):
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        count = len(self.displayed_projects)
        if count == 0:
            empty_lbl = make_label(
                "No projects match your search criteria.",
                11, color=TEXT_SECONDARY
            )
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setContentsMargins(0, 40, 0, 0)
            self.list_layout.insertWidget(0, empty_lbl)
            self.results_label.setText("No results found.")
            return

        chosen_program = self.filter_combo.currentText()
        suffix = f"  —  filtered by '{chosen_program}'" if chosen_program != "All Programs" else ""
        self.results_label.setText(
            f"Showing {count} project{'s' if count != 1 else ''}" + suffix
        )

        for proj in self.displayed_projects:
            card = ProjectCard(
                project=proj,
                current_student=self.current_student,
                team_controller=self.controller
            )
            self.list_layout.insertWidget(self.list_layout.count() - 1, card)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AvailableProjectsView(specialization="Computer")
    window.show()
    sys.exit(app.exec())
