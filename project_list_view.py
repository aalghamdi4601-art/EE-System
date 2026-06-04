# ==========================================
# Project List View
# ==========================================
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from project_controller import ProjectController
from project_form import ProjectFormWindow


class ProjectListViewWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db         = db
        self.controller = ProjectController(db)
        self.setWindowTitle("Project List")
        self.setMinimumSize(700, 450)
        self._build_ui()
        self._load_projects()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Title", "Description", "Supervisor"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # Buttons
        btn_bar = QHBoxLayout()

        btn_edit = QPushButton("Edit Selected")
        btn_edit.setFixedHeight(36)
        btn_edit.setStyleSheet(
            "QPushButton { background-color: #E65100; color: white;"
            "border-radius: 6px; font-weight: bold; }"
            "QPushButton:hover { background-color: #F57C00; }"
        )
        btn_edit.clicked.connect(self._edit_selected)

        btn_delete = QPushButton("Delete Selected")
        btn_delete.setFixedHeight(36)
        btn_delete.setStyleSheet(
            "QPushButton { background-color: #C62828; color: white;"
            "border-radius: 6px; font-weight: bold; }"
            "QPushButton:hover { background-color: #D32F2F; }"
        )
        btn_delete.clicked.connect(self._delete_selected)

        btn_bar.addWidget(btn_edit)
        btn_bar.addWidget(btn_delete)
        btn_bar.addStretch()
        layout.addLayout(btn_bar)

    def _load_projects(self):
        """Load all projects into the table."""
        self.table.setRowCount(0)
        for project in self.controller.get_all_projects():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(project.get("project_id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(project.get("title", "")))
            self.table.setItem(row, 2, QTableWidgetItem(project.get("description", "")))
            self.table.setItem(row, 3, QTableWidgetItem(project.get("supervisor", "")))

    def _get_selected_project_id(self):
        """Return the project_id of the selected row, or None."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Please select a project first.")
            return None
        return int(self.table.item(row, 0).text())

    def _edit_selected(self):
        project_id = self._get_selected_project_id()
        if project_id is None:
            return
        project = self.controller.get_project_by_id(project_id)
        if project:
            self.form = ProjectFormWindow(
                db=self.db,
                project_to_edit=project,
                refresh_callback=self._load_projects
            )
            self.form.show()

    def _delete_selected(self):
        project_id = self._get_selected_project_id()
        if project_id is None:
            return
        confirm = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this project?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            ok, msg = self.controller.delete_project(project_id)
            if ok:
                QMessageBox.information(self, "Success", msg)
            else:
                QMessageBox.warning(self, "Error", msg)
            self._load_projects()
