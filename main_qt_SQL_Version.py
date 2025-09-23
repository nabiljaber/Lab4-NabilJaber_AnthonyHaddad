'''"""
PyQt Desktop Application (SQLite Version) — School Management System

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
import sys
import csv
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QGroupBox, QSpinBox, QCheckBox, QToolBar
from db_store import DBStore
from person import ValidationError

class MainWindow(QMainWindow):
    """Top-level PyQt window organizing tabs and toolbars for managing students, instructors, courses, and relations."""

    def __init__(self):
        '''"""  init  .

"""'''
        super().__init__()
        self.setWindowTitle('School Management System (SQLite, PyQt5)')
        self.resize(1120, 720)
        self.db = DBStore()
        self.sel_student_id = None
        self.sel_instructor_id = None
        self.sel_course_id = None
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self._build_toolbar()
        self._build_students_tab()
        self._build_instructors_tab()
        self._build_courses_tab()
        self._build_relations_tab()
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.refresh_all)
        self.refresh_all()

    def _build_toolbar(self):
        '''"""Construct the application toolbar.

"""'''
        tb = QToolBar('Main')
        self.addToolBar(tb)
        btn_backup = QPushButton('Backup DB')
        btn_backup.clicked.connect(self._backup)
        tb.addWidget(btn_backup)
        btn_export = QPushButton('Export CSV')
        btn_export.clicked.connect(self._export_csv)
        tb.addWidget(btn_export)
        tb.addSeparator()
        tb.addWidget(QLabel('  Search: '))
        self.txt_search = QLineEdit()
        self.txt_search.setFixedWidth(280)
        self.txt_search.textChanged.connect(self._apply_search)
        tb.addWidget(self.txt_search)
        tb.addWidget(QLabel(' in '))
        self.cmb_scope = QComboBox()
        self.cmb_scope.addItems(['Students', 'Instructors', 'Courses'])
        self.cmb_scope.currentIndexChanged.connect(self._apply_search)
        tb.addWidget(self.cmb_scope)
        btn_clear = QPushButton('Clear')
        btn_clear.clicked.connect(self._clear_search)
        tb.addWidget(btn_clear)
        tb.addSeparator()
        self.chk_auto = QCheckBox('Auto-Refresh')
        self.chk_auto.toggled.connect(self._toggle_auto_refresh)
        tb.addWidget(self.chk_auto)

    def _backup(self):
        '''""" backup.

"""'''
        path, _ = QFileDialog.getSaveFileName(self, 'Backup DB', '', 'SQLite DB (*.db)')
        if not path:
            return
        try:
            self.db.backup_db(path)
            QMessageBox.information(self, 'Backup', f'Database copied to:\n{path}')
        except Exception as e:
            QMessageBox.critical(self, 'Backup error', str(e))

    def _export_csv(self):
        '''""" export csv.

"""'''
        folder = QFileDialog.getExistingDirectory(self, 'Choose folder to export CSV files')
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
            QMessageBox.information(self, 'Exported', f'CSV files saved to:\n{folder}')
        except Exception as e:
            QMessageBox.critical(self, 'Export error', str(e))

    def _toggle_auto_refresh(self, checked: bool):
        '''    """ toggle auto refresh.

Parameters:
    checked: parameter.
    """'''
        if checked:
            self.refresh_all()
            self.timer.start()
        else:
            self.timer.stop()

    def _build_students_tab(self):
        '''""" build students tab.

"""'''
        page = QWidget()
        v = QVBoxLayout(page)
        gb = QGroupBox('Student Form')
        vgb = QVBoxLayout(gb)
        grid = QtWidgets.QGridLayout()
        vgb.addLayout(grid)
        self.s_name = QLineEdit()
        self.s_age = QSpinBox()
        self.s_age.setRange(0, 150)
        self.s_email = QLineEdit()
        self.s_id = QLineEdit()
        grid.addWidget(QLabel('Name'), 0, 0)
        grid.addWidget(self.s_name, 0, 1)
        grid.addWidget(QLabel('Age'), 0, 2)
        grid.addWidget(self.s_age, 0, 3)
        grid.addWidget(QLabel('Email'), 1, 0)
        grid.addWidget(self.s_email, 1, 1)
        grid.addWidget(QLabel('Student ID'), 1, 2)
        grid.addWidget(self.s_id, 1, 3)
        h = QHBoxLayout()
        btn_add = QPushButton('Add')
        btn_add.clicked.connect(self._add_student)
        btn_upd = QPushButton('Update')
        btn_upd.clicked.connect(self._update_student)
        btn_del = QPushButton('Delete')
        btn_del.clicked.connect(self._delete_student)
        btn_clr = QPushButton('Clear Form')
        btn_clr.clicked.connect(self._clear_student_form)
        for b in (btn_add, btn_upd, btn_del, btn_clr):
            h.addWidget(b)
        vgb.addLayout(h)
        v.addWidget(gb)
        self.tbl_students = QTableWidget(0, 5)
        self.tbl_students.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Email', 'Courses'])
        self.tbl_students.horizontalHeader().setStretchLastSection(True)
        self.tbl_students.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_students.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_students.itemSelectionChanged.connect(self._on_student_select)
        v.addWidget(self.tbl_students)
        self.tabs.addTab(page, 'Students')

    def _add_student(self):
        '''""" add student.

"""'''
        try:
            self.db.add_student(self.s_name.text(), int(self.s_age.value()), self.s_email.text(), self.s_id.text())
            QMessageBox.information(self, 'Success', 'Student added')
            self._clear_student_form()
            self.refresh_all()
        except (ValidationError, ValueError) as e:
            QMessageBox.critical(self, 'Add error', str(e))

    def _update_student(self):
        '''""" update student.

"""'''
        if not self.sel_student_id:
            QMessageBox.critical(self, 'No selection', 'Select a student')
            return
        try:
            self.db.update_student(self.sel_student_id, name=self.s_name.text(), age=int(self.s_age.value()), email=self.s_email.text())
            QMessageBox.information(self, 'Updated', 'Student updated')
            self.refresh_all()
        except (ValidationError, ValueError) as e:
            QMessageBox.critical(self, 'Update error', str(e))

    def _delete_student(self):
        '''""" delete student.

"""'''
        if not self.sel_student_id:
            QMessageBox.critical(self, 'No selection', 'Select a student')
            return
        if QMessageBox.question(self, 'Confirm', f'Delete student {self.sel_student_id}?') != QMessageBox.Yes:
            return
        self.db.delete_student(self.sel_student_id)
        self._clear_student_form()
        self.refresh_all()

    def _clear_student_form(self):
        '''""" clear student form.

"""'''
        self.sel_student_id = None
        self.s_name.clear()
        self.s_age.setValue(0)
        self.s_email.clear()
        self.s_id.clear()

    def _on_student_select(self):
        '''""" on student select.

"""'''
        rows = self.tbl_students.selectionModel().selectedRows()
        if not rows:
            return
        r = rows[0].row()
        sid = self.tbl_students.item(r, 0).text()
        name = self.tbl_students.item(r, 1).text()
        age = int(self.tbl_students.item(r, 2).text())
        email = self.tbl_students.item(r, 3).text()
        self.sel_student_id = sid
        self.s_id.setText(sid)
        self.s_name.setText(name)
        self.s_age.setValue(age)
        self.s_email.setText(email)

    def _refresh_students(self, filter_text: str=''):
        '''    """ refresh students.

Parameters:
    filter_text: parameter.
    """'''
        ft = (filter_text or '').lower()
        data = []
        for s in self.db.list_students():
            courses = ', '.join(self.db.student_courses(s.student_id)) or 'None'
            row = (s.student_id, s.name, str(s.age), s.email, courses)
            if not ft or any((ft in str(x).lower() for x in row)):
                data.append(row)
        self.tbl_students.setRowCount(0)
        for row in data:
            r = self.tbl_students.rowCount()
            self.tbl_students.insertRow(r)
            for c, val in enumerate(row):
                self.tbl_students.setItem(r, c, QTableWidgetItem(val))

    def _build_instructors_tab(self):
        '''""" build instructors tab.

"""'''
        page = QWidget()
        v = QVBoxLayout(page)
        gb = QGroupBox('Instructor Form')
        vgb = QVBoxLayout(gb)
        grid = QtWidgets.QGridLayout()
        vgb.addLayout(grid)
        self.i_name = QLineEdit()
        self.i_age = QSpinBox()
        self.i_age.setRange(0, 150)
        self.i_email = QLineEdit()
        self.i_id = QLineEdit()
        grid.addWidget(QLabel('Name'), 0, 0)
        grid.addWidget(self.i_name, 0, 1)
        grid.addWidget(QLabel('Age'), 0, 2)
        grid.addWidget(self.i_age, 0, 3)
        grid.addWidget(QLabel('Email'), 1, 0)
        grid.addWidget(self.i_email, 1, 1)
        grid.addWidget(QLabel('Instructor ID'), 1, 2)
        grid.addWidget(self.i_id, 1, 3)
        h = QHBoxLayout()
        btn_add = QPushButton('Add')
        btn_add.clicked.connect(self._add_instructor)
        btn_upd = QPushButton('Update')
        btn_upd.clicked.connect(self._update_instructor)
        btn_del = QPushButton('Delete')
        btn_del.clicked.connect(self._delete_instructor)
        btn_clr = QPushButton('Clear Form')
        btn_clr.clicked.connect(self._clear_instructor_form)
        for b in (btn_add, btn_upd, btn_del, btn_clr):
            h.addWidget(b)
        vgb.addLayout(h)
        v.addWidget(gb)
        self.tbl_instructors = QTableWidget(0, 5)
        self.tbl_instructors.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Email', 'Courses'])
        self.tbl_instructors.horizontalHeader().setStretchLastSection(True)
        self.tbl_instructors.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_instructors.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_instructors.itemSelectionChanged.connect(self._on_instructor_select)
        v.addWidget(self.tbl_instructors)
        self.tabs.addTab(page, 'Instructors')

    def _add_instructor(self):
        '''""" add instructor.

"""'''
        try:
            self.db.add_instructor(self.i_name.text(), int(self.i_age.value()), self.i_email.text(), self.i_id.text())
            QMessageBox.information(self, 'Success', 'Instructor added')
            self._clear_instructor_form()
            self.refresh_all()
        except (ValidationError, ValueError) as e:
            QMessageBox.critical(self, 'Add error', str(e))

    def _update_instructor(self):
        '''""" update instructor.

"""'''
        if not self.sel_instructor_id:
            QMessageBox.critical(self, 'No selection', 'Select an instructor')
            return
        try:
            self.db.update_instructor(self.sel_instructor_id, name=self.i_name.text(), age=int(self.i_age.value()), email=self.i_email.text())
            QMessageBox.information(self, 'Updated', 'Instructor updated')
            self.refresh_all()
        except (ValidationError, ValueError) as e:
            QMessageBox.critical(self, 'Update error', str(e))

    def _delete_instructor(self):
        '''""" delete instructor.

"""'''
        if not self.sel_instructor_id:
            QMessageBox.critical(self, 'No selection', 'Select an instructor')
            return
        if QMessageBox.question(self, 'Confirm', f'Delete instructor {self.sel_instructor_id}?') != QMessageBox.Yes:
            return
        self.db.delete_instructor(self.sel_instructor_id)
        self._clear_instructor_form()
        self.refresh_all()

    def _clear_instructor_form(self):
        '''""" clear instructor form.

"""'''
        self.sel_instructor_id = None
        self.i_name.clear()
        self.i_age.setValue(0)
        self.i_email.clear()
        self.i_id.clear()

    def _on_instructor_select(self):
        '''""" on instructor select.

"""'''
        rows = self.tbl_instructors.selectionModel().selectedRows()
        if not rows:
            return
        r = rows[0].row()
        iid = self.tbl_instructors.item(r, 0).text()
        name = self.tbl_instructors.item(r, 1).text()
        age = int(self.tbl_instructors.item(r, 2).text())
        email = self.tbl_instructors.item(r, 3).text()
        self.sel_instructor_id = iid
        self.i_id.setText(iid)
        self.i_name.setText(name)
        self.i_age.setValue(age)
        self.i_email.setText(email)

    def _refresh_instructors(self, filter_text: str=''):
        '''    """ refresh instructors.

Parameters:
    filter_text: parameter.
    """'''
        ft = (filter_text or '').lower()
        data = []
        all_courses = self.db.list_courses()
        for i in self.db.list_instructors():
            course_ids = [c.course_id for c in all_courses if c.instructor_id == i.instructor_id]
            row = (i.instructor_id, i.name, str(i.age), i.email, ', '.join(course_ids) or 'None')
            if not ft or any((ft in str(x).lower() for x in row)):
                data.append(row)
        self.tbl_instructors.setRowCount(0)
        for row in data:
            r = self.tbl_instructors.rowCount()
            self.tbl_instructors.insertRow(r)
            for c, val in enumerate(row):
                self.tbl_instructors.setItem(r, c, QTableWidgetItem(val))

    def _build_courses_tab(self):
        '''""" build courses tab.

"""'''
        page = QWidget()
        v = QVBoxLayout(page)
        gb = QGroupBox('Course Form')
        vgb = QVBoxLayout(gb)
        grid = QtWidgets.QGridLayout()
        vgb.addLayout(grid)
        self.c_id = QLineEdit()
        self.c_name = QLineEdit()
        grid.addWidget(QLabel('Course ID'), 0, 0)
        grid.addWidget(self.c_id, 0, 1)
        grid.addWidget(QLabel('Course Name'), 0, 2)
        grid.addWidget(self.c_name, 0, 3)
        h = QHBoxLayout()
        btn_add = QPushButton('Add')
        btn_add.clicked.connect(self._add_course)
        btn_upd = QPushButton('Update Name')
        btn_upd.clicked.connect(self._update_course)
        btn_del = QPushButton('Delete')
        btn_del.clicked.connect(self._delete_course)
        btn_clr = QPushButton('Clear Form')
        btn_clr.clicked.connect(self._clear_course_form)
        for b in (btn_add, btn_upd, btn_del, btn_clr):
            h.addWidget(b)
        vgb.addLayout(h)
        v.addWidget(gb)
        self.tbl_courses = QTableWidget(0, 4)
        self.tbl_courses.setHorizontalHeaderLabels(['ID', 'Name', 'Instructor', 'Students'])
        self.tbl_courses.horizontalHeader().setStretchLastSection(True)
        self.tbl_courses.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_courses.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_courses.itemSelectionChanged.connect(self._on_course_select)
        v.addWidget(self.tbl_courses)
        self.tabs.addTab(page, 'Courses')

    def _add_course(self):
        '''""" add course.

"""'''
        try:
            self.db.add_course(self.c_id.text(), self.c_name.text())
            QMessageBox.information(self, 'Success', 'Course added')
            self._clear_course_form()
            self.refresh_all()
        except ValidationError as e:
            QMessageBox.critical(self, 'Add error', str(e))

    def _update_course(self):
        '''""" update course.

"""'''
        if not self.sel_course_id:
            QMessageBox.critical(self, 'No selection', 'Select a course')
            return
        try:
            self.db.update_course_name(self.sel_course_id, self.c_name.text())
            QMessageBox.information(self, 'Updated', 'Course renamed')
            self.refresh_all()
        except ValidationError as e:
            QMessageBox.critical(self, 'Update error', str(e))

    def _delete_course(self):
        '''""" delete course.

"""'''
        if not self.sel_course_id:
            QMessageBox.critical(self, 'No selection', 'Select a course')
            return
        if QMessageBox.question(self, 'Confirm', f'Delete course {self.sel_course_id}?') != QMessageBox.Yes:
            return
        self.db.delete_course(self.sel_course_id)
        self._clear_course_form()
        self.refresh_all()

    def _clear_course_form(self):
        '''""" clear course form.

"""'''
        self.sel_course_id = None
        self.c_id.clear()
        self.c_name.clear()

    def _on_course_select(self):
        '''""" on course select.

"""'''
        rows = self.tbl_courses.selectionModel().selectedRows()
        if not rows:
            return
        r = rows[0].row()
        cid = self.tbl_courses.item(r, 0).text()
        name = self.tbl_courses.item(r, 1).text()
        self.sel_course_id = cid
        self.c_id.setText(cid)
        self.c_name.setText(name)

    def _refresh_courses(self, filter_text: str=''):
        '''    """ refresh courses.

Parameters:
    filter_text: parameter.
    """'''
        ft = (filter_text or '').lower()
        data = []
        for c in self.db.list_courses():
            ins = c.instructor_id or 'None'
            students = ', '.join(self.db.course_students(c.course_id)) or 'None'
            row = (c.course_id, c.course_name, ins, students)
            if not ft or any((ft in str(x).lower() for x in row)):
                data.append(row)
        self.tbl_courses.setRowCount(0)
        for row in data:
            r = self.tbl_courses.rowCount()
            self.tbl_courses.insertRow(r)
            for c, val in enumerate(row):
                self.tbl_courses.setItem(r, c, QTableWidgetItem(val))

    def _build_relations_tab(self):
        '''""" build relations tab.

"""'''
        page = QWidget()
        v = QVBoxLayout(page)
        gb_enroll = QGroupBox('Enroll Student in Course')
        ge = QtWidgets.QGridLayout(gb_enroll)
        self.cmb_student = QComboBox()
        self.cmb_course_enroll = QComboBox()
        ge.addWidget(QLabel('Student ID'), 0, 0)
        ge.addWidget(self.cmb_student, 0, 1)
        ge.addWidget(QLabel('Course ID'), 0, 2)
        ge.addWidget(self.cmb_course_enroll, 0, 3)
        btn_enroll = QPushButton('Enroll')
        btn_enroll.clicked.connect(self._enroll_student)
        ge.addWidget(btn_enroll, 0, 4)
        v.addWidget(gb_enroll)
        gb_assign = QGroupBox('Assign Instructor to Course')
        ga = QtWidgets.QGridLayout(gb_assign)
        self.cmb_instructor = QComboBox()
        self.cmb_course_assign = QComboBox()
        ga.addWidget(QLabel('Instructor ID'), 0, 0)
        ga.addWidget(self.cmb_instructor, 0, 1)
        ga.addWidget(QLabel('Course ID'), 0, 2)
        ga.addWidget(self.cmb_course_assign, 0, 3)
        btn_assign = QPushButton('Assign')
        btn_assign.clicked.connect(self._assign_instructor)
        ga.addWidget(btn_assign, 0, 4)
        v.addWidget(gb_assign)
        gb_drop = QGroupBox('Drop / Unassign')
        gd = QtWidgets.QGridLayout(gb_drop)
        self.cmb_student_drop = QComboBox()
        self.cmb_course_drop = QComboBox()
        self.cmb_course_unassign = QComboBox()
        gd.addWidget(QLabel('Drop Student ID'), 0, 0)
        gd.addWidget(self.cmb_student_drop, 0, 1)
        gd.addWidget(QLabel('From Course ID'), 0, 2)
        gd.addWidget(self.cmb_course_drop, 0, 3)
        btn_drop = QPushButton('Drop')
        btn_drop.clicked.connect(self._drop_student)
        gd.addWidget(btn_drop, 0, 4)
        gd.addWidget(QLabel('Unassign Instructor from Course ID'), 1, 0)
        gd.addWidget(self.cmb_course_unassign, 1, 1)
        btn_unassign = QPushButton('Unassign')
        btn_unassign.clicked.connect(self._unassign_instructor)
        gd.addWidget(btn_unassign, 1, 2)
        v.addWidget(gb_drop)
        self.tabs.addTab(page, 'Relations')

    def _fill_relation_dd(self):
        '''""" fill relation dd.

"""'''
        self.cmb_student.clear()
        self.cmb_student_drop.clear()
        self.cmb_instructor.clear()
        self.cmb_course_enroll.clear()
        self.cmb_course_assign.clear()
        self.cmb_course_drop.clear()
        self.cmb_course_unassign.clear()
        self.cmb_student.addItems([s.student_id for s in self.db.list_students()])
        self.cmb_student_drop.addItems([s.student_id for s in self.db.list_students()])
        self.cmb_instructor.addItems([i.instructor_id for i in self.db.list_instructors()])
        cids = [c.course_id for c in self.db.list_courses()]
        for cmb in (self.cmb_course_enroll, self.cmb_course_assign, self.cmb_course_drop, self.cmb_course_unassign):
            cmb.addItems(cids)

    def _enroll_student(self):
        '''""" enroll student.

"""'''
        sid = self.cmb_student.currentText()
        cid = self.cmb_course_enroll.currentText()
        if not sid or not cid:
            QMessageBox.critical(self, 'Missing', 'Select student and course')
            return
        try:
            self.db.enroll_student_in_course(sid, cid)
            QMessageBox.information(self, 'Enrolled', f'{sid} → {cid}')
            self.refresh_all()
        except ValidationError as e:
            QMessageBox.critical(self, 'Enroll error', str(e))

    def _assign_instructor(self):
        '''""" assign instructor.

"""'''
        iid = self.cmb_instructor.currentText()
        cid = self.cmb_course_assign.currentText()
        if not iid or not cid:
            QMessageBox.critical(self, 'Missing', 'Select instructor and course')
            return
        try:
            self.db.assign_instructor_to_course(iid, cid)
            QMessageBox.information(self, 'Assigned', f'{iid} → {cid}')
            self.refresh_all()
        except ValidationError as e:
            QMessageBox.critical(self, 'Assign error', str(e))

    def _drop_student(self):
        '''""" drop student.

"""'''
        sid = self.cmb_student_drop.currentText()
        cid = self.cmb_course_drop.currentText()
        if not sid or not cid:
            QMessageBox.critical(self, 'Missing', 'Select student and course')
            return
        try:
            self.db.drop_student_from_course(sid, cid)
            QMessageBox.information(self, 'Dropped', f'{sid} ✕ {cid}')
            self.refresh_all()
        except ValidationError as e:
            QMessageBox.critical(self, 'Drop error', str(e))

    def _unassign_instructor(self):
        '''""" unassign instructor.

"""'''
        cid = self.cmb_course_unassign.currentText()
        if not cid:
            QMessageBox.critical(self, 'Missing', 'Select a course')
            return
        try:
            self.db.unassign_instructor_from_course(cid)
            QMessageBox.information(self, 'Unassigned', f'Cleared instructor for {cid}')
            self.refresh_all()
        except ValidationError as e:
            QMessageBox.critical(self, 'Unassign error', str(e))

    def _apply_search(self):
        '''""" apply search.

"""'''
        q = (self.txt_search.text() or '').strip().lower()
        scope = self.cmb_scope.currentText()
        if scope == 'Students':
            self._refresh_students(q)
        elif scope == 'Instructors':
            self._refresh_instructors(q)
        else:
            self._refresh_courses(q)

    def _clear_search(self):
        '''""" clear search.

"""'''
        self.txt_search.clear()
        self._apply_search()

    def refresh_all(self):
        '''"""Refresh all.

"""'''
        self._refresh_students()
        self._refresh_instructors()
        self._refresh_courses()
        self._fill_relation_dd()

    def closeEvent(self, event: QtGui.QCloseEvent):
        '''    """Closeevent.

Parameters:
    event: parameter.
    """'''
        try:
            if self.timer.isActive():
                self.timer.stop()
            self.db.close()
        finally:
            event.accept()

def main():
    '''"""Main.

"""'''
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()