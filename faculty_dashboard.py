# ==========================================
# Faculty Dashboard View
# ==========================================

import tkinter as tk
from views.project_form import ProjectFormWindow
from views.project_list_view import ProjectListViewWindow

class FacultyDashboardWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Faculty Dashboard")
        self.root.geometry("400x300")

        self.label_welcome = tk.Label(root, text="Welcome to Project Management", font=("Arial", 14, "bold"))
        self.label_welcome.pack(pady=20)

        self.btn_add_project = tk.Button(root, text="Add New Project", font=("Arial", 11), width=25, command=self.open_add_project_form)
        self.btn_add_project.pack(pady=10)

        self.btn_view_projects = tk.Button(root, text="Manage Projects", font=("Arial", 11), width=25, command=self.open_project_list)
        self.btn_view_projects.pack(pady=10)

    # Open add form window
    def open_add_project_form(self):
        form_window = tk.Toplevel(self.root)
        ProjectFormWindow(form_window)

    # Open project list window
    def open_project_list(self):
        list_window = tk.Toplevel(self.root)
        ProjectListViewWindow(list_window)
