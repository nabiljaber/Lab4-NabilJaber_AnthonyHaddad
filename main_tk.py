'''"""
Tkinter Desktop Application — School Management System

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
import csv, json
from db_store import DBStore as DataStore
from person import ValidationError

class App(tk.Tk):
    """Top-level Tkinter GUI application that provides tabs for Students, Instructors, Courses, and Relations."""

    def __init__(self):
        '''"""  init  .

"""'''
        super().__init__()
        self.title('School Management System')
        self.geometry('1100x680')
        self.ds = DataStore()
        self.sel_student_id = None
        self.sel_instructor_id = None
        self.sel_course_id = None
        self.build_toolbar()
        self.build_tabs()
        self.refresh_all()
        self.protocol('WM_DELETE_WINDOW', self.on_close)

    def build_toolbar(self):
        '''"""Construct the application toolbar.

"""'''
        bar = ttk.Frame(self, padding=(6, 6))
        bar.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(bar, text='Save JSON', command=self.save_json).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text='Load JSON', command=self.load_json).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text='Export CSV', command=self.export_csv).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text='Reload DB', command=self.reload_all).pack(side=tk.LEFT, padx=12)
        ttk.Label(bar, text='Search:').pack(side=tk.LEFT, padx=(12, 4))
        self.var_search = tk.StringVar()
        ent = ttk.Entry(bar, textvariable=self.var_search, width=32)
        ent.pack(side=tk.LEFT, padx=4)
        ent.bind('<KeyRelease>', lambda e: self.apply_search())
        ttk.Label(bar, text=' in ').pack(side=tk.LEFT)
        self.var_search_scope = tk.StringVar(value='Students')
        ttk.Combobox(bar, textvariable=self.var_search_scope, values=['Students', 'Instructors', 'Courses'], width=12, state='readonly').pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text='Clear', command=self.clear_search).pack(side=tk.LEFT, padx=4)

    def build_tabs(self):
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
        self.build_students_tab()
        self.build_instructors_tab()
        self.build_courses_tab()
        self.build_relations_tab()

    def build_students_tab(self):
        '''"""Build students tab.

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
        ttk.Button(btns, text='Add', command=self.add_student).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Update', command=self.update_student).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Delete', command=self.delete_student).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Clear Form', command=self.clear_student_form).pack(side=tk.LEFT, padx=8)
        cols = ('id', 'name', 'age', 'email', 'courses')
        self.tree_students = ttk.Treeview(frm, columns=cols, show='headings', height=12)
        for c, w in zip(cols, (110, 180, 60, 220, 360)):
            self.tree_students.heading(c, text=c.capitalize())
            self.tree_students.column(c, width=w, anchor='w')
        self.tree_students.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.tree_students.bind('<<TreeviewSelect>>', self.on_student_select)

    def add_student(self):
        '''"""Add a new student to the store or current view.

"""'''
        try:
            age_val = int(self.s_age.get())
            self.ds.add_student(self.s_name.get(), age_val, self.s_email.get(), self.s_id.get())
            messagebox.showinfo('Success', 'Student added.')
            self.clear_student_form()
            self.refresh_students()
        except (ValidationError, ValueError) as e:
            messagebox.showerror('Error adding student', str(e))

    def update_student(self):
        '''"""Update an existing student's attributes.

"""'''
        sid = self.sel_student_id
        if not sid:
            messagebox.showerror('No selection', 'Select a student from the table.')
            return
        try:
            age_val = int(self.s_age.get())
            self.ds.update_student(sid, name=self.s_name.get(), age=age_val, email=self.s_email.get())
            messagebox.showinfo('Updated', f'Student {sid} updated.')
            self.refresh_students()
        except (ValidationError, ValueError) as e:
            messagebox.showerror('Update error', str(e))

    def delete_student(self):
        '''"""Remove a student from the store or current view.

"""'''
        sid = self.sel_student_id
        if not sid:
            messagebox.showerror('No selection', 'Select a student from the table.')
            return
        if not messagebox.askyesno('Confirm', f'Delete student {sid}?'):
            return
        self.ds.delete_student(sid)
        self.clear_student_form()
        self.refresh_all()

    def clear_student_form(self):
        '''"""Clear student form.

"""'''
        self.sel_student_id = None
        self.s_name.set('')
        self.s_age.set('')
        self.s_email.set('')
        self.s_id.set('')

    def on_student_select(self, _):
        '''    """On student select.

