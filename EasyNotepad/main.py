import tkinter as tk
from tkinter import filedialog
import pandas as pd
import requests

def write_to_file():
    try:
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "w") as file:
                    file.write("This is some text written by the Python script.")
                print(f"File saved to: {file_path}")
            except Exception as e:
                print(f"Error writing to file: {e}")
    except Exception as e:
        print(f"Error opening file dialog: {e}")

def main():
    root = tk.Tk()
    root.title("Text File Writer")

    button = tk.Button(root, text="Write to File", command=write_to_file)
    button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()