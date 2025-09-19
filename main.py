import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

# Connect to the database
conn = sqlite3.connect("school.db")
cursor = conn.cursor()

# Create tables if not exist
cursor.execute("""CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    age INTEGER,
    grade TEXT,
    registration_date TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS lessons (
    lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_name TEXT NOT NULL UNIQUE
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS student_lessons (
    student_id INTEGER,
    lesson_id INTEGER,
    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY(lesson_id) REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    PRIMARY KEY(student_id, lesson_id)
)""")

conn.commit()


# ============ Functions ============

def add_student():
    try:
        student_id = int(simpledialog.askstring("Add Student", "Enter student ID:"))
        first_name = simpledialog.askstring("Add Student", "Enter first name:")
        last_name = simpledialog.askstring("Add Student", "Enter last name:")
        age = int(simpledialog.askstring("Add Student", "Enter age:"))
        grade = simpledialog.askstring("Add Student", "Enter grade:")
        registration_date = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)",
                       (student_id, first_name, last_name, age, grade, registration_date))

        lessons = simpledialog.askstring("Add Student", "Enter lessons (comma separated):")
        if lessons:
            for lesson in lessons.split(","):
                lesson = lesson.strip()
                if lesson:
                    cursor.execute("INSERT OR IGNORE INTO lessons (lesson_name) VALUES (?)", (lesson,))
                    cursor.execute("SELECT lesson_id FROM lessons WHERE lesson_name=?", (lesson,))
                    lesson_id = cursor.fetchone()[0]
                    cursor.execute("INSERT INTO student_lessons (student_id, lesson_id) VALUES (?, ?)",
                                   (student_id, lesson_id))

        conn.commit()
        messagebox.showinfo("Success", "Student added successfully ✅")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add student: {e}")


def delete_student():
    student_id = simpledialog.askstring("Delete Student", "Enter student ID to delete:")
    if student_id:
        cursor.execute("SELECT * FROM students WHERE student_id=?", (student_id,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM students WHERE student_id=?", (student_id,))
            conn.commit()
            messagebox.showinfo("Success", "Student deleted successfully ✅")
        else:
            messagebox.showwarning("Not Found", "Student not found ⚠️")


def update_student():
    student_id = simpledialog.askstring("Update Student", "Enter student ID to update:")
    if student_id:
        cursor.execute("SELECT * FROM students WHERE student_id=?", (student_id,))
        if cursor.fetchone():
            first_name = simpledialog.askstring("Update Student", "Enter new first name:")
            last_name = simpledialog.askstring("Update Student", "Enter new last name:")
            age = simpledialog.askstring("Update Student", "Enter new age:")
            grade = simpledialog.askstring("Update Student", "Enter new grade:")

            cursor.execute("""UPDATE students
                              SET first_name=?, last_name=?, age=?, grade=?
                              WHERE student_id=?""",
                           (first_name, last_name, age, grade, student_id))
            conn.commit()
            messagebox.showinfo("Success", "Student updated successfully ✅")
        else:
            messagebox.showwarning("Not Found", "Student not found ⚠️")


def show_student():
    student_id = simpledialog.askstring("Show Student", "Enter student ID to view:")
    if student_id:
        cursor.execute("SELECT * FROM students WHERE student_id=?", (student_id,))
        student = cursor.fetchone()
        if student:
            info = f"""
ID: {student[0]}
Name: {student[1]} {student[2]}
Age: {student[3]}
Grade: {student[4]}
Registration Date: {student[5]}
"""
            # Get lessons
            cursor.execute("""SELECT lesson_name FROM lessons
                              JOIN student_lessons ON lessons.lesson_id = student_lessons.lesson_id
                              WHERE student_lessons.student_id=?""", (student_id,))
            lessons = [row[0] for row in cursor.fetchall()]
            info += "Lessons: " + (", ".join(lessons) if lessons else "None")

            messagebox.showinfo("Student Info", info)
        else:
            messagebox.showwarning("Not Found", "Student not found ⚠️")


# ============ GUI ============

root = tk.Tk()
root.title("School Management System")
root.geometry("400x300")

label = tk.Label(root, text="School Management System", font=("Arial", 14, "bold"))
label.pack(pady=20)

btn_add = tk.Button(root, text="Add Student", width=20, command=add_student)
btn_add.pack(pady=5)

btn_delete = tk.Button(root, text="Delete Student", width=20, command=delete_student)
btn_delete.pack(pady=5)

btn_update = tk.Button(root, text="Update Student", width=20, command=update_student)
btn_update.pack(pady=5)

btn_show = tk.Button(root, text="Show Student", width=20, command=show_student)
btn_show.pack(pady=5)

btn_quit = tk.Button(root, text="Quit", width=20, command=root.quit)
btn_quit.pack(pady=20)

root.mainloop()

conn.close()