Parameters:
    _: parameter.
    """'''
        item = self.tree_students.selection()
        if not item:
            return
        vals = self.tree_students.item(item[0], 'values')
        sid, name, age, email, _courses = vals
        self.sel_student_id = sid
        self.s_id.set(sid)
        self.s_name.set(name)
        self.s_age.set(age)
        self.s_email.set(email)

    def refresh_students(self, filter_text: str=''):
        '''    """Refresh students.

Parameters:
    filter_text: parameter.
    """'''
        self.tree_students.delete(*self.tree_students.get_children())
        ft = filter_text.lower()
        for r in self.ds.list_students():
            courses = ', '.join(self.ds.student_courses(r.student_id)) or 'None'
            row = (r.student_id, r.name, r.age, r.email, courses)
            if not ft or any((ft in str(x).lower() for x in row)):
                self.tree_students.insert('', tk.END, values=row)

    def build_instructors_tab(self):
        '''"""Build instructors tab.

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
        ttk.Button(btns, text='Add', command=self.add_instructor).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Update', command=self.update_instructor).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Delete', command=self.delete_instructor).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Clear Form', command=self.clear_instructor_form).pack(side=tk.LEFT, padx=8)
        cols = ('id', 'name', 'age', 'email', 'courses')
        self.tree_instructors = ttk.Treeview(frm, columns=cols, show='headings', height=12)
        for c, w in zip(cols, (120, 180, 60, 220, 360)):
            self.tree_instructors.heading(c, text=c.capitalize())
            self.tree_instructors.column(c, width=w, anchor='w')
        self.tree_instructors.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.tree_instructors.bind('<<TreeviewSelect>>', self.on_instructor_select)

    def add_instructor(self):
        '''"""Add a new instructor to the store or current view.

"""'''
        try:
            age_val = int(self.i_age.get())
            self.ds.add_instructor(self.i_name.get(), age_val, self.i_email.get(), self.i_id.get())
            messagebox.showinfo('Success', 'Instructor added.')
            self.clear_instructor_form()
            self.refresh_instructors()
        except (ValidationError, ValueError) as e:
            messagebox.showerror('Error adding instructor', str(e))

    def update_instructor(self):
        '''"""Update an existing instructor's attributes.

"""'''
        iid = self.sel_instructor_id
        if not iid:
            messagebox.showerror('No selection', 'Select an instructor from the table.')
            return
        try:
            age_val = int(self.i_age.get())
            self.ds.update_instructor(iid, name=self.i_name.get(), age=age_val, email=self.i_email.get())
            messagebox.showinfo('Updated', f'Instructor {iid} updated.')
            self.refresh_instructors()
        except (ValidationError, ValueError) as e:
            messagebox.showerror('Update error', str(e))

    def delete_instructor(self):
        '''"""Remove an instructor from the store or current view.

"""'''
        iid = self.sel_instructor_id
        if not iid:
            messagebox.showerror('No selection', 'Select an instructor from the table.')
            return
        if not messagebox.askyesno('Confirm', f'Delete instructor {iid}?'):
            return
        self.ds.delete_instructor(iid)
        self.clear_instructor_form()
        self.refresh_all()

    def clear_instructor_form(self):
        '''"""Clear instructor form.

"""'''
        self.sel_instructor_id = None
        self.i_name.set('')
        self.i_age.set('')
        self.i_email.set('')
        self.i_id.set('')

    def on_instructor_select(self, _):
        '''    """On instructor select.

Parameters:
    _: parameter.
    """'''
        item = self.tree_instructors.selection()
        if not item:
            return
        vals = self.tree_instructors.item(item[0], 'values')
        iid, name, age, email, _courses = vals
        self.sel_instructor_id = iid
        self.i_id.set(iid)
        self.i_name.set(name)
        self.i_age.set(age)
        self.i_email.set(email)

    def refresh_instructors(self, filter_text: str=''):
        '''    """Refresh instructors.

Parameters:
    filter_text: parameter.
    """'''
        self.tree_instructors.delete(*self.tree_instructors.get_children())
        ft = filter_text.lower()
        for r in self.ds.list_instructors():
            row = (r.instructor_id, r.name, r.age, r.email, '—')
            if not ft or any((ft in str(x).lower() for x in row)):
                self.tree_instructors.insert('', tk.END, values=row)

    def build_courses_tab(self):
        '''"""Build courses tab.

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
        ttk.Button(btns, text='Add', command=self.add_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Update Name', command=self.update_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Delete', command=self.delete_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text='Clear Form', command=self.clear_course_form).pack(side=tk.LEFT, padx=8)
        cols = ('id', 'name', 'instructor', 'students')
        self.tree_courses = ttk.Treeview(frm, columns=cols, show='headings', height=12)
        for c, w in zip(cols, (120, 260, 160, 460)):
            self.tree_courses.heading(c, text=c.capitalize())
            self.tree_courses.column(c, width=w, anchor='w')
        self.tree_courses.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.tree_courses.bind('<<TreeviewSelect>>', self.on_course_select)

    def add_course(self):
        '''"""Create a course record.

"""'''
        try:
            self.ds.add_course(self.c_id.get(), self.c_name.get())
            messagebox.showinfo('Success', 'Course added.')
            self.clear_course_form()
            self.refresh_courses()
        except ValidationError as e:
            messagebox.showerror('Error adding course', str(e))

    def update_course(self):
        '''"""Update an existing course record.

"""'''
        cid = self.sel_course_id
        if not cid:
            messagebox.showerror('No selection', 'Select a course from the table.')
            return
        name = self.c_name.get().strip()
        if not name:
            messagebox.showerror('Invalid', 'Course name cannot be empty.')
            return
        self.ds.update_course_name(cid, name)
        messagebox.showinfo('Updated', f'Course {cid} renamed.')
        self.refresh_all()

    def delete_course(self):
        '''"""Delete a course record.

"""'''
        cid = self.sel_course_id
        if not cid:
            messagebox.showerror('No selection', 'Select a course from the table.')
            return
        if not messagebox.askyesno('Confirm', f'Delete course {cid}?'):
            return
        self.ds.delete_course(cid)
        self.clear_course_form()
        self.refresh_all()

    def clear_course_form(self):
        '''"""Clear course form.

"""'''
        self.sel_course_id = None
        self.c_id.set('')
        self.c_name.set('')

    def on_course_select(self, _):
        '''    """On course select.

Parameters:
    _: parameter.
    """'''
        item = self.tree_courses.selection()
        if not item:
            return
        vals = self.tree_courses.item(item[0], 'values')
        cid, name, instr, _students = vals
        self.sel_course_id = cid
        self.c_id.set(cid)
        self.c_name.set(name)

    def refresh_courses(self, filter_text: str=''):
        '''    """Refresh courses.

Parameters:
    filter_text: parameter.
    """'''
        self.tree_courses.delete(*self.tree_courses.get_children())
        ft = filter_text.lower()
        for r in self.ds.list_courses():
            ins = r.instructor_id or 'None'
            students = ', '.join(self.ds.course_students(r.course_id)) or 'None'
            row = (r.course_id, r.course_name, ins, students)
            if not ft or any((ft in str(x).lower() for x in row)):
                self.tree_courses.insert('', tk.END, values=row)

    def build_relations_tab(self):
        '''"""Build relations tab.

"""'''
        frm = self.tab_relations
        enroll_box = ttk.LabelFrame(frm, text='Enroll Student in Course', padding=10)
        enroll_box.pack(fill=tk.X, pady=6)
        self.var_student = tk.StringVar()
        self.var_course_for_enroll = tk.StringVar()
        ttk.Label(enroll_box, text='Student ID').grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.cmb_student = ttk.Combobox(enroll_box, textvariable=self.var_student, width=20, state='readonly')
        self.cmb_student.grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(enroll_box, text='Course ID').grid(row=0, column=2, padx=4, pady=4, sticky='w')
        self.cmb_course_enroll = ttk.Combobox(enroll_box, textvariable=self.var_course_for_enroll, width=20, state='readonly')
        self.cmb_course_enroll.grid(row=0, column=3, padx=4, pady=4)
        ttk.Button(enroll_box, text='Enroll', command=self.enroll_student).grid(row=0, column=4, padx=6, pady=4)
        assign_box = ttk.LabelFrame(frm, text='Assign Instructor to Course', padding=10)
        assign_box.pack(fill=tk.X, pady=6)
        self.var_instructor = tk.StringVar()
        self.var_course_for_assign = tk.StringVar()
        ttk.Label(assign_box, text='Instructor ID').grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.cmb_instructor = ttk.Combobox(assign_box, textvariable=self.var_instructor, width=20, state='readonly')
        self.cmb_instructor.grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(assign_box, text='Course ID').grid(row=0, column=2, padx=4, pady=4, sticky='w')
        self.cmb_course_assign = ttk.Combobox(assign_box, textvariable=self.var_course_for_assign, width=20, state='readonly')
        self.cmb_course_assign.grid(row=0, column=3, padx=4, pady=4)
        ttk.Button(assign_box, text='Assign', command=self.assign_instructor).grid(row=0, column=4, padx=6, pady=4)
        drop_box = ttk.LabelFrame(frm, text='Drop / Unassign', padding=10)
        drop_box.pack(fill=tk.X, pady=6)
        self.var_student_drop = tk.StringVar()
        self.var_course_drop = tk.StringVar()
        self.var_course_unassign = tk.StringVar()
        ttk.Label(drop_box, text='Drop Student ID').grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.cmb_student_drop = ttk.Combobox(drop_box, textvariable=self.var_student_drop, width=20, state='readonly')
        self.cmb_student_drop.grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(drop_box, text='From Course ID').grid(row=0, column=2, padx=4, pady=4, sticky='w')
        self.cmb_course_drop = ttk.Combobox(drop_box, textvariable=self.var_course_drop, width=20, state='readonly')
        self.cmb_course_drop.grid(row=0, column=3, padx=4, pady=4)
        ttk.Button(drop_box, text='Drop', command=self.drop_student).grid(row=0, column=4, padx=6, pady=4)
        ttk.Label(drop_box, text='Unassign Instructor from Course ID').grid(row=1, column=0, padx=4, pady=8, sticky='w')
        self.cmb_course_unassign = ttk.Combobox(drop_box, textvariable=self.var_course_unassign, width=20, state='readonly')
        self.cmb_course_unassign.grid(row=1, column=1, padx=4, pady=8)
        ttk.Button(drop_box, text='Unassign', command=self.unassign_instructor).grid(row=1, column=2, padx=6, pady=8)

    def fill_relation_dropdowns(self):
        '''"""Fill relation dropdowns.

"""'''
        s_ids = sorted([r.student_id for r in self.ds.list_students()])
        i_ids = sorted([r.instructor_id for r in self.ds.list_instructors()])
        c_ids = sorted([r.course_id for r in self.ds.list_courses()])
        self.cmb_student['values'] = s_ids
        self.cmb_student_drop['values'] = s_ids
        self.cmb_instructor['values'] = i_ids
        self.cmb_course_enroll['values'] = c_ids
        self.cmb_course_assign['values'] = c_ids
        self.cmb_course_drop['values'] = c_ids
        self.cmb_course_unassign['values'] = c_ids

    def enroll_student(self):
        '''"""Enroll student.

"""'''
        sid = self.var_student.get()
        cid = self.var_course_for_enroll.get()
        if not sid or not cid:
            messagebox.showerror('Missing data', 'Select a student and a course.')
            return
        try:
            self.ds.enroll_student_in_course(sid, cid)
            messagebox.showinfo('Enrolled', f'Student {sid} enrolled in {cid}.')
            self.refresh_all()
        except ValidationError as e:
            messagebox.showerror('Enroll error', str(e))

    def assign_instructor(self):
        '''"""Assign instructor.

"""'''
        iid = self.var_instructor.get()
        cid = self.var_course_for_assign.get()
        if not iid or not cid:
            messagebox.showerror('Missing data', 'Select an instructor and a course.')
            return
        try:
            self.ds.assign_instructor_to_course(iid, cid)
            messagebox.showinfo('Assigned', f'Instructor {iid} assigned to {cid}.')
            self.refresh_all()
        except ValidationError as e:
            messagebox.showerror('Assign error', str(e))

    def drop_student(self):
        '''"""Drop student.

"""'''
        sid = self.var_student_drop.get()
        cid = self.var_course_drop.get()
        if not sid or not cid:
            messagebox.showerror('Missing data', 'Select a student and a course.')
            return
        try:
            self.ds.drop_student_from_course(sid, cid)
            messagebox.showinfo('Dropped', f'Student {sid} dropped from {cid}.')
            self.refresh_all()
        except ValidationError as e:
            messagebox.showerror('Drop error', str(e))

    def unassign_instructor(self):
        '''"""Unassign instructor.

"""'''
        cid = self.var_course_unassign.get()
        if not cid:
            messagebox.showerror('Missing data', 'Select a course.')
            return
        try:
            self.ds.unassign_instructor_from_course(cid)
            messagebox.showinfo('Unassigned', f'Instructor cleared for {cid}.')
            self.refresh_all()
        except ValidationError as e:
            messagebox.showerror('Unassign error', str(e))

    def apply_search(self):
        '''"""Apply search.

"""'''
        q = self.var_search.get().strip()
        scope = self.var_search_scope.get()
        if scope == 'Students':
            self.refresh_students(q)
        elif scope == 'Instructors':
            self.refresh_instructors(q)
        else:
            self.refresh_courses(q)

    def clear_search(self):
        '''"""Clear search.

"""'''
        self.var_search.set('')
        self.apply_search()

    def export_csv(self):
        '''"""Export csv.

"""'''
        folder = filedialog.askdirectory(title='Choose folder to export CSV files')
        if not folder:
            return
        try:
            with open(f'{folder}/students.csv', 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['student_id', 'name', 'age', 'email', 'registered_course_ids'])
                for s in self.ds.list_students():
                    course_ids = self.ds.student_courses(s.student_id)
                    w.writerow([s.student_id, s.name, s.age, s.email, ';'.join(course_ids)])
            with open(f'{folder}/instructors.csv', 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['instructor_id', 'name', 'age', 'email', 'assigned_course_ids'])
                courses = self.ds.list_courses()
                for i in self.ds.list_instructors():
                    assigned = [c.course_id for c in courses if c.instructor_id == i.instructor_id]
                    w.writerow([i.instructor_id, i.name, i.age, i.email, ';'.join(assigned)])
            with open(f'{folder}/courses.csv', 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['course_id', 'course_name', 'instructor_id', 'enrolled_student_ids'])
                for c in self.ds.list_courses():
                    s_ids = self.ds.course_students(c.course_id)
                    w.writerow([c.course_id, c.course_name, c.instructor_id or '', ';'.join(s_ids)])
            messagebox.showinfo('Exported', f'CSV files saved to:\n{folder}')
        except Exception as e:
            messagebox.showerror('Export error', str(e))

    def save_json(self):
        '''"""Save json.

"""'''
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')])
        if not path:
            return
        try:
            from db_store import DBStore
            DBStore.dump_json(self.ds, path)
            messagebox.showinfo('Saved', f'Data exported to JSON:\n{path}')
        except Exception as e:
            messagebox.showerror('Save JSON error', str(e))

    def load_json(self):
        '''"""Load json.

"""'''
        path = filedialog.askopenfilename(filetypes=[('JSON', '*.json')])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for s in data.get('students', []):
                sid = s.get('student_id', '').strip()
                name = s.get('name', '')
                age = int(s.get('age', 0))
                email = s.get('email', '')
                try:
                    self.ds.add_student(name, age, email, sid)
                except ValidationError:
                    self.ds.update_student(sid, name=name, age=age, email=email)
            for i in data.get('instructors', []):
                iid = i.get('instructor_id', '').strip()
                name = i.get('name', '')
                age = int(i.get('age', 0))
                email = i.get('email', '')
                try:
                    self.ds.add_instructor(name, age, email, iid)
                except ValidationError:
                    self.ds.update_instructor(iid, name=name, age=age, email=email)
            for c in data.get('courses', []):
                cid = c.get('course_id', '').strip()
                cname = c.get('course_name', '')
                instr = c.get('instructor_id', None)
                try:
                    self.ds.add_course(cid, cname)
                except ValidationError:
                    self.ds.update_course_name(cid, cname)
                if instr:
                    try:
                        self.ds.assign_instructor_to_course(instr, cid)
                    except ValidationError:
                        pass
            for c in data.get('courses', []):
                cid = c.get('course_id', '').strip()
                for sid in c.get('students', []):
                    try:
                        self.ds.enroll_student_in_course(sid, cid)
                    except ValidationError:
                        pass
            self.refresh_all()
            messagebox.showinfo('Loaded', f'Data loaded from JSON:\n{path}')
        except Exception as e:
            messagebox.showerror('Load JSON error', str(e))

    def reload_all(self):
        '''"""Reload all.

"""'''
        try:
            self.ds.close()
        except:
            pass
        self.ds = DataStore()
        self.refresh_all()
        messagebox.showinfo('Reloaded', 'Re-opened database.')

    def refresh_all(self):
        '''"""Refresh all.

"""'''
        self.refresh_students()
        self.refresh_instructors()
        self.refresh_courses()
        self.fill_relation_dropdowns()

    def on_close(self):
        '''"""Gracefully handle application shutdown and resource cleanup.

"""'''
        try:
            self.ds.close()
        finally:
            self.destroy()
if __name__ == '__main__':
    App().mainloop()