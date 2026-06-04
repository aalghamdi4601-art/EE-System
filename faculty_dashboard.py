# ==========================================
# Faculty Dashboard View
# ==========================================
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt


class FacultyDashboardWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Faculty Dashboard")
        self.setGeometry(100, 100, 400, 300)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Welcome label
        label = QLabel("Welcome to Project Management")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(label)

        # Add project button
        btn_add = QPushButton("Add New Project")
        btn_add.setFixedHeight(40)
        btn_add.clicked.connect(self.open_add_project_form)
        layout.addWidget(btn_add)

        # Manage projects button
        btn_manage = QPushButton("Manage Projects")
        btn_manage.setFixedHeight(40)
        btn_manage.clicked.connect(self.open_project_list)
        layout.addWidget(btn_manage)

    def open_add_project_form(self):
        from project_form import ProjectFormWindow
        self.form = ProjectFormWindow(self.db)
        self.form.show()

    def open_project_list(self):
        from project_list_view import ProjectListViewWindow
        self.list_view = ProjectListViewWindow(self.db)
        self.list_view.show()
