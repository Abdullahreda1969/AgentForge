import tkinter as tk
from tkinter import messagebox
import json
import os

class TodoListApp:
    def __init__(self, master):
        self.master = master
        master.title("TaskMaster Pro v1.0")
        master.geometry("400x500")

        self.tasks = []
        self.file_path = 'tasks.json'
        self.load_tasks_from_file()

        # --- واجهة الإدخال ---
        self.entry_task = tk.Entry(master, font=("Arial", 12), width=30)
        self.entry_task.pack(pady=10)

        self.add_button = tk.Button(master, text="➕ Add Task", command=self.add_task, bg="#4CAF50", fg="white")
        self.add_button.pack(pady=5)

        # --- قائمة المهام ---
        self.task_listbox = tk.Listbox(master, width=50, height=15, font=("Arial", 11))
        self.task_listbox.pack(pady=10, padx=10)

        # --- أزرار التحكم ---
        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=5)

        self.complete_button = tk.Button(btn_frame, text="✔️ Complete", command=self.mark_complete)
        self.complete_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(btn_frame, text="🗑️ Delete", command=self.delete_task, bg="#f44336", fg="white")
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.update_task_list()

    def load_tasks_from_file(self):
        """تحميل المهام من ملف JSON"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = []

    def save_tasks_to_file(self):
        """حفظ المهام في ملف JSON"""
        with open(self.file_path, 'w') as f:
            json.dump(self.tasks, f)

    def add_task(self):
        task_text = self.entry_task.get()
        if task_text != "":
            self.tasks.append({"text": task_text, "status": "Pending"})
            self.entry_task.delete(0, tk.END)
            self.update_task_list()
            self.save_tasks_to_file()
        else:
            messagebox.showwarning("Warning", "You must enter a task!")

    def update_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            display_text = f"[{task['status']}] {task['text']}"
            self.task_listbox.insert(tk.END, display_text)

    def delete_task(self):
        try:
            index = self.task_listbox.curselection()[0]
            del self.tasks[index]
            self.update_task_list()
            self.save_tasks_to_file()
        except IndexError:
            messagebox.showwarning("Warning", "Select a task to delete!")

    def mark_complete(self):
        try:
            index = self.task_listbox.curselection()[0]
            self.tasks[index]["status"] = "Completed"
            self.update_task_list()
            self.save_tasks_to_file()
        except IndexError:
            messagebox.showwarning("Warning", "Select a task!")

    def run(self):
        self.master.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoListApp(root)
    app.run()
    