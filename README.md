# School Management System (My IP Project)

Hey! This is a simple School Management System I made for our database project. It helps keep track of everything in a school like students, marks, and attendance without using bulky registers.

## What it does:
*   **Two ways to use it**: You can run it in the simple terminal (`app.py`) or use the cool window version (`gui_app.py`) with buttons and tabs.
*   **Dashboard**: Shows how many students and teachers are in the school right now.
*   **Student Records**: Add new students or see the list of existing ones.
*   **Attendance**: Mark who is present or absent in class and check the history.
*   **Marks**: Enter marks for different subjects and exams.
*   **Fees**: Keep track of who has paid their fees and how much is still pending.

## Before you start:
1.  Make sure you have **Python** installed.
2.  You need **MySQL** running on your laptop.
3.  If you want to use the Window version (GUI), you might need to run this command if it doesn't work:
    *   On Mac: `brew install python-tk`
    *   On Windows: It usually comes with Python!

## How to run it:
1.  **Get the code**: Just download or clone this folder.
2.  **Setup your password**: If your MySQL has a password, you can set it in your terminal like this before running:
    *   `export DB_PASS="your_password"`
3.  **Run it!**:
    *   For the simple menu: `python3 app.py`
    *   For the window app: `python3 gui_app.py`

*The best part? It automatically creates all the tables and the database for you on the first run, so you don't have to worry about manual SQL setup!*

---
Made by Ruthwik (Class 11)
