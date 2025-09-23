import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# ================= قاعدة البيانات =================
def init_db():
    conn = sqlite3.connect("school.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        age INTEGER,
        grade INTEGER,
        reg_date TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS lessons (
        lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,
        lesson_name TEXT UNIQUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS student_lessons (
        student_id INTEGER,
        lesson_id INTEGER,
        PRIMARY KEY (student_id, lesson_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
        FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()


# ================= التحقق =================
def is_text(val): return val.isalpha()
def is_number(val): return val.isdigit()


# ================= إدارة الدروس =================
def manage_lessons():
    def load_lessons():
        for row in tree.get_children():
            tree.delete(row)
        cur.execute("SELECT * FROM lessons")
        for row in cur.fetchall():
            tree.insert("", tk.END, values=row)

    def add_lesson():
        name = entry_lesson.get().strip()
        if not name:
            messagebox.showerror("خطأ", "اسم الدرس فارغ")
            return
        try:
            cur.execute("INSERT INTO lessons (lesson_name) VALUES (?)", (name,))
            conn.commit()
            load_lessons()
            entry_lesson.delete(0, tk.END)
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "الدرس موجود بالفعل")

    def delete_lesson():
        sel = tree.selection()
        if not sel:
            return
        lid = tree.item(sel[0])["values"][0]
        cur.execute("DELETE FROM lessons WHERE lesson_id=?", (lid,))
        conn.commit()
        load_lessons()

    win = tk.Toplevel(root)
    win.title("إدارة الدروس")
    win.geometry("400x300")

    tk.Label(win, text="اسم الدرس:").pack(pady=5)
    entry_lesson = tk.Entry(win)
    entry_lesson.pack()

    tk.Button(win, text="إضافة", command=add_lesson).pack(pady=3)
    tk.Button(win, text="حذف", command=delete_lesson).pack(pady=3)

    tree = ttk.Treeview(win, columns=("id", "name"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("name", text="الدرس")
    tree.pack(fill=tk.BOTH, expand=True, pady=5)

    conn = sqlite3.connect("school.db")
    cur = conn.cursor()
    load_lessons()


# ================= إضافة/تعديل طالب =================
def student_form(edit=False, student_data=None):
    def save_student():
        sid = e_id.get()
        fname = e_first.get()
        lname = e_last.get()
        age = e_age.get()
        grade = e_grade.get()
        reg = e_reg.get()

        if not (is_number(sid) and is_text(fname) and is_text(lname) and is_number(age) and is_number(grade)):
            messagebox.showerror("خطأ", "تأكد من صحة المدخلات.")
            return

        try:
            if edit:
                cur.execute("""
                UPDATE students SET first_name=?, last_name=?, age=?, grade=?, reg_date=?
                WHERE student_id=?
                """, (fname, lname, int(age), int(grade), reg, int(sid)))
            else:
                cur.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)",
                            (int(sid), fname, lname, int(age), int(grade), reg))

            # تحديث الدروس المختارة
            cur.execute("DELETE FROM student_lessons WHERE student_id=?", (int(sid),))
            for i in lessons_box.curselection():
                lname_sel = lessons_box.get(i)
                cur.execute("SELECT lesson_id FROM lessons WHERE lesson_name=?", (lname_sel,))
                lid = cur.fetchone()
                if lid:
                    cur.execute("INSERT OR IGNORE INTO student_lessons VALUES (?, ?)", (int(sid), lid[0]))

            conn.commit()
            load_students()
            win.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "رقم الطالب موجود بالفعل")

    win = tk.Toplevel(root)
    win.title("تعديل طالب" if edit else "إضافة طالب")

    tk.Label(win, text="رقم الطالب:").grid(row=0, column=0)
    e_id = tk.Entry(win)
    e_id.grid(row=0, column=1)

    tk.Label(win, text="الاسم:").grid(row=1, column=0)
    e_first = tk.Entry(win)
    e_first.grid(row=1, column=1)

    tk.Label(win, text="الكنية:").grid(row=2, column=0)
    e_last = tk.Entry(win)
    e_last.grid(row=2, column=1)

    tk.Label(win, text="العمر:").grid(row=3, column=0)
    e_age = tk.Entry(win)
    e_age.grid(row=3, column=1)

    tk.Label(win, text="الصف:").grid(row=4, column=0)
    e_grade = tk.Entry(win)
    e_grade.grid(row=4, column=1)

    tk.Label(win, text="تاريخ التسجيل:").grid(row=5, column=0)
    e_reg = tk.Entry(win)
    e_reg.grid(row=5, column=1)

    tk.Label(win, text="الدروس:").grid(row=6, column=0)
    lessons_box = tk.Listbox(win, selectmode=tk.MULTIPLE, height=6)
    lessons_box.grid(row=6, column=1)

    # تحميل الدروس
    cur.execute("SELECT lesson_name FROM lessons")
    all_lessons = [l[0] for l in cur.fetchall()]
    for l in all_lessons:
        lessons_box.insert(tk.END, l)

    if edit and student_data:
        e_id.insert(0, student_data[0])
        e_id.config(state="disabled")
        e_first.insert(0, student_data[1])
        e_last.insert(0, student_data[2])
        e_age.insert(0, student_data[3])
        e_grade.insert(0, student_data[4])
        e_reg.insert(0, student_data[5])

        # تحديد الدروس المسجلة
        cur.execute("""
        SELECT l.lesson_name FROM lessons l
        JOIN student_lessons sl ON l.lesson_id=sl.lesson_id
        WHERE sl.student_id=?
        """, (student_data[0],))
        lessons = [x[0] for x in cur.fetchall()]
        for i, l in enumerate(all_lessons):
            if l in lessons:
                lessons_box.selection_set(i)

    tk.Button(win, text="حفظ", command=save_student).grid(row=7, column=0, columnspan=2)


# ================= عرض كل الطلاب =================
def load_students():
    for row in table.get_children():
        table.delete(row)
    cur.execute("SELECT * FROM students")
    for row in cur.fetchall():
        table.insert("", tk.END, values=row)


def delete_student():
    sel = table.selection()
    if not sel:
        return
    sid = table.item(sel[0])["values"][0]
    cur.execute("DELETE FROM students WHERE student_id=?", (sid,))
    conn.commit()
    load_students()


def edit_student():
    sel = table.selection()
    if not sel:
        return
    sid = table.item(sel[0])["values"][0]
    cur.execute("SELECT * FROM students WHERE student_id=?", (sid,))
    student = cur.fetchone()
    if student:
        student_form(edit=True, student_data=student)


# ================= الواجهة الرئيسية =================
root = tk.Tk()
root.title("📚 نظام المدرسة")
root.geometry("700x500")

style = ttk.Style()
style.configure("Treeview", font=("Arial", 11), rowheight=28)
style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

frm_btns = tk.Frame(root)
frm_btns.pack(pady=10)

tk.Button(frm_btns, text="إضافة طالب", command=lambda: student_form()).pack(side=tk.LEFT, padx=5)
tk.Button(frm_btns, text="تعديل", command=edit_student).pack(side=tk.LEFT, padx=5)
tk.Button(frm_btns, text="حذف", command=delete_student).pack(side=tk.LEFT, padx=5)
tk.Button(frm_btns, text="إدارة الدروس", command=manage_lessons).pack(side=tk.LEFT, padx=5)

table = ttk.Treeview(root, columns=("id", "fname", "lname", "age", "grade", "reg"),
                     show="headings")
table.heading("id", text="ID")
table.heading("fname", text="الاسم")
table.heading("lname", text="الكنية")
table.heading("age", text="العمر")
table.heading("grade", text="الصف")
table.heading("reg", text="تاريخ التسجيل")
table.pack(fill=tk.BOTH, expand=True)

conn = sqlite3.connect("school.db")
cur = conn.cursor()
init_db()
load_students()

root.mainloop()
