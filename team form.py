# views/team_form.py
# Member 3 - Team Creation Form
#
# A QDialog where a student creates a new team of 3.
# Member 1's ID is pre-filled (from the logged-in user) and read-only.
# Members 2 and 3 IDs are validated live as the user types.

from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from controllers.team_controller import TeamController


# ---------------------------------------------------------------------------
# Shared palette
# ---------------------------------------------------------------------------
PRIMARY_COLOR  = "#1A3C6E"
ACCENT_COLOR   = "#2E7D32"
LIGHT_BG       = "#F4F6F8"
CARD_BG        = "#FFFFFF"
TEXT_PRIMARY   = "#1C1C1E"
TEXT_SECONDARY = "#6B7280"
DANGER_COLOR   = "#C62828"
SUCCESS_COLOR  = "#2E7D32"
BORDER_COLOR   = "#E0E0E0"
ERROR_FIELD_BG = "#FFF3F3"


class TeamFormView(QDialog):
    """
    Modal dialog for creating a new student team.

    Parameters:
        current_student     : dict — the logged-in student's info (Member 4 provides)
        on_success_callback : callable — called (no args) after a team is created
                              so the dashboard can refresh itself
        parent              : QWidget or None
    """

    def __init__(self, current_student: dict, on_success_callback=None, parent=None):
        super().__init__(parent)
        self.current_student = current_student
        self.on_success      = on_success_callback
        self.controller      = TeamController()

        self.setWindowTitle("Create a New Team")
        self.setMinimumWidth(480)
        self.setModal(True)
        self.setStyleSheet(f"background-color: {LIGHT_BG};")

        self._build_ui()

    # ------------------------------------------------------------------
    # Cleanup — close DB connection when dialog closes
    # ------------------------------------------------------------------

    def closeEvent(self, event):
        self.controller.close()
        super().closeEvent(event)

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        card = QFrame()
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 10px;
                margin: 20px;
                border: 1px solid {BORDER_COLOR};
            }}
            """
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 24, 28, 24)
        card_layout.setSpacing(16)

        # ----- Team Name -----
        card_layout.addWidget(self._field_label("Team Name  *"))
        self.team_name_input = self._make_input("e.g. Phoenix Team")
        card_layout.addWidget(self.team_name_input)
        self.team_name_error = self._error_label()
        card_layout.addWidget(self.team_name_error)

        card_layout.addWidget(
            self._section_divider("Team Members  (exactly 3 students required)")
        )

        # ----- Member 1 (pre-filled, read-only) -----
        card_layout.addWidget(self._field_label("Member 1 — Student ID  (You)"))
        self.member1_input = self._make_input(read_only=True)
        self.member1_input.setText(str(self.current_student.get("student_id", "")))
        self.member1_info = self._info_label(
            f"  {self.current_student.get('name', '')}  |  "
            f"{self.current_student.get('program', '')}"
        )
        card_layout.addWidget(self.member1_input)
        card_layout.addWidget(self.member1_info)

        # ----- Member 2 -----
        card_layout.addWidget(self._field_label("Member 2 — Student ID  *"))
        self.member2_input = self._make_input("Enter student ID")
        self.member2_error    = self._error_label()
        self.member2_info_lbl = self._info_label()
        self.member2_input.textChanged.connect(
            lambda: self._live_validate(self.member2_input,
                                        self.member2_error,
                                        self.member2_info_lbl)
        )
        card_layout.addWidget(self.member2_input)
        card_layout.addWidget(self.member2_error)
        card_layout.addWidget(self.member2_info_lbl)

        # ----- Member 3 -----
        card_layout.addWidget(self._field_label("Member 3 — Student ID  *"))
        self.member3_input = self._make_input("Enter student ID")
        self.member3_error    = self._error_label()
        self.member3_info_lbl = self._info_label()
        self.member3_input.textChanged.connect(
            lambda: self._live_validate(self.member3_input,
                                        self.member3_error,
                                        self.member3_info_lbl)
        )
        card_layout.addWidget(self.member3_input)
        card_layout.addWidget(self.member3_error)
        card_layout.addWidget(self.member3_info_lbl)

        root.addWidget(card)

        # ----- Buttons -----
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(20, 0, 20, 20)
        btn_row.setSpacing(12)
        btn_row.addStretch()

        self.cancel_btn = self._make_button("Cancel", primary=False)
        self.cancel_btn.clicked.connect(self.reject)

        self.submit_btn = self._make_button("Create Team", primary=True)
        self.submit_btn.clicked.connect(self._submit)

        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.submit_btn)
        root.addLayout(btn_row)

    # ------------------------------------------------------------------
    # Live validation as the user types in Member 2 / 3 fields
    # ------------------------------------------------------------------

    def _live_validate(self, input_field: QLineEdit, error_label: QLabel,
                       info_label: QLabel):
        sid = input_field.text().strip()

        # Reset previous feedback
        error_label.setText("")
        info_label.setText("")
        self._reset_field_style(input_field)

        if not sid:
            return  # nothing typed yet

        # Check if it's also member 1 (the current user)
        if sid == self.current_student.get("student_id"):
            self._mark_field_error(input_field, error_label,
                                   "This is your own ID — you are already Member 1.")
            return

        # Validate the ID exists
        valid, msg = self.controller.validate_student_id(sid)
        if not valid:
            self._mark_field_error(input_field, error_label, msg)
            return

        # Already in a team?
        if self.controller.is_student_in_a_team(sid):
            existing = self.controller.get_team_of_student(sid)
            team_ref = f"'{existing['team_name']}'" if existing else "another team"
            self._mark_field_error(input_field, error_label,
                                   f"This student is already in {team_ref}.")
            return

        # All good — show student info in green
        student = self.controller.get_student_by_id(sid)
        if student:
            completed_count = len(self.controller.get_student_courses(sid))
            info_label.setText(
                f"  ✓  {student.get('name', '')}  |  "
                f"{student.get('program', '')}  |  "
                f"GPA: {student.get('gpa', '?')}  |  "
                f"{completed_count} course(s) completed"
            )
            info_label.setStyleSheet(f"color: {SUCCESS_COLOR}; font-size: 10px;")
            input_field.setStyleSheet(
                f"border: 2px solid {SUCCESS_COLOR}; border-radius: 6px; "
                f"padding: 6px; background: #F0FFF4;"
            )

    # ------------------------------------------------------------------
    # Form submission
    # ------------------------------------------------------------------

    def _submit(self):
        # Clear all previous error markers
        self.team_name_error.setText("")
        self.member2_error.setText("")
        self.member3_error.setText("")
        self._reset_field_style(self.team_name_input)
        self._reset_field_style(self.member2_input)
        self._reset_field_style(self.member3_input)

        team_name  = self.team_name_input.text().strip()
        member1_id = self.member1_input.text().strip()
        member2_id = self.member2_input.text().strip()
        member3_id = self.member3_input.text().strip()

        # Quick front-end checks
        if not team_name:
            self._mark_field_error(self.team_name_input, self.team_name_error,
                                   "Team name is required.")
            return
        if not member2_id:
            self._mark_field_error(self.member2_input, self.member2_error,
                                   "Member 2 student ID is required.")
            return
        if not member3_id:
            self._mark_field_error(self.member3_input, self.member3_error,
                                   "Member 3 student ID is required.")
            return

        # Lock the button while DB work is happening
        self.submit_btn.setEnabled(False)
        self.submit_btn.setText("Creating...")

        success, message = self.controller.create_team(
            team_name=team_name,
            member_ids=[member1_id, member2_id, member3_id]
        )

        self.submit_btn.setEnabled(True)
        self.submit_btn.setText("Create Team")

        if success:
            QMessageBox.information(self, "Team Created", f"✅  {message}")
            if self.on_success:
                self.on_success()
            self.accept()
        else:
            # Highlight the relevant field where possible
            lower_msg = message.lower()
            if "team name" in lower_msg or "taken" in lower_msg:
                self._mark_field_error(self.team_name_input, self.team_name_error, message)
            elif member2_id and member2_id in message:
                self._mark_field_error(self.member2_input, self.member2_error, message)
            elif member3_id and member3_id in message:
                self._mark_field_error(self.member3_input, self.member3_error, message)
            else:
                QMessageBox.critical(self, "Error Creating Team", message)

    # ------------------------------------------------------------------
    # Helper widget builders
    # ------------------------------------------------------------------

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setStyleSheet(f"background-color: {PRIMARY_COLOR}; border: none;")
        header.setFixedHeight(56)

        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 24, 0)

        title = QLabel("🤝  Create a New Team")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet("color: white;")
        h_layout.addWidget(title)
        return header

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl.setStyleSheet(f"color: {TEXT_PRIMARY};")
        return lbl

    def _make_input(self, placeholder: str = "", read_only: bool = False) -> QLineEdit:
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setReadOnly(read_only)
        field.setFixedHeight(36)
        field.setFont(QFont("Segoe UI", 10))

        if read_only:
            field.setStyleSheet(
                f"border: 1px solid {BORDER_COLOR}; border-radius: 6px; "
                f"padding: 6px; background: #EFEFEF; color: {TEXT_SECONDARY};"
            )
        else:
            field.setStyleSheet(
                f"border: 1px solid {BORDER_COLOR}; border-radius: 6px; "
                f"padding: 6px; background: {CARD_BG}; color: {TEXT_PRIMARY};"
            )
        return field

    def _error_label(self) -> QLabel:
        lbl = QLabel("")
        lbl.setFont(QFont("Segoe UI", 9))
        lbl.setStyleSheet(f"color: {DANGER_COLOR};")
        lbl.setWordWrap(True)
        return lbl

    def _info_label(self, text: str = "") -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 9))
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY};")
        return lbl

    def _section_divider(self, title: str) -> QWidget:
        """A horizontal line with a small text label between the line halves."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 6, 0, 2)
        layout.setSpacing(8)

        left_line = QFrame()
        left_line.setFrameShape(QFrame.HLine)
        left_line.setStyleSheet(f"color: {BORDER_COLOR};")

        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY};")
        lbl.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        # ↑↑↑ Earlier I had a typo here: `lbl.setWhiteSpace = True`
        #     which silently added a fake attribute instead of doing
        #     anything.  Removed it — Qt handles label sizing fine on its own.

        right_line = QFrame()
        right_line.setFrameShape(QFrame.HLine)
        right_line.setStyleSheet(f"color: {BORDER_COLOR};")

        layout.addWidget(left_line, 1)
        layout.addWidget(lbl)
        layout.addWidget(right_line, 3)
        return container

    def _make_button(self, text: str, primary: bool = True) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setMinimumWidth(130)
        btn.setFont(QFont("Segoe UI", 10, QFont.Bold if primary else QFont.Normal))
        btn.setCursor(Qt.PointingHandCursor)

        if primary:
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {PRIMARY_COLOR};
                    color: white;
                    border-radius: 8px;
                    border: none;
                }}
                QPushButton:hover  {{ background-color: #25518C; }}
                QPushButton:pressed{{ background-color: #122A4E; }}
                QPushButton:disabled{{ background-color: #AAAAAA; }}
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
                }}
                QPushButton:hover  {{ background-color: #EBF0FF; }}
                QPushButton:pressed{{ background-color: #D0DBFF; }}
                """
            )
        return btn

    # ------------------------------------------------------------------
    # Field error styling
    # ------------------------------------------------------------------

    def _mark_field_error(self, field: QLineEdit, error_lbl: QLabel, message: str):
        field.setStyleSheet(
            f"border: 2px solid {DANGER_COLOR}; border-radius: 6px; "
            f"padding: 6px; background: {ERROR_FIELD_BG};"
        )
        error_lbl.setText(f"⚠  {message}")

    def _reset_field_style(self, field: QLineEdit):
        if field.isReadOnly():
            return
        field.setStyleSheet(
            f"border: 1px solid {BORDER_COLOR}; border-radius: 6px; "
            f"padding: 6px; background: {CARD_BG}; color: {TEXT_PRIMARY};"
        )
