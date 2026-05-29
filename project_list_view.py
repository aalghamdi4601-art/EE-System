# ==========================================
# Project List View
# ==========================================

import tkinter as tk
from tkinter import messagebox, ttk
from controllers.project_controller import ProjectController
from views.project_form import ProjectFormWindow

class ProjectListViewWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Project List")
        self.root.geometry("600x400")
        self.controller = ProjectController()

        columns = ("id", "title", "description", "faculty")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        self.tree.heading("id", text="Project ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("description", text="Description")
        self.tree.heading("faculty", text="Faculty ID")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.btn_edit = tk.Button(btn_frame, text="Edit Selected", bg="orange", font=("Arial", 10), command=self.edit_selected_project)
        self.btn_edit.pack(side=tk.LEFT, padx=10)

        self.btn_delete = tk.Button(btn_frame, text="Delete Selected", bg="red", fg="white", font=("Arial", 10), command=self.delete_selected_project)
        self.btn_delete.pack(side=tk.LEFT, padx=10)

        self.load_projects_data()

    # Load data into table
    def load_projects_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        all_projects = self.controller.get_all_projects()
        for project in all_projects:
            self.tree.insert("", tk.END, values=(project.get('project_id'), project.get('title'), project.get('description'), project.get('faculty_id')))

    # Edit selected project row
    def edit_selected_project(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a project!")
            return
        project_id = self.tree.item(selected_item)['values'][0]
        project_to_edit = self.controller.get_project_by_id(project_id)
        if project_to_edit:
            edit_window = tk.Toplevel(self.root)
            ProjectFormWindow(edit_window, project_to_edit=project_to_edit, refresh_callback=self.load_projects_data)

    # Delete selected project row
    def delete_selected_project(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a project!")
            return
        project_id = self.tree.item(selected_item)['values'][0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure?")
        if confirm:
            result = self.controller.delete_project(project_id)
            messagebox.showinfo("Result", result)
            self.load_projects_data()
