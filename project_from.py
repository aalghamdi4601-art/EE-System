# ==========================================
# Project Form View
# ==========================================

import tkinter as tk
from tkinter import messagebox
from controllers.project_controller import ProjectController

class ProjectFormWindow:
    def __init__(self, root, project_to_edit=None, refresh_callback=None):
        self.root = root
        self.project_to_edit = project_to_edit
        self.refresh_callback = refresh_callback
        self.controller = ProjectController()
        
        if self.project_to_edit:
            self.root.title("Edit Project")
        else:
            self.root.title("Add New Project")
        self.root.geometry("400x350")

        tk.Label(root, text="Project Title:", font=("Arial", 10)).pack(pady=5)
        self.entry_title = tk.Entry(root, width=40)
        self.entry_title.pack(pady=5)

        tk.Label(root, text="Project Description:", font=("Arial", 10)).pack(pady=5)
        self.entry_description = tk.Entry(root, width=40)
        self.entry_description.pack(pady=5)

        tk.Label(root, text="Faculty Member ID:", font=("Arial", 10)).pack(pady=5)
        self.entry_faculty = tk.Entry(root, width=40)
        self.entry_faculty.pack(pady=5)

        self.btn_save = tk.Button(root, text="Save Project", font=("Arial", 11, "bold"), bg="green", fg="white", command=self.save_data)
        self.btn_save.pack(pady=20)

        if self.project_to_edit:
            self.entry_title.insert(0, self.project_to_edit.get('title', ''))
            self.entry_description.insert(0, self.project_to_edit.get('description', ''))
            self.entry_faculty.insert(0, self.project_to_edit.get('faculty_id', ''))

    # Save data from form fields
    def save_data(self):
        title = self.entry_title.get()
        description = self.entry_description.get()
        faculty_member = self.entry_faculty.get()

        if self.project_to_edit:
            result = self.controller.update_project(self.project_to_edit.get('project_id'), title, description, faculty_member)
        else:
            result = self.controller.add_project(title, description, faculty_member)

        if "Error" in result:
            messagebox.showerror("Notification", result)
        else:
            messagebox.showinfo("Success", result)
            if self.refresh_callback:
                self.refresh_callback()
            self.controller.close()
            self.root.destroy()
