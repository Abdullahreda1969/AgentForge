import tkinter as tk
import json
import os

def load_tasks():
    global tasks
    if os.path.exists("tasks.json"):
        # فحص حجم الملف: إذا كان صفراً، نعتبر القائمة فارغة
        if os.path.getsize("tasks.json") == 0:
            tasks = []
            return
        
        with open("tasks.json", "r", encoding="utf-8") as f:
            try:
                tasks = json.load(f)
            except json.JSONDecodeError:
                # إذا كان الملف تالفاً أو فارغاً، ابدأ بقائمة فارغة
                tasks = []
    else:
        tasks = []

def add_item(entry):
    task = entry.get()
    tasks.append(task)
    entry.delete(0, tk.END)
    listbox.insert(0, task)

def update_listbox(tasks):
    listbox.delete(0, tk.END)
    for task in tasks:
        listbox.insert(0, task)

if __name__ == "__main__":
    load_tasks()
    add_item(entry)
    update_listbox(tasks)