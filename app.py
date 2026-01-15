import os
import sys
import subprocess
from datetime import date

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
    from mysql.connector import Error
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS school")
        cursor.close()
        conn.close()
        
        conn = get_connection("school")
        cursor = conn.cursor()
        
        tables = {}
        
        tables['classes'] = """
        CREATE TABLE IF NOT EXISTS classes (
            class_id INT AUTO_INCREMENT PRIMARY KEY,
            class_name VARCHAR(10) NOT NULL,
            section VARCHAR(10),
            stream VARCHAR(20)
        )
        """
        
        tables['teachers'] = """
        CREATE TABLE IF NOT EXISTS teachers (
            teacher_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            subject_specialization VARCHAR(50),
            email VARCHAR(100)
        )
        """
        
        tables['subjects'] = """
        CREATE TABLE IF NOT EXISTS subjects (
            subject_id INT AUTO_INCREMENT PRIMARY KEY,
            subject_name VARCHAR(50) NOT NULL,
            teacher_id INT,
            FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
        )
        """
        
        tables['students'] = """
        CREATE TABLE IF NOT EXISTS students (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            dob DATE,
            gender ENUM('Male','Female','Other'),
            class_id INT,
            admission_date DATE,
            FOREIGN KEY (class_id) REFERENCES classes(class_id)
        )
        """
        
        tables['marks'] = """
        CREATE TABLE IF NOT EXISTS marks (
            mark_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
            subject_id INT,
            exam_type VARCHAR(20),
            marks_obtained INT,
            max_marks INT,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
        )
        """
        
        tables['fees'] = """
        CREATE TABLE IF NOT EXISTS fees (
            fee_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
            total_fee INT,
            paid_fee INT,
            due_fee INT,
            last_payment_date DATE,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """
        
        tables['attendance'] = """
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
            date DATE,
            status ENUM('Present','Absent'),
            UNIQUE(student_id, date),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """
        
        for table_name, ddl in tables.items():
            cursor.execute(ddl)
            
        cursor.close()
        conn.close()
        
    except Error as e:
        sys.exit(1)

