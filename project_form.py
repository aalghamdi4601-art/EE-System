# ==========================================
# Project Form View
# ==========================================
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from project_controller import ProjectController


class ProjectFormWindow(QWidget):
    def __init__(self, db, project_to_edit=None, refresh_callback=None):
        super().__init__()
        self.project_to_edit  = project_to_edit
        self.refresh_callback = refresh_callback
        self.controller       = ProjectController(db)

        self.setWindowTitle("Edit Project" if project_to_edit else "Add New Project")
        self.setFixedSize(450, 380)
        self._build_ui()

        # Fill fields if editing
        if self.project_to_edit:
            self.entry_title.setText(project_to_edit.get("title", ""))
            self.entry_description.setText(project_to_edit.get("description", ""))
            self.entry_faculty.setText(project_to_edit.get("supervisor", ""))
            self.entry_specialization.setText(project_to_edit.get("specialization", ""))

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        # Title
        layout.addWidget(QLabel("Project Title:"))
        self.entry_title = QLineEdit()
        self.entry_title.setPlaceholderText("Enter project title")
        layout.addWidget(self.entry_title)

        # Description
        layout.addWidget(QLabel("Project Description:"))
        self.entry_description = QLineEdit()
        self.entry_description.setPlaceholderText("Enter project description")
        layout.addWidget(self.entry_description)

        # Faculty Member
        layout.addWidget(QLabel("Faculty Member ID:"))
        self.entry_faculty = QLineEdit()
        self.entry_faculty.setPlaceholderText("Enter faculty ID")
        layout.addWidget(self.entry_faculty)

        # Specialization
        layout.addWidget(QLabel("Specialization:"))
        self.entry_specialization = QLineEdit()
        self.entry_specialization.setPlaceholderText("e.g. Computer, Power, Communications")
        layout.addWidget(self.entry_specialization)

        # Save button
        btn_save = QPushButton("Save Project")
        btn_save.setFixedHeight(40)
        btn_save.setStyleSheet(
            "QPushButton { background-color: #2E7D32; color: white;"
            "border-radius: 6px; font-weight: bold; }"
            "QPushButton:hover { background-color: #388E3C; }"
        )
        btn_save.clicked.connect(self._save_data)
        layout.addWidget(btn_save)

    def _save_data(self):
        title          = self.entry_title.text().strip()
        description    = self.entry_description.text().strip()
        faculty_member = self.entry_faculty.text().strip()
        specialization = self.entry_specialization.text().strip()

        if self.project_to_edit:
            ok, msg = self.controller.update_project(
                self.project_to_edit.get("project_id"),
                title, description, faculty_member, specialization
            )
        else:
            ok, msg = self.controller.add_project(
                title, description, faculty_member, specialization
            )

        if ok:
            QMessageBox.information(self, "Success", msg)
            if self.refresh_callback:
                self.refresh_callback()
            self.close()
        else:
            QMessageBox.warning(self, "Error", msg)
