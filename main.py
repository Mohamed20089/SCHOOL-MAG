import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

con = sqlite3.connect("school_gui.db")
cur = con.cursor()

# جداول
cur.execute("CREATE TABLE IF NOT EXISTS guardians(guardian_id INTEGER PRIMARY KEY AUTOINCREMENT,guardian_name TEXT,phone TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS students(student_id INTEGER PRIMARY KEY AUTOINCREMENT,first_name TEXT,last_name TEXT,age INTEGER,grade TEXT,registration_date TEXT,guardian_id INTEGER,FOREIGN KEY(guardian_id) REFERENCES guardians(guardian_id))")
cur.execute("CREATE TABLE IF NOT EXISTS lessons(lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,lesson_name TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS student_lessons(student_id INTEGER,lesson_id INTEGER,PRIMARY KEY(student_id,lesson_id),FOREIGN KEY(student_id) REFERENCES students(student_id),FOREIGN KEY(lesson_id) REFERENCES lessons(lesson_id))")
con.commit()

# تحميل الطلاب
def load():
    for i in tree.get_children():
        tree.delete(i)

    cur.execute("""
        SELECT s.student_id,
               s.first_name || ' ' || s.last_name AS full_name,
               s.age,
               s.grade,
               s.registration_date,
               COALESCE(g.guardian_name || ' (' || g.phone || ')', 'No Guardian')
        FROM students s
        LEFT JOIN guardians g ON s.guardian_id = g.guardian_id
    """)

    for r in cur.fetchall():
        sid = r[0]
        cur.execute("""
            SELECT lesson_name 
            FROM lessons l 
            JOIN student_lessons sl ON l.lesson_id = sl.lesson_id 
            WHERE sl.student_id = ?
        """, (sid,))
        lessons = ", ".join([x[0] for x in cur.fetchall()])
        tree.insert("", 'end', values=r + (lessons,))

# تحقق
def check(fn, ln, ag, gr, gn, gp):
    if not fn.isalpha(): return "First name letters only"
    if not ln.isalpha(): return "Last name letters only"
    if not ag.isdigit(): return "Age must be number"
    if gp and not gp.isdigit(): return "Phone numbers only"
    if not gr: return "Choose grade"
    return None

# إدارة الدروس
def manage_lessons():
    f = tk.Toplevel(root)
    f.geometry("300x300")
    f.title("Lessons")
    lb = tk.Listbox(f)
    lb.pack(fill="both", expand=True)
    e = tk.Entry(f)
    e.pack()

    def reload_lessons():
        lb.delete(0, "end")
        cur.execute("SELECT lesson_id, lesson_name FROM lessons")
        for l in cur.fetchall():
            lb.insert("end", f"{l[0]} - {l[1]}")

    def add_lesson():
        name = e.get().strip()
        if not name:
            messagebox.showerror("err", "empty")
            return
        cur.execute("INSERT INTO lessons(lesson_name) VALUES (?)", (name,))
        con.commit()
        e.delete(0, "end")
        reload_lessons()

    def del_lesson():
        if not lb.curselection():
            return
        lid = int(lb.get(lb.curselection()[0]).split(" - ")[0])
        cur.execute("DELETE FROM lessons WHERE lesson_id=?", (lid,))
        cur.execute("DELETE FROM student_lessons WHERE lesson_id=?", (lid,))
        con.commit()
        reload_lessons()

    tk.Button(f, text="Add", command=add_lesson).pack()
    tk.Button(f, text="Delete", command=del_lesson).pack()
    reload_lessons()