def view_students():
    from mysql.connector import Error
    try:
        conn = get_connection("school")
        cursor = conn.cursor()
        query = """
        SELECT s.student_id, s.name, s.gender, c.class_name, c.section, c.stream
        FROM students s
        JOIN classes c ON s.class_id = c.class_id
        ORDER BY s.student_id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print("\nStudent Records:")
        print(f"{'ID':<5} {'Name':<20} {'Gender':<10} {'Class':<10} {'Section':<10} {'Stream':<15}")
        print("-" * 75)
        for row in rows:
            cls = row[3]
            sec = row[4] if row[4] else "-"
            strm = row[5] if row[5] else "-"
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<10} {cls:<10} {sec:<10} {strm:<15}")
            
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error: {e}")

def add_student():
    from mysql.connector import Error
    try:
        conn = get_connection("school")
        cursor = conn.cursor()
        
        print("\nAdd New Student")
        name = input("Enter Name: ")
        dob = input("Enter DOB (YYYY-MM-DD): ")
        gender = input("Enter Gender (Male/Female/Other): ")
        
        cursor.execute("SELECT class_id, class_name, section, stream FROM classes")
        classes = cursor.fetchall()
        for c in classes:
            strm = f"({c[3]})" if c[3] else ""
            sec = f"Sec: {c[2]}" if c[2] else ""
            print(f"{c[0]}: Class {c[1]} {sec} {strm}")
            
        class_id = input("Enter Class ID: ")
        admission_date = date.today()
        
        query = "INSERT INTO students (name, dob, gender, class_id, admission_date) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (name, dob, gender, class_id, admission_date))
        conn.commit()
        
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error: {e}")

def add_marks():
    from mysql.connector import Error
    try:
        conn = get_connection("school")
        cursor = conn.cursor()
        
        cursor.execute("SELECT student_id, name FROM students") 
        students = cursor.fetchall()
        for s in students:
            print(f"{s[0]}: {s[1]}")
        student_id = input("Enter Student ID: ")
        
        cursor.execute("SELECT subject_id, subject_name FROM subjects")
        subjects = cursor.fetchall()
        for s in subjects:
            print(f"{s[0]}: {s[1]}")
        subject_id = input("Enter Subject ID: ")
        
        exam_type = input("Enter Exam Type (e.g., Midterm, Final): ")
        marks = input("Enter Marks Obtained: ")
        max_marks = input("Enter Max Marks: ")
        
        query = "INSERT INTO marks (student_id, subject_id, exam_type, marks_obtained, max_marks) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (student_id, subject_id, exam_type, marks, max_marks))
        conn.commit()
        
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error: {e}")

def view_marks():
    from mysql.connector import Error
    try:
        conn = get_connection("school")
        cursor = conn.cursor()
        
        student_id = input("Enter Student ID to view (or Press Enter for all): ")
        
        query = """
        SELECT s.name, sub.subject_name, m.exam_type, m.marks_obtained, m.max_marks
        FROM marks m
        JOIN students s ON m.student_id = s.student_id
        JOIN subjects sub ON m.subject_id = sub.subject_id
        """
        
        if student_id:
            query += f" WHERE m.student_id = {student_id}"
            
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"\n{'Student':<20} {'Subject':<15} {'Exam':<10} {'Marks':<10}")
        print("-" * 60)
        for row in rows:
            print(f"{row[0]:<20} {row[1]:<15} {row[2]:<10} {row[3]}/{row[4]}")
            
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error: {e}")

def mark_attendance():
    from mysql.connector import Error
    try:
        conn = get_connection("school")
        cursor = conn.cursor()
        
        att_date = input(f"Enter Date (YYYY-MM-DD, default today {date.today()}): ")
        if not att_date:
            att_date = date.today()
            
        cursor.execute("SELECT student_id, name FROM students")
        students = cursor.fetchall()
        
        inserts = []
        for s in students:
            status = input(f"{s[1]} (ID: {s[0]}): ").upper()
            status_val = "Present" if status == 'P' else "Absent"
            inserts.append((s[0], att_date, status_val))
            
        query = """
        INSERT INTO attendance (student_id, date, status) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE status = VALUES(status)
        """
        cursor.executemany(query, inserts)
        conn.commit()
        
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error: {e}")

def view_attendance():
    from mysql.connector import Error
    try:
        conn = get_connection("school")
        cursor = conn.cursor()
        
        print("1. View by Student")
        print("2. View by Date")
        choice = input("Enter Choice: ")
        
        if choice == '1':
            sid = input("Enter Student ID (or Enter for all): ")
            query = """
            SELECT a.date, s.name, a.status 
            FROM attendance a 
            JOIN students s ON a.student_id = s.student_id
            WHERE 1=1
            """
            if sid:
                query += f" AND a.student_id = {sid}"
            query += " ORDER BY a.date DESC LIMIT 50"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            print(f"\n{'Date':<12} {'Name':<20} {'Status':<10}")
            print("-" * 45)
            for row in rows:
                print(f"{str(row[0]):<12} {row[1]:<20} {row[2]:<10}")
                
        elif choice == '2':
            dt = input("Enter Date (YYYY-MM-DD): ")
            query = """
            SELECT s.student_id, s.name, c.class_name, c.section, a.status
            FROM students s
            JOIN classes c ON s.class_id = c.class_id
            LEFT JOIN attendance a ON s.student_id = a.student_id AND a.date = %s
            ORDER BY c.class_name, s.name
            """
            cursor.execute(query, (dt,))
            rows = cursor.fetchall()
            
            for row in rows:
                cls = f"{row[2]}{row[3] if row[3] else ''}"
                status = row[4] if row[4] else "N/A"
                print(f"{row[0]:<5} {row[1]:<20} {cls:<10} {status:<10}")

        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error: {e}")

def menu():
    setup_database()
    
    while True:
        print("\nSCHOOL MANAGEMENT SYSTEM")
        print("1. View Student Records")
        print("2. Add New Student")
        print("3. Add Marks")
        print("4. View Marks")
        print("5. Mark Daily Attendance")
        print("6. View Attendance Log")
        print("7. Exit")
        
        choice = input("\nEnter Choice (1-7): ")
        
        if choice == '1':
            view_students()
        elif choice == '2':
            add_student()
        elif choice == '3':
            add_marks()
        elif choice == '4':
            view_marks()
        elif choice == '5':
            mark_attendance()
        elif choice == '6':
            view_attendance()
        elif choice == '7':
            break

if __name__ == "__main__":
    if not os.path.exists(VENV_DIR):
        create_venv()
        install_deps()
        rerun_in_venv()
    
    if not in_venv():
        rerun_in_venv()

    try:
        import mysql.connector
        from mysql.connector import Error
        menu()
    except ImportError:
        sys.exit(1)
