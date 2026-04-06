# AgentForge Professional GUI Standards (v2.0)

### 1. ARCHITECTURE REQUIREMENTS

- ALWAYS separate the UI layout from the data logic.
- DATA PERSISTENCE: Use JSON or SQLite for saving data.
- Path Handling: Use `os.path.join` for all file paths.

### 2. UI/UX STANDARDS (Tkinter)

- THEME: Use dark mode colors (Bg: #121212, Fg: #FFFFFF, Accent: #00FF00).
- WIDGETS: Use `ttk.Treeview` for tables and `ttk.Style` for a modern look.
- RESPONSIVENESS: Use `pack(fill='both', expand=True)` or `grid` with proper weights.

### 3. FUNCTIONALITY RULES (STRICT)

- **NO PLACEHOLDERS:** Buttons MUST NOT use `print("Ready")`. They must open a dialog or execute a function.
- **INPUT VALIDATION:** Always check if Entry fields are empty before saving.
- **FEEDBACK:** Use `messagebox.showinfo` or `messagebox.showerror` to talk to the user.

### 4. CODE QUALITY

- NO `input()` calls.
- NO hardcoded usernames or local paths.
- Ensure all imports are at the top of the file.
