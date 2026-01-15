import os
import sys
import subprocess
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

VENV_DIR = "venv"

def in_venv():
    return sys.prefix != sys.base_prefix

def create_venv():
    subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])

def install_deps():
    pip_path = os.path.join(VENV_DIR, "bin", "pip")
    subprocess.check_call([pip_path, "install", "mysql-connector-python"])

def rerun_in_venv():
    python_path = os.path.join(VENV_DIR, "bin", "python")
    if not os.path.exists(python_path):
        python_path = os.path.join(VENV_DIR, "Scripts", "python.exe")
    os.execv(python_path, [python_path] + sys.argv)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASS", ""),
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci"
}

def get_connection(db_name=None):
    import mysql.connector
    config = DB_CONFIG.copy()
    if db_name:
        config["database"] = db_name
    return mysql.connector.connect(**config)

def setup_database():
    import mysql.connector
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS school")
        cursor.close()
        conn.close()
        
        conn = get_connection("school")
        cursor = conn.cursor()
        
        tables = {
            'classes': """CREATE TABLE IF NOT EXISTS classes (
                class_id INT AUTO_INCREMENT PRIMARY KEY,
                class_name VARCHAR(10) NOT NULL,
                section VARCHAR(10),
                stream VARCHAR(20)
            )""",
            'teachers': """CREATE TABLE IF NOT EXISTS teachers (
                teacher_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                subject_specialization VARCHAR(50),
                email VARCHAR(100)
            )""",
            'subjects': """CREATE TABLE IF NOT EXISTS subjects (
                subject_id INT AUTO_INCREMENT PRIMARY KEY,
                subject_name VARCHAR(50) NOT NULL,
                teacher_id INT,
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
            )""",
            'students': """CREATE TABLE IF NOT EXISTS students (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                dob DATE,
                gender ENUM('Male','Female','Other'),
                class_id INT,
                admission_date DATE,
                FOREIGN KEY (class_id) REFERENCES classes(class_id)
            )""",
            'marks': """CREATE TABLE IF NOT EXISTS marks (
                mark_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                subject_id INT,
                exam_type VARCHAR(20),
                marks_obtained INT,
                max_marks INT,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
            )""",
            'fees': """CREATE TABLE IF NOT EXISTS fees (
                fee_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                total_fee INT,
                paid_fee INT,
                due_fee INT,
                last_payment_date DATE,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )""",
            'attendance': """CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                date DATE,
                status ENUM('Present','Absent'),
                UNIQUE(student_id, date),
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )"""
        }
        
        for table_name, ddl in tables.items():
            cursor.execute(ddl)
            
        cursor.close()
        conn.close()
    except Exception as e:
        sys.exit(1)

class ModernTheme:
    BG_COLOR = "#f0f0f0"
    HEADER_BG = "#2c3e50"
    HEADER_FG = "#ffffff"
    ACCENT_COLOR = "#3498db"
    BUTTON_BG = "#ecf0f1"
    
    @staticmethod
    def apply(root):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure(".", background=ModernTheme.BG_COLOR, font=("Helvetica", 10))
        style.configure("TFrame", background=ModernTheme.BG_COLOR)
        style.configure("TNotebook", background=ModernTheme.BG_COLOR, tabposition='n')
        style.configure("TNotebook.Tab", padding=[12, 8], font=("Helvetica", 11, "bold"))
        style.map("TNotebook.Tab", background=[("selected", ModernTheme.ACCENT_COLOR)], foreground=[("selected", "white")])
        style.configure("Treeview", rowheight=28, font=("Helvetica", 10), background="white", fieldbackground="white")
        style.configure("Treeview.Heading", background=ModernTheme.HEADER_BG, foreground=ModernTheme.HEADER_FG, font=("Helvetica", 10, "bold"), padding=5)
        style.configure("TButton", padding=6, relief="flat", background=ModernTheme.BUTTON_BG, font=("Helvetica", 10))
        style.map("TButton", background=[('active', ModernTheme.ACCENT_COLOR)], foreground=[('active', 'white')])
        style.configure("TLabel", background=ModernTheme.BG_COLOR, font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), foreground=ModernTheme.HEADER_BG)

