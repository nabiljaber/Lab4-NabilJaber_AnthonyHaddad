'''"""
SQLite Data Access Layer — School Management System

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
from __future__ import annotations
import sqlite3, shutil, re, json
from dataclasses import dataclass
from typing import List, Optional
from person import ValidationError
DB_PATH = 'school.db'

@dataclass
class StudentRow:
    """Typed record representing one row in the students table."""
    student_id: str
    name: str
    age: int
    email: str

@dataclass
class InstructorRow:
    """Typed record representing one row in the instructors table."""
    instructor_id: str
    name: str
    age: int
    email: str

@dataclass
class CourseRow:
    """Typed record representing one row in the courses table."""
    course_id: str
    course_name: str
    instructor_id: Optional[str]

class DBStore:
    """SQLite-backed repository providing CRUD and relation-management utilities for students, instructors, and courses."""

    def __init__(self, db_path: str=DB_PATH):
        '''    """  init  .

Parameters:
    db_path: parameter.
    """'''
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('PRAGMA foreign_keys = ON')
        self._init_schema()

    def _init_schema(self):
        '''""" init schema.

"""'''
        cur = self.conn.cursor()
        cur.execute('\n        CREATE TABLE IF NOT EXISTS students(\n            student_id TEXT PRIMARY KEY,\n            name TEXT NOT NULL,\n            age INTEGER NOT NULL CHECK(age >= 0),\n            email TEXT NOT NULL\n        )')
        cur.execute('\n        CREATE TABLE IF NOT EXISTS instructors(\n            instructor_id TEXT PRIMARY KEY,\n            name TEXT NOT NULL,\n            age INTEGER NOT NULL CHECK(age >= 0),\n            email TEXT NOT NULL\n        )')
        cur.execute('\n        CREATE TABLE IF NOT EXISTS courses(\n            course_id TEXT PRIMARY KEY,\n            course_name TEXT NOT NULL,\n            instructor_id TEXT,\n            FOREIGN KEY(instructor_id) REFERENCES instructors(instructor_id)\n              ON UPDATE CASCADE ON DELETE SET NULL\n        )')
        cur.execute('\n        CREATE TABLE IF NOT EXISTS registrations(\n            student_id TEXT NOT NULL,\n            course_id  TEXT NOT NULL,\n            PRIMARY KEY(student_id, course_id),\n            FOREIGN KEY(student_id) REFERENCES students(student_id)\n              ON UPDATE CASCADE ON DELETE CASCADE,\n            FOREIGN KEY(course_id)  REFERENCES courses(course_id)\n              ON UPDATE CASCADE ON DELETE CASCADE\n        )')
        self.conn.commit()

    def _check_email(self, email: str):
        '''    """ check email.

Parameters:
    email: parameter.
    """'''
        if not isinstance(email, str) or not re.match('^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$', email):
            raise ValidationError(f'Invalid email format: {email}')

    def add_student(self, name: str, age: int, email: str, student_id: str) -> StudentRow:
        '''    """Add a new student to the store or current view.

Parameters:
    name: parameter.
    age: parameter.
    email: parameter.
    student_id: parameter.
    """'''
        if not student_id.strip():
            raise ValidationError('Student ID cannot be empty.')
        if not isinstance(age, int) or age < 0:
            raise ValidationError('Age must be a non-negative integer.')
        self._check_email(email)
        try:
            self.conn.execute('INSERT INTO students(student_id,name,age,email) VALUES(?,?,?,?)', (student_id, name, age, email))
            self.conn.commit()
            return StudentRow(student_id, name, age, email)
        except sqlite3.IntegrityError:
            raise ValidationError(f"Student ID '{student_id}' already exists.")

    def update_student(self, student_id: str, *, name: str, age: int, email: str) -> None:
        '''    """Update an existing student's attributes.

Parameters:
    student_id: parameter.
    """'''
        if not isinstance(age, int) or age < 0:
            raise ValidationError('Age must be a non-negative integer.')
        self._check_email(email)
        cur = self.conn.execute('UPDATE students SET name=?, age=?, email=? WHERE student_id=?', (name, age, email, student_id))
        if cur.rowcount == 0:
            raise ValidationError(f"Unknown student_id '{student_id}'.")
        self.conn.commit()

    def delete_student(self, student_id: str) -> None:
        '''    """Remove a student from the store or current view.

Parameters:
    student_id: parameter.
    """'''
        self.conn.execute('DELETE FROM students WHERE student_id=?', (student_id,))
        self.conn.commit()

    def list_students(self) -> List[StudentRow]:
        '''"""List all students.

"""'''
        cur = self.conn.execute('SELECT student_id,name,age,email FROM students ORDER BY student_id')
        return [StudentRow(*row) for row in cur.fetchall()]

    def add_instructor(self, name: str, age: int, email: str, instructor_id: str) -> InstructorRow:
        '''    """Add a new instructor to the store or current view.

Parameters:
    name: parameter.
    age: parameter.
    email: parameter.
    instructor_id: parameter.
    """'''
        if not instructor_id.strip():
            raise ValidationError('Instructor ID cannot be empty.')
        if not isinstance(age, int) or age < 0:
            raise ValidationError('Age must be a non-negative integer.')
        self._check_email(email)
        try:
            self.conn.execute('INSERT INTO instructors(instructor_id,name,age,email) VALUES(?,?,?,?)', (instructor_id, name, age, email))
            self.conn.commit()
            return InstructorRow(instructor_id, name, age, email)
        except sqlite3.IntegrityError:
            raise ValidationError(f"Instructor ID '{instructor_id}' already exists.")

    def update_instructor(self, instructor_id: str, *, name: str, age: int, email: str) -> None:
        '''    """Update an existing instructor's attributes.

Parameters:
    instructor_id: parameter.
    """'''
        if not isinstance(age, int) or age < 0:
            raise ValidationError('Age must be a non-negative integer.')
        self._check_email(email)
        cur = self.conn.execute('UPDATE instructors SET name=?, age=?, email=? WHERE instructor_id=?', (name, age, email, instructor_id))
        if cur.rowcount == 0:
            raise ValidationError(f"Unknown instructor_id '{instructor_id}'.")
        self.conn.commit()

    def delete_instructor(self, instructor_id: str) -> None:
        '''    """Remove an instructor from the store or current view.

Parameters:
    instructor_id: parameter.
    """'''
        self.conn.execute('DELETE FROM instructors WHERE instructor_id=?', (instructor_id,))
        self.conn.commit()

    def list_instructors(self) -> List[InstructorRow]:
        '''"""List all instructors.

"""'''
        cur = self.conn.execute('SELECT instructor_id,name,age,email FROM instructors ORDER BY instructor_id')
        return [InstructorRow(*row) for row in cur.fetchall()]

    def add_course(self, course_id: str, course_name: str) -> CourseRow:
        '''    """Create a course record.

Parameters:
    course_id: parameter.
    course_name: parameter.
    """'''
        if not course_id.strip():
            raise ValidationError('Course ID cannot be empty.')
        if not course_name.strip():
            raise ValidationError('Course name cannot be empty.')
        try:
            self.conn.execute('INSERT INTO courses(course_id,course_name) VALUES(?,?)', (course_id, course_name))
            self.conn.commit()
            return CourseRow(course_id, course_name, None)
        except sqlite3.IntegrityError:
            raise ValidationError(f"Course ID '{course_id}' already exists.")

    def update_course_name(self, course_id: str, course_name: str) -> None:
        '''    """Update the course name by id.

Parameters:
    course_id: parameter.
    course_name: parameter.
    """'''
        if not course_name.strip():
            raise ValidationError('Course name cannot be empty.')
        cur = self.conn.execute('UPDATE courses SET course_name=? WHERE course_id=?', (course_name, course_id))
        if cur.rowcount == 0:
            raise ValidationError(f"Unknown course_id '{course_id}'.")
        self.conn.commit()

    def delete_course(self, course_id: str) -> None:
        '''    """Delete a course record.

Parameters:
    course_id: parameter.
    """'''
        self.conn.execute('DELETE FROM courses WHERE course_id=?', (course_id,))
        self.conn.commit()

    def list_courses(self) -> List[CourseRow]:
        '''"""List all courses.

"""'''
        cur = self.conn.execute('SELECT course_id,course_name,instructor_id FROM courses ORDER BY course_id')
        return [CourseRow(*row) for row in cur.fetchall()]

    def assign_instructor_to_course(self, instructor_id: str, course_id: str) -> None:
        '''    """Assign an instructor to a course.

Parameters:
    instructor_id: parameter.
    course_id: parameter.
    """'''
        if not self._exists('instructors', 'instructor_id', instructor_id):
            raise ValidationError(f"Unknown instructor_id '{instructor_id}'.")
        if not self._exists('courses', 'course_id', course_id):
            raise ValidationError(f"Unknown course_id '{course_id}'.")
        self.conn.execute('UPDATE courses SET instructor_id=? WHERE course_id=?', (instructor_id, course_id))
        self.conn.commit()

    def unassign_instructor_from_course(self, course_id: str) -> None:
        '''    """Unassign the instructor from a course.

Parameters:
    course_id: parameter.
    """'''
        self.conn.execute('UPDATE courses SET instructor_id=NULL WHERE course_id=?', (course_id,))
        self.conn.commit()

    def enroll_student_in_course(self, student_id: str, course_id: str) -> None:
        '''    """Register a student into a course.

Parameters:
    student_id: parameter.
    course_id: parameter.
    """'''
        if not self._exists('students', 'student_id', student_id):
            raise ValidationError(f"Unknown student_id '{student_id}'.")
        if not self._exists('courses', 'course_id', course_id):
            raise ValidationError(f"Unknown course_id '{course_id}'.")
        try:
            self.conn.execute('INSERT INTO registrations(student_id,course_id) VALUES(?,?)', (student_id, course_id))
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValidationError(f"Student '{student_id}' already enrolled in '{course_id}'.")

    def drop_student_from_course(self, student_id: str, course_id: str) -> None:
        '''    """Unenroll a student from a course.

Parameters:
    student_id: parameter.
    course_id: parameter.
    """'''
        cur = self.conn.execute('DELETE FROM registrations WHERE student_id=? AND course_id=?', (student_id, course_id))
        if cur.rowcount == 0:
            raise ValidationError(f"Student '{student_id}' is not enrolled in '{course_id}'.")
        self.conn.commit()

    def course_students(self, course_id: str) -> List[str]:
        '''    """Return student IDs for a given course.

Parameters:
    course_id: parameter.
    """'''
        cur = self.conn.execute('SELECT r.student_id FROM registrations r WHERE r.course_id=? ORDER BY r.student_id', (course_id,))
        return [row[0] for row in cur.fetchall()]

    def student_courses(self, student_id: str) -> List[str]:
        '''    """Return course IDs for a given student.

Parameters:
    student_id: parameter.
    """'''
        cur = self.conn.execute('SELECT r.course_id FROM registrations r WHERE r.student_id=? ORDER BY r.course_id', (student_id,))
        return [row[0] for row in cur.fetchall()]

    def _exists(self, table: str, col: str, value: str) -> bool:
        '''    """ exists.

Parameters:
    table: parameter.
    col: parameter.
    value: parameter.
    """'''
        cur = self.conn.execute(f'SELECT 1 FROM {table} WHERE {col}=? LIMIT 1', (value,))
        return cur.fetchone() is not None

    def to_dict(self):
        '''"""To dict.

"""'''
        return {'students': [{'student_id': s.student_id, 'name': s.name, 'age': s.age, 'email': s.email, 'courses': self.student_courses(s.student_id)} for s in self.list_students()], 'instructors': [{'instructor_id': i.instructor_id, 'name': i.name, 'age': i.age, 'email': i.email, 'courses': [c.course_id for c in self.list_courses() if c.instructor_id == i.instructor_id]} for i in self.list_instructors()], 'courses': [{'course_id': c.course_id, 'course_name': c.course_name, 'instructor_id': c.instructor_id, 'students': self.course_students(c.course_id)} for c in self.list_courses()]}

    def dump_json(self, path: str) -> None:
        '''    """Dump json.

Parameters:
    path: parameter.
    """'''
        data = self.to_dict()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def backup_db(self, dest_path: str) -> None:
        '''    """Create a file copy of the SQLite database.

Parameters:
    dest_path: parameter.
    """'''
        self.conn.commit()
        shutil.copyfile(self.db_path, dest_path)

    def close(self):
        '''"""Close.

"""'''
        try:
            self.conn.close()
        except:
            pass