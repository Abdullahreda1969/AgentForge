import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class ShippingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AgentForge: FastTrack Logistics Manager v1.9")
        self.root.geometry("900x600")
        self.root.configure(bg='#121212')
        
        # 1. تهيئة البيانات
        self.data_file = 'data.json'
        self.data = self.load_data()
        
        # 2. بناء الواجهة
        self.setup_ui()
        self.refresh_table()

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
        # العنوان العلوي
        header = tk.Label(self.root, text="FASTTRACK LOGISTICS SYSTEM", 
                         fg='#00ff00', bg='#121212', font=('Segoe UI', 20, 'bold'))
        header.pack(pady=20)

        # منطقة المدخلات
        input_frame = tk.Frame(self.root, bg='#121212')
        input_frame.pack(pady=10, fill='x', padx=50)

        tk.Label(input_frame, text="Customer Name:", fg='white', bg='#121212').grid(row=0, column=0, padx=5)
        self.ent_name = tk.Entry(input_frame, bg='#222222', fg='white', insertbackground='white')
        self.ent_name.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Tracking ID:", fg='white', bg='#121212').grid(row=0, column=2, padx=5)
        self.ent_id = tk.Entry(input_frame, bg='#222222', fg='white', insertbackground='white')
        self.ent_id.grid(row=0, column=3, padx=5)

        # الجدول (Treeview)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e", borderwidth=0)
        style.configure("Treeview.Heading", background="#333333", foreground="#00ff00", relief="flat")
        style.map("Treeview", background=[('selected', '#00ff00')], foreground=[('selected', 'black')])

        self.tree = ttk.Treeview(self.root, columns=('ID', 'Customer', 'Status'), show='headings')
        self.tree.heading('ID', text='TRACKING ID')
        self.tree.heading('Customer', text='CUSTOMER NAME')
        self.tree.heading('Status', text='STATUS')
        self.tree.pack(fill='both', expand=True, padx=50, pady=20)

        # الأزرار
        btn_frame = tk.Frame(self.root, bg='#121212')
        btn_frame.pack(pady=20)

        add_btn = tk.Button(btn_frame, text="➕ ADD SHIPMENT", bg='#00ff00', fg='black', 
                           font=('Arial', 10, 'bold'), width=20, command=self.add_shipment)
        add_btn.pack(side='left', padx=10)

        del_btn = tk.Button(btn_frame, text="🗑️ DELETE SELECTED", bg='#ff4444', fg='white', 
                           font=('Arial', 10, 'bold'), width=20, command=self.delete_shipment)
        del_btn.pack(side='left', padx=10)

    def add_shipment(self):
        name = self.ent_name.get()
        tid = self.ent_id.get()
        if name and tid:
            self.data.append({"id": tid, "customer": name, "status": "Pending"})
            self.save_data()
            self.refresh_table()
            self.ent_name.delete(0, tk.END); self.ent_id.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please fill all fields!")

    def delete_shipment(self):
        selected = self.tree.selection()
        if selected:
            for item in selected:
                item_val = self.tree.item(item)['values'][0]
                self.data = [d for d in self.data if str(d['id']) != str(item_val)]
            self.save_data()
            self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        for item in self.data:
            self.tree.insert('', 'end', values=(item['id'], item['customer'], item['status']))

if __name__ == "__main__":
    root = tk.Tk()
    app = ShippingApp(root)
    root.mainloop()