class SchoolDBApp:
    def __init__(self, root):
        self.root = root
        self.root.title("School Management Pro")
        self.root.geometry("1100x750")
        
        ModernTheme.apply(root)
        
        header_frame = tk.Frame(root, bg=ModernTheme.HEADER_BG, height=60)
        header_frame.pack(fill='x')
        tk.Label(header_frame, text="School Management System", bg=ModernTheme.HEADER_BG, fg="white", font=("Helvetica", 18, "bold")).pack(side='left', padx=20, pady=15)
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_students = ttk.Frame(self.notebook)
        self.tab_teachers = ttk.Frame(self.notebook)
        self.tab_marks = ttk.Frame(self.notebook)
        self.tab_attendance = ttk.Frame(self.notebook)
        self.tab_fees = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_dashboard, text=' Dashboard ')
        self.notebook.add(self.tab_students, text=' Students ')
        self.notebook.add(self.tab_teachers, text=' Teachers ')
        self.notebook.add(self.tab_marks, text=' Marks ')
        self.notebook.add(self.tab_attendance, text=' Attendance ')
        self.notebook.add(self.tab_fees, text=' Fees ')
        
        self.setup_dashboard()
        self.setup_students()
        self.setup_teachers()
        self.setup_marks()
        self.setup_attendance()
        self.setup_fees()
        
        self.refresh_dashboard()

    def run_query(self, query, params=(), fetch=True, commit=False):
        try:
            conn = get_connection("school")
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            result = None
            if fetch:
                result = cursor.fetchall()
            if commit:
                conn.commit()
                
            conn.close()
            return result
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return None

    def setup_dashboard(self):
        self.dash_frame = ttk.Frame(self.tab_dashboard, padding=20)
        self.dash_frame.pack(fill='both', expand=True)
        
        ttk.Label(self.dash_frame, text="Overview", style="Header.TLabel").pack(anchor='w', pady=(0, 20))
        
        cards_frame = ttk.Frame(self.dash_frame)
        cards_frame.pack(fill='x')
        
        self.card_student = self.create_card(cards_frame, "Total Students", "0", 0)
        self.card_teacher = self.create_card(cards_frame, "Total Teachers", "0", 1)
        self.card_classes = self.create_card(cards_frame, "Total Classes", "0", 2)
        
        ttk.Separator(self.dash_frame, orient='horizontal').pack(fill='x', pady=30)
        ttk.Button(self.dash_frame, text="Refresh Dashboard", command=self.refresh_dashboard).pack(anchor='w')

    def create_card(self, parent, title, value, col):
        frame = tk.Frame(parent, bg="white", highlightbackground="#ccc", highlightthickness=1, padx=20, pady=20)
        frame.grid(row=0, column=col, sticky='ew', padx=10)
        parent.grid_columnconfigure(col, weight=1)
        
        tk.Label(frame, text=title, bg="white", fg="#7f8c8d", font=("Helvetica", 12)).pack(anchor='w')
        val_lbl = tk.Label(frame, text=value, bg="white", fg="#2c3e50", font=("Helvetica", 24, "bold"))
        val_lbl.pack(anchor='w')
        return val_lbl

    def refresh_dashboard(self):
        res = self.run_query("SELECT COUNT(*) FROM students")
        if res: self.card_student.config(text=str(res[0][0]))
        res = self.run_query("SELECT COUNT(*) FROM teachers")
        if res: self.card_teacher.config(text=str(res[0][0]))
        res = self.run_query("SELECT COUNT(*) FROM classes")
        if res: self.card_classes.config(text=str(res[0][0]))

    def setup_students(self):
        controls = ttk.Frame(self.tab_students, padding=10)
        controls.pack(fill='x')
        ttk.Button(controls, text="Add New Student", command=self.add_student_dialog).pack(side='left')
        ttk.Button(controls, text="Delete Selected", command=self.delete_student).pack(side='right')
        
        cols = ('ID', 'Name', 'Gender', 'Class', 'Section', 'Stream')
        self.tree_students = ttk.Treeview(self.tab_students, columns=cols, show='headings')
        for col in cols:
            self.tree_students.heading(col, text=col)
            self.tree_students.column(col, width=100)
            
        self.tree_students.pack(fill='both', expand=True, padx=10, pady=10)
        self.load_students()
        
    def load_students(self):
        for item in self.tree_students.get_children():
            self.tree_students.delete(item)
        rows = self.run_query("""
            SELECT s.student_id, s.name, s.gender, c.class_name, c.section, c.stream 
            FROM students s 
            LEFT JOIN classes c ON s.class_id = c.class_id
            ORDER BY s.student_id
        """)
        if rows:
            for r in rows:
                vals = [x if x is not None else "-" for x in r]
                self.tree_students.insert('', 'end', values=vals)

    def add_student_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add Student")
        win.geometry("400x450")
        
        ttk.Label(win, text="Full Name").pack(pady=5)
        ent_name = ttk.Entry(win)
        ent_name.pack(pady=5)
        ttk.Label(win, text="DOB (YYYY-MM-DD)").pack(pady=5)
        ent_dob = ttk.Entry(win)
        ent_dob.pack(pady=5)
        ttk.Label(win, text="Gender").pack(pady=5)
        cbo_gender = ttk.Combobox(win, values=["Male", "Female", "Other"])
        cbo_gender.pack(pady=5)
        ttk.Label(win, text="Class").pack(pady=5)
        cbo_class = ttk.Combobox(win)
        cbo_class.pack(pady=5)
        
        classes = self.run_query("SELECT class_id, class_name, section, stream FROM classes")
        cls_map = {}
        if classes:
            for c in classes:
                lbl = f"{c[1]} {c[2] or ''} ({c[3] or 'Gen'})"
                cls_map[lbl] = c[0]
            cbo_class['values'] = list(cls_map.keys())
            
        def save():
            name = ent_name.get()
            dob = ent_dob.get()
            gender = cbo_gender.get()
            cls = cbo_class.get()
            if not name or not cls: return
            self.run_query(
                "INSERT INTO students (name, dob, gender, class_id, admission_date) VALUES (%s, %s, %s, %s, %s)",
                (name, dob, gender, cls_map[cls], date.today()),
                commit=True, fetch=False
            )
            self.load_students()
            self.refresh_dashboard()
            win.destroy()

        ttk.Button(win, text="Save", command=save).pack(pady=20)

    def delete_student(self):
        sel = self.tree_students.selection()
        if not sel: return
        sid = self.tree_students.item(sel[0])['values'][0]
        try:
            conn = get_connection("school")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM marks WHERE student_id = %s", (sid,))
            cursor.execute("DELETE FROM attendance WHERE student_id = %s", (sid,))
            cursor.execute("DELETE FROM fees WHERE student_id = %s", (sid,))
            cursor.execute("DELETE FROM students WHERE student_id = %s", (sid,))
            conn.commit()
            conn.close()
            self.load_students()
            self.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def setup_teachers(self):
        controls = ttk.Frame(self.tab_teachers, padding=10)
        controls.pack(fill='x')
        ttk.Button(controls, text="Add Teacher", command=self.add_teacher_dialog).pack(side='left')
        
        cols = ('ID', 'Name', 'Subject', 'Email')
        self.tree_teachers = ttk.Treeview(self.tab_teachers, columns=cols, show='headings')
        for col in cols: self.tree_teachers.heading(col, text=col)
        self.tree_teachers.pack(fill='both', expand=True, padx=10, pady=10)
        self.load_teachers()

    def load_teachers(self):
        for i in self.tree_teachers.get_children(): self.tree_teachers.delete(i)
        rows = self.run_query("SELECT teacher_id, name, subject_specialization, email FROM teachers")
        if rows:
            for r in rows: self.tree_teachers.insert('', 'end', values=r)

    def add_teacher_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add Teacher")
        win.geometry("300x350")
        fields = ["Name", "Subject", "Email"]
        entries = {}
        for f in fields:
            ttk.Label(win, text=f).pack(pady=5)
            entries[f] = ttk.Entry(win)
            entries[f].pack(pady=5)
        def save():
            v = [entries[f].get() for f in fields]
            if not v[0]: return
            self.run_query("INSERT INTO teachers (name, subject_specialization, email) VALUES (%s, %s, %s)", tuple(v), commit=True, fetch=False)
            self.load_teachers()
            self.refresh_dashboard()
            win.destroy()
        ttk.Button(win, text="Save", command=save).pack(pady=20)

    def setup_marks(self):
        controls = ttk.Frame(self.tab_marks, padding=10)
        controls.pack(fill='x')
        ttk.Button(controls, text="Add Marks", command=self.add_marks_dialog).pack(side='left')
        ttk.Button(controls, text="Refresh", command=self.load_marks).pack(side='left', padx=5)
        cols = ('Student', 'Class', 'Subject', 'Exam', 'Marks', 'Max')
        self.tree_marks = ttk.Treeview(self.tab_marks, columns=cols, show='headings')
        for col in cols: self.tree_marks.heading(col, text=col)
        self.tree_marks.pack(fill='both', expand=True, padx=10, pady=10)
        self.load_marks()

    def load_marks(self):
        for i in self.tree_marks.get_children(): self.tree_marks.delete(i)
        rows = self.run_query("""
            SELECT s.name, CONCAT(c.class_name, c.section), sub.subject_name, m.exam_type, m.marks_obtained, m.max_marks
            FROM marks m
            JOIN students s ON m.student_id = s.student_id
            JOIN classes c ON s.class_id = c.class_id
            JOIN subjects sub ON m.subject_id = sub.subject_id
            ORDER BY m.mark_id DESC LIMIT 100
        """)
        if rows:
            for r in rows: self.tree_marks.insert('', 'end', values=r)

    def add_marks_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Enter Marks")
        win.geometry("400x500")
        ttk.Label(win, text="Select Student").pack(pady=5)
        cbo_student = ttk.Combobox(win)
        cbo_student.pack(pady=5)
        st_rows = self.run_query("SELECT student_id, name FROM students ORDER BY name")
        st_map = {f"{r[1]} (ID: {r[0]})": r[0] for r in st_rows or []}
        cbo_student['values'] = list(st_map.keys())
        ttk.Label(win, text="Select Subject").pack(pady=5)
        cbo_sub = ttk.Combobox(win)
        cbo_sub.pack(pady=5)
        sub_rows = self.run_query("SELECT subject_id, subject_name FROM subjects ORDER BY subject_name")
        sub_map = {r[1]: r[0] for r in sub_rows or []}
        cbo_sub['values'] = list(sub_map.keys())
        ttk.Label(win, text="Exam Type").pack(pady=5)
        ent_exam = ttk.Entry(win)
        ent_exam.pack(pady=5)
        ttk.Label(win, text="Marks Obtained").pack(pady=5)
        ent_obt = ttk.Entry(win)
        ent_obt.pack(pady=5)
        ttk.Label(win, text="Max Marks").pack(pady=5)
        ent_max = ttk.Entry(win)
        ent_max.insert(0, "100")
        ent_max.pack(pady=5)
        def save():
            s_label = cbo_student.get()
            sub_label = cbo_sub.get()
            if not s_label or not sub_label: return
            sid, subid = st_map[s_label], sub_map[sub_label]
            self.run_query("INSERT INTO marks (student_id, subject_id, exam_type, marks_obtained, max_marks) VALUES (%s, %s, %s, %s, %s)", (sid, subid, ent_exam.get(), ent_obt.get(), ent_max.get()), commit=True, fetch=False)
            self.load_marks()
            win.destroy()
        ttk.Button(win, text="Save", command=save).pack(pady=20)

    def setup_attendance(self):
        nb = ttk.Notebook(self.tab_attendance)
        nb.pack(fill='both', expand=True)
        f_mark, f_view = ttk.Frame(nb), ttk.Frame(nb)
        nb.add(f_mark, text="Mark Attendance")
        nb.add(f_view, text="View Logs")
        ctrl = ttk.Frame(f_mark, padding=10)
        ctrl.pack(fill='x')
        ttk.Label(ctrl, text="Date:").pack(side='left')
        ent_date = ttk.Entry(ctrl)
        ent_date.insert(0, str(date.today()))
        ent_date.pack(side='left', padx=5)
        status_vars = {}
        def load_class_list():
            for w in scroll_frame.winfo_children(): w.destroy()
            status_vars.clear()
            rows = self.run_query("SELECT s.student_id, s.name, c.class_name FROM students s JOIN classes c ON s.class_id=c.class_id ORDER BY c.class_name, s.name")
            if not rows: return
            for i, r in enumerate(rows):
                sid, name, cl = r
                ttk.Label(scroll_frame, text=f"{cl} - {name}").grid(row=i, column=0, sticky='w', padx=10, pady=2)
                var = tk.StringVar(value="Present")
                ttk.Combobox(scroll_frame, textvariable=var, values=["Present", "Absent"], width=8, state='readonly').grid(row=i, column=1, padx=10)
                status_vars[sid] = var
        ttk.Button(ctrl, text="Load Students", command=load_class_list).pack(side='left')
        canvas = tk.Canvas(f_mark)
        scr = ttk.Scrollbar(f_mark, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scr.set)
        canvas.pack(side="left", fill="both", expand=True)
        scr.pack(side="right", fill="y")
        def submit_att():
            dt = ent_date.get()
            data = [(sid, dt, var.get()) for sid, var in status_vars.items()]
            if not data: return
            try:
                conn = get_connection("school")
                cursor = conn.cursor()
                cursor.executemany("INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE status=VALUES(status)", data)
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Attendance Marked")
            except Exception as e: messagebox.showerror("Error", str(e))
        ttk.Button(ctrl, text="Submit Attendance", command=submit_att).pack(side='right')
        v_ctrl = ttk.Frame(f_view, padding=10)
        v_ctrl.pack(fill='x')
        v_ent = ttk.Entry(v_ctrl)
        v_ent.insert(0, str(date.today()))
        v_ent.pack(side='left')
        cols_v = ('Name', 'Class', 'Status')
        tree_att = ttk.Treeview(f_view, columns=cols_v, show='headings')
        for c in cols_v: tree_att.heading(c, text=c)
        tree_att.pack(fill='both', expand=True, padx=10, pady=10)
        def load_view():
            for i in tree_att.get_children(): tree_att.delete(i)
            rows = self.run_query("""
                SELECT s.name, CONCAT(c.class_name, c.section), COALESCE(a.status, 'N/A')
                FROM students s JOIN classes c ON s.class_id = c.class_id
                LEFT JOIN attendance a ON s.student_id = a.student_id AND a.date = %s
                ORDER BY c.class_name
            """, (v_ent.get(),))
            if rows:
                for r in rows: tree_att.insert('', 'end', values=r)
        ttk.Button(v_ctrl, text="View Report", command=load_view).pack(side='left', padx=5)

    def setup_fees(self):
        cols = ('ID', 'Student', 'Total', 'Paid', 'Due', 'Last Payment')
        self.tree_fees = ttk.Treeview(self.tab_fees, columns=cols, show='headings')
        for c in cols: self.tree_fees.heading(c, text=c)
        self.tree_fees.pack(fill='both', expand=True, padx=10, pady=10)
        frame_act = ttk.Frame(self.tab_fees, padding=10)
        frame_act.pack(fill='x')
        ttk.Button(frame_act, text="Refresh", command=self.load_fees).pack(side='right')
        ttk.Button(frame_act, text="Update Payment", command=self.update_fee_dialog).pack(side='right', padx=5)
        self.load_fees()

    def load_fees(self):
        for i in self.tree_fees.get_children(): self.tree_fees.delete(i)
        rows = self.run_query("SELECT f.fee_id, s.name, f.total_fee, f.paid_fee, f.due_fee, f.last_payment_date FROM fees f JOIN students s ON f.student_id = s.student_id")
        if rows:
            for r in rows: self.tree_fees.insert('', 'end', values=r)

    def update_fee_dialog(self):
        sel = self.tree_fees.selection()
        if not sel: return
        item = self.tree_fees.item(sel[0])['values']
        fee_id, name, total, paid, due, last = item
        win = tk.Toplevel(self.root)
        win.title(f"Update Fees: {name}")
        win.geometry("300x250")
        ttk.Label(win, text=f"Total: {total} | Paid: {paid}").pack(pady=10)
        ttk.Label(win, text="Payment Amount:").pack(pady=5)
        ent_pay = ttk.Entry(win)
        ent_pay.pack(pady=5)
        def save():
            amt = int(ent_pay.get())
            new_paid = paid + amt
            self.run_query("UPDATE fees SET paid_fee=%s, due_fee=%s, last_payment_date=%s WHERE fee_id=%s", (new_paid, total - new_paid, date.today(), fee_id), commit=True, fetch=False)
            self.load_fees()
            win.destroy()
        ttk.Button(win, text="Process Payment", command=save).pack(pady=15)

if __name__ == "__main__":
    if not os.path.exists(VENV_DIR):
        create_venv()
        install_deps()
        rerun_in_venv()
    if not in_venv(): rerun_in_venv()
    if tk is None: sys.exit(1)
    setup_database()
    root = tk.Tk()
    app = SchoolDBApp(root)
    root.mainloop()
