# School Management System

A comprehensive student and school record management system with both Command-Line Interface (CLI) and Graphical User Interface (GUI) versions. This project allows for managing student records, teachers, marks, attendance, and fee status using a MySQL backend.

## Features

- **Dual Modes**: 
  - `app.py`: Interactive CLI for terminal usage.
  - `gui_app.py`: Modern Tkinter-based GUI with a dashboard and multi-tab navigation.
- **Dashboard**: Live stats for total students, teachers, and classes.
- **Student Management**: Full record management including admission details and class assignment.
- **Attendance Tracking**: Mark daily attendance with a class-wise checklist and view historical logs.
- **Academics**: Record exam marks for various subjects and view student performance.
- **Finance**: Track fee payments, total dues, and update payment records.
- **Auto-Environment**: Automatically sets up a Python virtual environment and installs required dependencies on the first run.

## Prerequisites

- **Python 3.x**
- **MySQL Server**: Ensure MySQL is running on your machine.
- **Tkinter**: (For GUI) 
  - macOS: `brew install python-tk`
  - Linux: `sudo apt-get install python3-tk`

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ruthwwikreddy/studentdb.git
   cd studentdb
   ```

2. **Configure Database**:
   The application connects to MySQL using the following environment variables (defaults are in brackets):
   - `DB_HOST` (localhost)
   - `DB_USER` (root)
   - `DB_PASS` (empty string)

   Example to set your password on macOS/Linux:
   ```bash
   export DB_PASS="your_password_here"
   ```

3. **Run the Application**:
   - **For CLI version**:
     ```bash
     python3 app.py
     ```
   - **For GUI version**:
     ```bash
     python3 gui_app.py
     ```

## Database Schema

The system automatically creates a `school` database with the following tables:
- `classes`: Grade, section, and stream details.
- `teachers`: Teacher names and specializations.
- `subjects`: Academic subjects linked to teachers.
- `students`: Central student records.
- `marks`: Exam results record.
- `fees`: Tuition fee status and history.
- `attendance`: Daily presence/absence log.

## License

This project is for educational purposes.
