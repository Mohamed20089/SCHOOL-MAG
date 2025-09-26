import sqlite3
import tkinter as tk
from tkinter import ttk,messagebox

con=sqlite3.connect("school.db")
cur=con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS students(
student_id INTEGER PRIMARY KEY,
first_name TEXT,
last_name TEXT,
age INTEGER,
grade TEXT,
reg_date TEXT)""")

cur.execute("""CREATE TABLE IF NOT EXISTS lessons(
lesson_id INTEGER PRIMARY KEY,
lesson_name TEXT)""")

cur.execute("""CREATE TABLE IF NOT EXISTS student_lessons(
student_id INTEGER,
lesson_id INTEGER,
FOREIGN KEY(student_id) REFERENCES students(student_id),
FOREIGN KEY(lesson_id) REFERENCES lessons(lesson_id))""")

con.commit()

root=tk.Tk()
root.title("School System")

table=ttk.Treeview(root,columns=("id","fname","lname","age","grade","reg","lessons"),show="headings")
table.heading("id",text="رقم الطالب")
table.heading("fname",text="الاسم")
table.heading("lname",text="الكنية")
table.heading("age",text="العمر")
table.heading("grade",text="الصف")
table.heading("reg",text="تاريخ التسجيل")
table.heading("lessons",text="الدروس")

for col in ("id","fname","lname","age","grade","reg","lessons"):
    table.column(col,anchor="center",stretch=True)

table.pack(fill="both",expand=True)

def reload_table():
    for i in table.get_children():
        table.delete(i)
    cur.execute("SELECT * FROM students")
    students=cur.fetchall()
    for s in students:
        sid=s[0]
        cur.execute("""SELECT l.lesson_name FROM lessons l
        JOIN student_lessons sl ON l.lesson_id=sl.lesson_id
        WHERE sl.student_id=?""",(sid,))
        lessons=[x[0] for x in cur.fetchall()]
        lessons_str=", ".join(lessons) if lessons else "—"
        table.insert("", "end", values=(s[0],s[1],s[2],s[3],s[4],s[5],lessons_str))

def add_student():
    win=tk.Toplevel(root)
    tk.Label(win,text="رقم الطالب").grid(row=0,column=0); sid=tk.Entry(win); sid.grid(row=0,column=1)
    tk.Label(win,text="الاسم").grid(row=1,column=0); fname=tk.Entry(win); fname.grid(row=1,column=1)
    tk.Label(win,text="الكنية").grid(row=2,column=0); lname=tk.Entry(win); lname.grid(row=2,column=1)
    tk.Label(win,text="العمر").grid(row=3,column=0); age=tk.Entry(win); age.grid(row=3,column=1)
    tk.Label(win,text="الصف").grid(row=4,column=0); grade=tk.Entry(win); grade.grid(row=4,column=1)
    tk.Label(win,text="تاريخ التسجيل").grid(row=5,column=0); reg=tk.Entry(win); reg.grid(row=5,column=1)
    tk.Label(win,text="اختر الدروس").grid(row=6,column=0)
    cur.execute("SELECT * FROM lessons"); lessons=cur.fetchall()
    vars=[]
    for i,(lid,lname) in enumerate(lessons):
        v=tk.IntVar(); cb=tk.Checkbutton(win,text=lname,variable=v)
        cb.grid(row=6+i,column=1,sticky="w"); vars.append((v,lid))
    def save():
        try:
            cur.execute("INSERT INTO students VALUES(?,?,?,?,?,?)",(sid.get(),fname.get(),lname.get(),age.get(),grade.get(),reg.get()))
            for v,lid in vars:
                if v.get()==1:
                    cur.execute("INSERT INTO student_lessons VALUES(?,?)",(sid.get(),lid))
            con.commit(); reload_table(); win.destroy(); messagebox.showinfo("تم","تمت الإضافة بنجاح")
        except Exception as e: messagebox.showerror("خطأ",str(e))
    tk.Button(win,text="حفظ",command=save).grid(row=20,column=1)

def delete_student():
    sel=table.selection()
    if not sel: return
    sid=table.item(sel[0])["values"][0]
    if messagebox.askyesno("تأكيد","هل تريد حذف الطالب؟"):
        cur.execute("DELETE FROM student_lessons WHERE student_id=?",(sid,))
        cur.execute("DELETE FROM students WHERE student_id=?",(sid,))
        con.commit(); reload_table()

def update_student():
    sel=table.selection()
    if not sel: return
    sid=table.item(sel[0])["values"][0]
    cur.execute("SELECT * FROM students WHERE student_id=?",(sid,))
    s=cur.fetchone()
    win=tk.Toplevel(root)
    tk.Label(win,text="الاسم").grid(row=0,column=0); fname=tk.Entry(win); fname.insert(0,s[1]); fname.grid(row=0,column=1)
    tk.Label(win,text="الكنية").grid(row=1,column=0); lname=tk.Entry(win); lname.insert(0,s[2]); lname.grid(row=1,column=1)
    tk.Label(win,text="العمر").grid(row=2,column=0); age=tk.Entry(win); age.insert(0,s[3]); age.grid(row=2,column=1)
    tk.Label(win,text="الصف").grid(row=3,column=0); grade=tk.Entry(win); grade.insert(0,s[4]); grade.grid(row=3,column=1)
    tk.Label(win,text="تاريخ التسجيل").grid(row=4,column=0); reg=tk.Entry(win); reg.insert(0,s[5]); reg.grid(row=4,column=1)
    cur.execute("SELECT * FROM lessons"); lessons=cur.fetchall()
    cur.execute("SELECT lesson_id FROM student_lessons WHERE student_id=?",(sid,))
    current=[x[0] for x in cur.fetchall()]
    vars=[]
    for i,(lid,lname) in enumerate(lessons):
        v=tk.IntVar(value=1 if lid in current else 0)
        cb=tk.Checkbutton(win,text=lname,variable=v); cb.grid(row=5+i,column=1,sticky="w")
        vars.append((v,lid))
    def save():
        cur.execute("UPDATE students SET first_name=?,last_name=?,age=?,grade=?,reg_date=? WHERE student_id=?",(fname.get(),lname.get(),age.get(),grade.get(),reg.get(),sid))
        cur.execute("DELETE FROM student_lessons WHERE student_id=?",(sid,))
        for v,lid in vars:
            if v.get()==1:
                cur.execute("INSERT INTO student_lessons VALUES(?,?)",(sid,lid))
        con.commit(); reload_table(); win.destroy()
    tk.Button(win,text="حفظ",command=save).grid(row=30,column=1)

frm=tk.Frame(root); frm.pack()
tk.Button(frm,text="إضافة",command=add_student).pack(side="left",padx=5)
tk.Button(frm,text="تعديل",command=update_student).pack(side="left",padx=5)
tk.Button(frm,text="حذف",command=delete_student).pack(side="left",padx=5)

reload_table()
root.mainloop()
