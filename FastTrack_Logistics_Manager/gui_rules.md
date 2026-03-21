import tkinter as tk
from tkinter import ttk, messagebox
import json, os

class BaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FastTrack Logistics v1.9")
        self.root.geometry("800x600")
        self.data_file = 'data.json'
        self.data = self.load_data()
        self.setup_ui()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return []
        return []

    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def setup_ui(self):
        # Header
        tk.Label(self.root, text="FASTTRACK LOGISTICS", fg='#00ff00', bg='#121212', font=('Arial', 18, 'bold')).pack(pady=20)
        
        # Treeview Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#222222", foreground="white", fieldbackground="#222222", borderwidth=0)
        style.map("Treeview", background=[('selected', '#00ff00')], foreground=[('selected', 'black')])

        # Table
        self.tree = ttk.Treeview(self.root, columns=('ID', 'Sender', 'Receiver', 'Status'), show='headings')
        for col in ('ID', 'Sender', 'Receiver', 'Status'): self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True, padx=20)

        # Controls
        btn_frame = tk.Frame(self.root, bg='#121212')
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="ADD SHIPMENT", fg='white', bg='#333333', width=15, command=lambda: print("Ready")).pack(side='left', padx=10)
        

if __name__ == "__main__":
    root = tk.Tk()
    app = BaseApp(root)
    root.mainloop()