# نموذج طالب
def form(edit=False, sid=None):
    f = tk.Toplevel(root)
    f.geometry("400x500")
    e1 = tk.Entry(f)
    e2 = tk.Entry(f)
    e3 = tk.Entry(f)
    grades = ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6"]
    grade = tk.StringVar()
    cb = ttk.Combobox(f, textvariable=grade, values=grades, state="readonly")
    e5 = tk.Entry(f)
    e6 = tk.Entry(f)
    tk.Label(f, text="First").pack()
    e1.pack()
    tk.Label(f, text="Last").pack()
    e2.pack()
    tk.Label(f, text="Age").pack()
    e3.pack()
    tk.Label(f, text="Grade").pack()
    cb.pack()
    tk.Label(f, text="Guardian").pack()
    e5.pack()
    tk.Label(f, text="Phone").pack()
    e6.pack()
    tk.Label(f, text="Lessons").pack()
    lb = tk.Listbox(f, selectmode="multiple")
    lb.pack(fill="both", expand=True)

    cur.execute("SELECT lesson_id, lesson_name FROM lessons")
    all_lessons = cur.fetchall()
    for l in all_lessons:
        lb.insert("end", f"{l[0]} - {l[1]}")

    if edit:
        cur.execute("""
            SELECT s.first_name, s.last_name, s.age, s.grade, g.guardian_name, g.phone
            FROM students s
            LEFT JOIN guardians g ON s.guardian_id = g.guardian_id
            WHERE s.student_id = ?
        """, (sid,))
        d = cur.fetchone()
        if d:
            e1.insert(0, d[0])
            e2.insert(0, d[1])
            e3.insert(0, str(d[2]))
            grade.set(d[3])
            e5.insert(0, d[4])
            e6.insert(0, d[5])
        cur.execute("SELECT lesson_id FROM student_lessons WHERE student_id=?", (sid,))
        chosen = [x[0] for x in cur.fetchall()]
        for i, l in enumerate(all_lessons):
            if l[0] in chosen:
                lb.selection_set(i)

    def save():
        fn, ln, ag, gr, gn, gp = e1.get().strip(), e2.get().strip(), e3.get().strip(), grade.get(), e5.get().strip(), e6.get().strip()
        err = check(fn, ln, ag, gr, gn, gp)
        if err:
            messagebox.showerror("err", err)
            return
        cur.execute("SELECT guardian_id FROM guardians WHERE guardian_name=? AND phone=?", (gn, gp))
        g = cur.fetchone()
        gid = g[0] if g else cur.execute("INSERT INTO guardians(guardian_name, phone) VALUES (?, ?)", (gn, gp)) or con.commit() or cur.lastrowid
        if edit:
            cur.execute("UPDATE students SET first_name=?, last_name=?, age=?, grade=?, guardian_id=? WHERE student_id=?", (fn, ln, ag, gr, gid, sid))
        else:
            cur.execute("INSERT INTO students(first_name, last_name, age, grade, registration_date, guardian_id) VALUES (?, ?, ?, ?, ?, ?)", (fn, ln, ag, gr, datetime.now().strftime("%Y-%m-%d"), gid))
            sid = cur.lastrowid
        cur.execute("DELETE FROM student_lessons WHERE student_id=?", (sid,))
        for i in lb.curselection():
            lid = int(lb.get(i).split(" - ")[0])
            cur.execute("INSERT INTO student_lessons(student_id, lesson_id) VALUES (?, ?)", (sid, lid))
        con.commit()
        load()
        f.destroy()

    tk.Button(f, text="Save", command=save).pack()

# أزرار
def add(): form()
def edit_():
    s = tree.selection()
    if not s:
        messagebox.showwarning("warn", "select")
        return
    sid = tree.item(s[0])["values"][0]
    form(True, sid)
def delete():
    s = tree.selection()
    if not s:
        return
    sid = tree.item(s[0])["values"][0]
    if messagebox.askyesno("confirm", "delete?"):
        cur.execute("DELETE FROM student_lessons WHERE student_id=?", (sid,))
        cur.execute("DELETE FROM students WHERE student_id=?", (sid,))
        con.commit()
        load()

root = tk.Tk()
root.geometry("1000x500")
root.title("School System")
cols = ("id", "name", "age", "grade", "date", "guardian", "lessons")
tree = ttk.Treeview(root, columns=cols, show="headings")
for c in cols:
    tree.heading(c, text=c)
tree.pack(fill="both", expand=True)

for t, cmd in [("Add", add), ("Edit", edit_), ("Delete", delete), ("Reload", load), ("Lessons", manage_lessons)]:
    tk.Button(root, text=t, command=cmd).pack(side="left", padx=5, pady=5)

load()
root.mainloop()
con.close()