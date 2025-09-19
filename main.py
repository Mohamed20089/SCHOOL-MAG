import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

conn = sqlite3.connect("school.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS students (student_id INTEGER PRIMARY KEY, first_name TEXT NOT NULL,last_name TEXT NOT NULL,age INTEGER,grade TEXT,registration_date TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS lessons (lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,lesson_name TEXT NOT NULL UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS student_lessons (student_id INTEGER,lesson_id INTEGER,FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,FOREIGN KEY(lesson_id) REFERENCES lessons(lesson_id) ON DELETE CASCADE,PRIMARY KEY(student_id, lesson_id))")
conn.commit()

def add_student():
 try:
  student_id = int(simpledialog.askstring("Add Student","Enter student ID:"))
  first_name = simpledialog.askstring("Add Student","Enter first name:")
  last_name = simpledialog.askstring("Add Student","Enter last name:")
  age = int(simpledialog.askstring("Add Student","Enter age:"))
  grade = simpledialog.askstring("Add Student","Enter grade:")
  registration_date = datetime.now().strftime("%Y-%m-%d")
  cursor.execute("INSERT INTO students VALUES (?,?,?,?,?,?)",(student_id,first_name,last_name,age,grade,registration_date))
  lessons = simpledialog.askstring("Add Student","Enter lessons (comma separated):")
  if lessons:
   for l in lessons.split(","):
    l = l.strip()
    if l:
     cursor.execute("INSERT OR IGNORE INTO lessons (lesson_name) VALUES (?)",(l,))
     cursor.execute("SELECT lesson_id FROM lessons WHERE lesson_name=?",(l,))
     lesson_id = cursor.fetchone()[0]
     cursor.execute("INSERT INTO student_lessons (student_id, lesson_id) VALUES (?,?)",(student_id,lesson_id))
  conn.commit()
  messagebox.showinfo("Success","Student added successfully ✅")
 except Exception as e:
  messagebox.showerror("Error","Failed to add student: "+str(e))

def delete_student():
 s_id = simpledialog.askstring("Delete Student","Enter student ID to delete:")
 if s_id:
  cursor.execute("SELECT * FROM students WHERE student_id=?",(s_id,))
  if cursor.fetchone():
   cursor.execute("DELETE FROM students WHERE student_id=?",(s_id,))
   conn.commit()
   messagebox.showinfo("Success","Student deleted successfully ✅")
  else:
   messagebox.showwarning("Not Found","Student not found ⚠️")

def update_student():
 s_id = simpledialog.askstring("Update Student","Enter student ID to update:")
 if s_id:
  cursor.execute("SELECT * FROM students WHERE student_id=?",(s_id,))
  if cursor.fetchone():
   f = simpledialog.askstring("Update Student","Enter new first name:")
   l = simpledialog.askstring("Update Student","Enter new last name:")
   a = simpledialog.askstring("Update Student","Enter new age:")
   g = simpledialog.askstring("Update Student","Enter new grade:")
   cursor.execute("UPDATE students SET first_name=?, last_name=?, age=?, grade=? WHERE student_id=?",(f,l,a,g,s_id))
   conn.commit()
   messagebox.showinfo("Success","Student updated successfully ✅")
  else:
   messagebox.showwarning("Not Found","Student not found ⚠️")

def show_student():
 sid = simpledialog.askstring("Show Student","Enter student ID to view:")
 if sid:
  cursor.execute("SELECT * FROM students WHERE student_id=?",(sid,))
  student = cursor.fetchone()
  if student:
   info = f"\nID: {student[0]}\nName: {student[1]} {student[2]}\nAge: {student[3]}\nGrade: {student[4]}\nRegistration Date: {student[5]}\n"
   cursor.execute("SELECT lesson_name FROM lessons JOIN student_lessons ON lessons.lesson_id = student_lessons.lesson_id WHERE student_lessons.student_id=?",(sid,))
   lessons = [x[0] for x in cursor.fetchall()]
   info += "Lessons: " + ", ".join(lessons) if lessons else "Lessons: None"
   messagebox.showinfo("Student Info", info)
  else:
   messagebox.showwarning("Not Found","Student not found ⚠️")

root = tk.Tk()
root.title("School Management System")
root.geometry("400x300")
tk.Label(root,text="School Management System",font=("Arial",14,"bold")).pack(pady=20)
tk.Button(root,text="Add Student",width=20,command=add_student).pack(pady=5)
tk.Button(root,text="Delete Student",width=20,command=delete_student).pack(pady=5)
tk.Button(root,text="Update Student",width=20,command=update_student).pack(pady=5)
tk.Button(root,text="Show Student",width=20,command=show_student).pack(pady=5)
tk.Button(root,text="Quit",width=20,command=root.quit).pack(pady=20)
root.mainloop()
conn.close()