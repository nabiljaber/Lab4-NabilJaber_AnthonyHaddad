'''"""
Tkinter Desktop Application (SQLite Version) — School Management System

This module is part of a course project that demonstrates a simple School Management System.
It follows the same documentation style across modules: a clear overview, responsibilities,
and how this component interacts with others in the project.

Date: 2025-09-22
Author: Anthony Haddad

Contents:
- High-level responsibilities of this module
- Key classes and functions defined here
- Notes on usage and important behaviors
"""'''
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from db_store import DBStore, ValidationError

class App(tk.Tk):
    """Top-level Tkinter GUI application that provides tabs for Students, Instructors, Courses, and Relations."""

    def __init__(self):
        '''"""  init  .

"""'''
        super().__init__()
        self.title('School Management System (SQLite)')
        self.geometry('1100x680')
        self.db = DBStore()
        self.sel_student_id = None
        self.sel_instructor_id = None
        self.sel_course_id = None
        self._auto_refresh_enabled = tk.BooleanVar(value=False)
        self._auto_refresh_job = None
        self._build_toolbar()
        self._build_tabs()
        self._refresh_all()
        self.protocol('WM_DELETE_WINDOW', self.on_close)

    def _build_toolbar(self):
        '''"""Construct the application toolbar.

"""'''
        bar = ttk.Frame(self, padding=(6, 6))
        bar.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(bar, text='Backup DB', command=self._backup).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text='Export CSV', command=self._export_csv).pack(side=tk.LEFT, padx=4)
        ttk.Label(bar, text='  Search:').pack(side=tk.LEFT, padx=(12, 4))
        self.var_search = tk.StringVar()
        ent = ttk.Entry(bar, textvariable=self.var_search, width=32)
        ent.pack(side=tk.LEFT, padx=4)
        ent.bind('<KeyRelease>', lambda e: self._apply_search())
        ttk.Label(bar, text=' in ').pack(side=tk.LEFT)
        self.var_search_scope = tk.StringVar(value='Students')
        ttk.Combobox(bar, textvariable=self.var_search_scope, values=['Students', 'Instructors', 'Courses'], width=12, state='readonly').pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text='Clear', command=self._clear_search).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(bar, text='Auto-Refresh', variable=self._auto_refresh_enabled, command=self._toggle_auto_refresh).pack(side=tk.RIGHT, padx=6)

    def _backup(self):
        '''""" backup.

"""'''
        path = filedialog.asksaveasfilename(defaultextension='.db', filetypes=[('SQLite DB', '*.db')])
        if not path:
            return
        try:
            self.db.backup_db(path)
            messagebox.showinfo('Backup', f'Database copied to:\n{path}')
        except Exception as e:
            messagebox.showerror('Backup error', str(e))

    def _export_csv(self):
        '''""" export csv.

"""'''
        folder = filedialog.askdirectory(title='Choose folder to export CSV files')
        if not folder:
            return
        try:
            with open(f'{folder}/students.csv', 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['student_id', 'name', 'age', 'email', 'registered_course_ids'])
                for s in self.db.list_students():
                    course_ids = self.db.student_courses(s.student_id)
                    w.writerow([s.student_id, s.name, s.age, s.email, ';'.join(course_ids)])
            with open(f'{folder}/instructors.csv', 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['instructor_id', 'name', 'age', 'email', 'assigned_course_ids'])
                courses = self.db.list_courses()
                for i in self.db.list_instructors():
                    assigned = [c.course_id for c in courses if c.instructor_id == i.instructor_id]
                    w.writerow([i.instructor_id, i.name, i.age, i.email, ';'.join(assigned)])
            with open(f'{folder}/courses.csv', 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['course_id', 'course_name', 'instructor_id', 'enrolled_student_ids'])
                for c in self.db.list_courses():
                    s_ids = self.db.course_students(c.course_id)
                    w.writerow([c.course_id, c.course_name, c.instructor_id or '', ';'.join(s_ids)])
            messagebox.showinfo('Exported', f'CSV files saved to:\n{folder}')
        except Exception as e:
            messagebox.showerror('Export error', str(e))

    def _build_tabs(self):
        '''"""Construct main tab pages and attach them to the window.

"""'''
        nb = ttk.Notebook(self)
        nb.pack(expand=True, fill=tk.BOTH, padx=6, pady=6)
        self.tab_students = ttk.Frame(nb, padding=10)
        self.tab_instructors = ttk.Frame(nb, padding=10)
        self.tab_courses = ttk.Frame(nb, padding=10)
        self.tab_relations = ttk.Frame(nb, padding=10)
        nb.add(self.tab_students, text='Students')
        nb.add(self.tab_instructors, text='Instructors')
        nb.add(self.tab_courses, text='Courses')
        nb.add(self.tab_relations, text='Relations')
        self._build_students_tab()
        self._build_instructors_tab()
        self._build_courses_tab()
        self._build_relations_tab()

    def _build_students_tab(self):
        '''""" build students tab.

"""'''
        frm = self.tab_students
        form = ttk.LabelFrame(frm, text='Student Form', padding=10)
        form.pack(side=tk.TOP, fill=tk.X)
        self.s_name = tk.StringVar()
        self.s_age = tk.StringVar()
        self.s_email = tk.StringVar()
        self.s_id = tk.StringVar()
        grid = ttk.Frame(form)
        grid.pack(fill=tk.X)
        ttk.Label(grid, text='Name').grid(row=0, column=0, sticky='w', padx=4, pady=4)
        ttk.Entry(grid, textvariable=self.s_name, width=30).grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(grid, text='Age').grid(row=0, column=2, sticky='w', padx=4, pady=4)
        ttk.Entry(grid, textvariable=self.s_age, width=10).grid(row=0, column=3, padx=4, pady=4)
        ttk.Label(grid, text='Email').grid(row=1, column=0, sticky='w', padx=4, pady=4)
        ttk.Entry(grid, textvariable=self.s_email, width=30).grid(row=1, column=1, padx=4, pady=4)
        ttk.Label(grid, text='Student ID').grid(row=1, column=2, sticky='w', padx=4, pady=4)
        ttk.Entry(grid, textvariable=self.s_id, width=16).grid(row=1, column=3, padx=4, pady=4)
        btns = ttk.Frame(form)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text='Add', command=self._add_student).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Update', command=self._update_student).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Delete', command=self._delete_student).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Clear Form', command=self._clear_student_form).pack(side=tk.LEFT, padx=8)
        cols = ('id', 'name', 'age', 'email', 'courses')
        self.tree_students = ttk.Treeview(frm, columns=cols, show='headings', height=12)
        for c, w in zip(cols, (110, 180, 60, 220, 360)):
            self.tree_students.heading(c, text=c.capitalize())
            self.tree_students.column(c, width=w, anchor='w')
        self.tree_students.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.tree_students.bind('<<TreeviewSelect>>', self._on_student_select)

    def _add_student(self):
        '''""" add student.

"""'''
        try:
            self.db.add_student(self.s_name.get(), int(self.s_age.get()), self.s_email.get(), self.s_id.get())
            messagebox.showinfo('Success', 'Student added')
            self._clear_student_form()
            self._refresh_all()
        except (ValidationError, ValueError) as e:
            messagebox.showerror('Add error', str(e))

    def _update_student(self):
        '''""" update student.

"""'''
        if not self.sel_student_id:
            return messagebox.showerror('No selection', 'Select a student')
        try:
            self.db.update_student(self.sel_student_id, name=self.s_name.get(), age=int(self.s_age.get()), email=self.s_email.get())
            messagebox.showinfo('Updated', 'Student updated')
            self._refresh_all()
        except (ValidationError, ValueError) as e:
            messagebox.showerror('Update error', str(e))

    def _delete_student(self):
        '''""" delete student.

"""'''
        if not self.sel_student_id:
            return messagebox.showerror('No selection', 'Select a student')
        if not messagebox.askyesno('Confirm', f'Delete student {self.sel_student_id}?'):
            return
        self.db.delete_student(self.sel_student_id)
        self._clear_student_form()
        self._refresh_all()

    def _clear_student_form(self):
        '''""" clear student form.

"""'''
        self.sel_student_id = None
        self.s_name.set('')
        self.s_age.set('')
        self.s_email.set('')
        self.s_id.set('')

    def _on_student_select(self, _):
        '''    """ on student select.

Parameters:
    _: parameter.
    """'''
        sel = self.tree_students.selection()
        if not sel:
            return
        sid, name, age, email, _ = self.tree_students.item(sel[0], 'values')
        self.sel_student_id = sid
        self.s_id.set(sid)
        self.s_name.set(name)
        self.s_age.set(age)
        self.s_email.set(email)

    def _refresh_students(self, filter_text: str=''):
        '''    """ refresh students.

Parameters:
    filter_text: parameter.
    """'''
        self.tree_students.delete(*self.tree_students.get_children())
        ft = (filter_text or '').lower()
        for s in self.db.list_students():
            courses = ', '.join(self.db.student_courses(s.student_id)) or 'None'
            row = (s.student_id, s.name, s.age, s.email, courses)
            if not ft or any((ft in str(x).lower() for x in row)):
                self.tree_students.insert('', tk.END, values=row)

    def _build_instructors_tab(self):
        '''""" build instructors tab.

"""'''
        frm = self.tab_instructors
        form = ttk.LabelFrame(frm, text='Instructor Form', padding=10)
        form.pack(side=tk.TOP, fill=tk.X)
        self.i_name = tk.StringVar()
        self.i_age = tk.StringVar()
        self.i_email = tk.StringVar()
        self.i_id = tk.StringVar()
        grid = ttk.Frame(form)
        grid.pack(fill=tk.X)
        ttk.Label(grid, text='Name').grid(row=0, column=0, sticky='w', padx=4, pady=4)
        ttk.Entry(grid, textvariable=self.i_name, width=30).grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(grid, text='Age').grid(row=0, column=2, sticky='w', padx=4, pady=4)
        ttk.Entry(grid, textvariable=self.i_age, width=10).grid(row=0, column=3, padx=4, pady=4)
        ttk.Label(grid, text='Email').grid(row=1, column=0, sticky='w', padx=4, pady=4)
        ttk.Entry(grid, textvariable=self.i_email, width=30).grid(row=1, column=1, padx=4, pady=4)
        ttk.Label(grid, text='Instructor ID').grid(row=1, column=2, sticky='w', padx=4, pady=4)
        ttk.Entry(grid, textvariable=self.i_id, width=16).grid(row=1, column=3, padx=4, pady=4)
        btns = ttk.Frame(form)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text='Add', command=self._add_instructor).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Update', command=self._update_instructor).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Delete', command=self._delete_instructor).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Clear Form', command=self._clear_instructor_form).pack(side=tk.LEFT, padx=8)
        cols = ('id', 'name', 'age', 'email', 'courses')
        self.tree_instructors = ttk.Treeview(frm, columns=cols, show='headings', height=12)
        for c, w in zip(cols, (120, 180, 60, 220, 360)):
            self.tree_instructors.heading(c, text=c.capitalize())
            self.tree_instructors.column(c, width=w, anchor='w')
        self.tree_instructors.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.tree_instructors.bind('<<TreeviewSelect>>', self._on_instructor_select)

    def _add_instructor(self):
        '''""" add instructor.

"""'''
        try:
            self.db.add_instructor(self.i_name.get(), int(self.i_age.get()), self.i_email.get(), self.i_id.get())
            messagebox.showinfo('Success', 'Instructor added')
            self._clear_instructor_form()
            self._refresh_all()
        except (ValidationError, ValueError) as e:
            messagebox.showerror('Add error', str(e))

    def _update_instructor(self):
        '''""" update instructor.

"""'''
        if not self.sel_instructor_id:
            return messagebox.showerror('No selection', 'Select an instructor')
        try:
            self.db.update_instructor(self.sel_instructor_id, name=self.i_name.get(), age=int(self.i_age.get()), email=self.i_email.get())
            messagebox.showinfo('Updated', 'Instructor updated')
            self._refresh_all()
        except (ValidationError, ValueError) as e:
            messagebox.showerror('Update error', str(e))

    def _delete_instructor(self):
        '''""" delete instructor.

"""'''
        if not self.sel_instructor_id:
            return messagebox.showerror('No selection', 'Select an instructor')
        if not messagebox.askyesno('Confirm', f'Delete instructor {self.sel_instructor_id}?'):
            return
        self.db.delete_instructor(self.sel_instructor_id)
        self._clear_instructor_form()
        self._refresh_all()

    def _clear_instructor_form(self):
        '''""" clear instructor form.

"""'''
        self.sel_instructor_id = None
        self.i_name.set('')
        self.i_age.set('')
        self.i_email.set('')
        self.i_id.set('')

    def _on_instructor_select(self, _):
        '''    """ on instructor select.

Parameters:
    _: parameter.
    """'''
        sel = self.tree_instructors.selection()
        if not sel:
            return
        iid, name, age, email, _ = self.tree_instructors.item(sel[0], 'values')
        self.sel_instructor_id = iid
        self.i_id.set(iid)
        self.i_name.set(name)
        self.i_age.set(age)
        self.i_email.set(email)

    def _refresh_instructors(self, filter_text: str=''):
        '''    """ refresh instructors.

Parameters:
    filter_text: parameter.
    """'''
        self.tree_instructors.delete(*self.tree_instructors.get_children())
        ft = (filter_text or '').lower()
        all_courses = self.db.list_courses()
        for i in self.db.list_instructors():
            course_ids = [c.course_id for c in all_courses if c.instructor_id == i.instructor_id]
            row = (i.instructor_id, i.name, i.age, i.email, ', '.join(course_ids) or 'None')
            if not ft or any((ft in str(x).lower() for x in row)):
                self.tree_instructors.insert('', tk.END, values=row)

    def _build_courses_tab(self):
        '''""" build courses tab.

"""'''
        frm = self.tab_courses
        form = ttk.LabelFrame(frm, text='Course Form', padding=10)
        form.pack(side=tk.TOP, fill=tk.X)
        self.c_id = tk.StringVar()
        self.c_name = tk.StringVar()
        grid = ttk.Frame(form)
        grid.pack(fill=tk.X)
        ttk.Label(grid, text='Course ID').grid(row=0, column=0, sticky='w', padx=4, pady=4)
        ttk.Entry(grid, textvariable=self.c_id, width=18).grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(grid, text='Course Name').grid(row=0, column=2, sticky='w', padx=4, pady=4)
        ttk.Entry(grid, textvariable=self.c_name, width=30).grid(row=0, column=3, padx=4, pady=4)
        btns = ttk.Frame(form)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text='Add', command=self._add_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Update Name', command=self._update_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Delete', command=self._delete_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Clear Form', command=self._clear_course_form).pack(side=tk.LEFT, padx=8)
        cols = ('id', 'name', 'instructor', 'students')
        self.tree_courses = ttk.Treeview(frm, columns=cols, show='headings', height=12)
        for c, w in zip(cols, (120, 260, 160, 460)):
            self.tree_courses.heading(c, text=c.capitalize())
            self.tree_courses.column(c, width=w, anchor='w')
        self.tree_courses.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.tree_courses.bind('<<TreeviewSelect>>', self._on_course_select)

    def _add_course(self):
        '''""" add course.

"""'''
        try:
            self.db.add_course(self.c_id.get(), self.c_name.get())
            messagebox.showinfo('Success', 'Course added')
            self._clear_course_form()
            self._refresh_all()
        except ValidationError as e:
            messagebox.showerror('Add error', str(e))

    def _update_course(self):
        '''""" update course.

"""'''
        if not self.sel_course_id:
            return messagebox.showerror('No selection', 'Select a course')
        try:
            self.db.update_course_name(self.sel_course_id, self.c_name.get())
            messagebox.showinfo('Updated', 'Course renamed')
            self._refresh_all()
        except ValidationError as e:
            messagebox.showerror('Update error', str(e))

    def _delete_course(self):
        '''""" delete course.

"""'''
        if not self.sel_course_id:
            return messagebox.showerror('No selection', 'Select a course')
        if not messagebox.askyesno('Confirm', f'Delete course {self.sel_course_id}?'):
            return
        self.db.delete_course(self.sel_course_id)
        self._clear_course_form()
        self._refresh_all()

    def _clear_course_form(self):
        '''""" clear course form.

"""'''
        self.sel_course_id = None
        self.c_id.set('')
        self.c_name.set('')

    def _on_course_select(self, _):
        '''    """ on course select.

Parameters:
    _: parameter.
    """'''
        sel = self.tree_courses.selection()
        if not sel:
            return
        cid, name, _ins, _students = self.tree_courses.item(sel[0], 'values')
        self.sel_course_id = cid
        self.c_id.set(cid)
        self.c_name.set(name)

    def _refresh_courses(self, filter_text: str=''):
        '''    """ refresh courses.

Parameters:
    filter_text: parameter.
    """'''
        self.tree_courses.delete(*self.tree_courses.get_children())
        ft = (filter_text or '').lower()
        for c in self.db.list_courses():
            ins = c.instructor_id or 'None'
            students = ', '.join(self.db.course_students(c.course_id)) or 'None'
            row = (c.course_id, c.course_name, ins, students)
            if not ft or any((ft in str(x).lower() for x in row)):
                self.tree_courses.insert('', tk.END, values=row)

    def _build_relations_tab(self):
        '''""" build relations tab.

"""'''
        frm = self.tab_relations
        enroll = ttk.LabelFrame(frm, text='Enroll Student in Course', padding=10)
        enroll.pack(fill=tk.X, pady=6)
        self.var_student = tk.StringVar()
        self.var_course_enroll = tk.StringVar()
        ttk.Label(enroll, text='Student ID').grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.cmb_student = ttk.Combobox(enroll, textvariable=self.var_student, width=20, state='readonly')
        self.cmb_student.grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(enroll, text='Course ID').grid(row=0, column=2, padx=4, pady=4, sticky='w')
        self.cmb_course_enroll = ttk.Combobox(enroll, textvariable=self.var_course_enroll, width=20, state='readonly')
        self.cmb_course_enroll.grid(row=0, column=3, padx=4, pady=4)
        ttk.Button(enroll, text='Enroll', command=self._enroll_student).grid(row=0, column=4, padx=6, pady=4)
        assign = ttk.LabelFrame(frm, text='Assign Instructor to Course', padding=10)
        assign.pack(fill=tk.X, pady=6)
        self.var_instructor = tk.StringVar()
        self.var_course_assign = tk.StringVar()
        ttk.Label(assign, text='Instructor ID').grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.cmb_instructor = ttk.Combobox(assign, textvariable=self.var_instructor, width=20, state='readonly')
        self.cmb_instructor.grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(assign, text='Course ID').grid(row=0, column=2, padx=4, pady=4, sticky='w')
        self.cmb_course_assign = ttk.Combobox(assign, textvariable=self.var_course_assign, width=20, state='readonly')
        self.cmb_course_assign.grid(row=0, column=3, padx=4, pady=4)
        ttk.Button(assign, text='Assign', command=self._assign_instructor).grid(row=0, column=4, padx=6, pady=4)
        drop = ttk.LabelFrame(frm, text='Drop / Unassign', padding=10)
        drop.pack(fill=tk.X, pady=6)
        self.var_student_drop = tk.StringVar()
        self.var_course_drop = tk.StringVar()
        self.var_course_unassign = tk.StringVar()
        ttk.Label(drop, text='Drop Student ID').grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.cmb_student_drop = ttk.Combobox(drop, textvariable=self.var_student_drop, width=20, state='readonly')
        self.cmb_student_drop.grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(drop, text='From Course ID').grid(row=0, column=2, padx=4, pady=4, sticky='w')
        self.cmb_course_drop = ttk.Combobox(drop, textvariable=self.var_course_drop, width=20, state='readonly')
        self.cmb_course_drop.grid(row=0, column=3, padx=4, pady=4)
        ttk.Button(drop, text='Drop', command=self._drop_student).grid(row=0, column=4, padx=6, pady=4)
        ttk.Label(drop, text='Unassign Instructor from Course ID').grid(row=1, column=0, padx=4, pady=8, sticky='w')
        self.cmb_course_unassign = ttk.Combobox(drop, textvariable=self.var_course_unassign, width=20, state='readonly')
        self.cmb_course_unassign.grid(row=1, column=1, padx=4, pady=8)
        ttk.Button(drop, text='Unassign', command=self._unassign_instructor).grid(row=1, column=2, padx=6, pady=8)

    def _fill_relation_dd(self):
        '''""" fill relation dd.

"""'''
        self.cmb_student['values'] = [s.student_id for s in self.db.list_students()]
        self.cmb_student_drop['values'] = [s.student_id for s in self.db.list_students()]
        self.cmb_instructor['values'] = [i.instructor_id for i in self.db.list_instructors()]
        cids = [c.course_id for c in self.db.list_courses()]
        self.cmb_course_enroll['values'] = cids
        self.cmb_course_assign['values'] = cids
        self.cmb_course_drop['values'] = cids
        self.cmb_course_unassign['values'] = cids

    def _enroll_student(self):
        '''""" enroll student.

"""'''
        sid = self.var_student.get()
        cid = self.var_course_enroll.get()
        if not sid or not cid:
            return messagebox.showerror('Missing', 'Select student and course')
        try:
            self.db.enroll_student_in_course(sid, cid)
            messagebox.showinfo('Enrolled', f'{sid} → {cid}')
            self._refresh_all()
        except ValidationError as e:
            messagebox.showerror('Enroll error', str(e))

    def _assign_instructor(self):
        '''""" assign instructor.

"""'''
        iid = self.var_instructor.get()
        cid = self.var_course_assign.get()
        if not iid or not cid:
            return messagebox.showerror('Missing', 'Select instructor and course')
        try:
            self.db.assign_instructor_to_course(iid, cid)
            messagebox.showinfo('Assigned', f'{iid} → {cid}')
            self._refresh_all()
        except ValidationError as e:
            messagebox.showerror('Assign error', str(e))

    def _drop_student(self):
        '''""" drop student.

"""'''
        sid = self.var_student_drop.get()
        cid = self.var_course_drop.get()
        if not sid or not cid:
            return messagebox.showerror('Missing', 'Select student and course')
        try:
            self.db.drop_student_from_course(sid, cid)
            messagebox.showinfo('Dropped', f'{sid} ✕ {cid}')
            self._refresh_all()
        except ValidationError as e:
            messagebox.showerror('Drop error', str(e))

    def _unassign_instructor(self):
        '''""" unassign instructor.

"""'''
        cid = self.var_course_unassign.get()
        if not cid:
            return messagebox.showerror('Missing', 'Select a course')
        try:
            self.db.unassign_instructor_from_course(cid)
            messagebox.showinfo('Unassigned', f'Cleared instructor for {cid}')
            self._refresh_all()
        except ValidationError as e:
            messagebox.showerror('Unassign error', str(e))

    def _apply_search(self):
        '''""" apply search.

"""'''
        q = self.var_search.get().strip()
        scope = self.var_search_scope.get()
        if scope == 'Students':
            self._refresh_students(q)
        elif scope == 'Instructors':
            self._refresh_instructors(q)
        else:
            self._refresh_courses(q)

    def _clear_search(self):
        '''""" clear search.

"""'''
        self.var_search.set('')
        self._apply_search()

    def _refresh_all(self):
        '''""" refresh all.

"""'''
        self._refresh_students()
        self._refresh_instructors()
        self._refresh_courses()
        self._fill_relation_dd()

    def _toggle_auto_refresh(self):
        '''""" toggle auto refresh.

"""'''
        if self._auto_refresh_enabled.get():
            self._schedule_auto_refresh()
        else:
            self._cancel_auto_refresh()

    def _schedule_auto_refresh(self):
        '''""" schedule auto refresh.

"""'''
        self._refresh_all()
        self._auto_refresh_job = self.after(2000, self._schedule_auto_refresh)

    def _cancel_auto_refresh(self):
        '''""" cancel auto refresh.

"""'''
        if self._auto_refresh_job is not None:
            try:
                self.after_cancel(self._auto_refresh_job)
            except Exception:
                pass
            self._auto_refresh_job = None

    def on_close(self):
        '''"""Gracefully handle application shutdown and resource cleanup.

"""'''
        try:
            self._cancel_auto_refresh()
            self.db.close()
        finally:
            self.destroy()
if __name__ == '__main__':
    App().mainloop()