'''"""
JSON Data Store — School Management System

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
from typing import Dict
from pathlib import Path
import json
from person import ValidationError
from Student import Student
from instructor import Instructor
from course import Course
STUDENTS_JSON = Path('students.json')
INSTRUCTORS_JSON = Path('instructors.json')
COURSES_JSON = Path('courses.json')

class DataStore:
    """In-memory JSON-backed repository providing CRUD utilities for students, instructors, and courses."""

    def __init__(self):
        '''"""  init  .

"""'''
        self.students: Dict[str, Student] = {}
        self.instructors: Dict[str, Instructor] = {}
        self.courses: Dict[str, Course] = {}

    def add_student(self, name: str, age: int, email: str, student_id: str) -> Student:
        '''    """Add a new student to the store or current view.

Parameters:
    name: parameter.
    age: parameter.
    email: parameter.
    student_id: parameter.
    """'''
        if student_id in self.students:
            raise ValidationError(f"Student ID '{student_id}' exists.")
        s = Student(name, age, email, student_id)
        self.students[student_id] = s
        return s

    def add_instructor(self, name: str, age: int, email: str, instructor_id: str) -> Instructor:
        '''    """Add a new instructor to the store or current view.

Parameters:
    name: parameter.
    age: parameter.
    email: parameter.
    instructor_id: parameter.
    """'''
        if instructor_id in self.instructors:
            raise ValidationError(f"Instructor ID '{instructor_id}' exists.")
        i = Instructor(name, age, email, instructor_id)
        self.instructors[instructor_id] = i
        return i

    def add_course(self, course_id: str, course_name: str) -> Course:
        '''    """Create a course record.

Parameters:
    course_id: parameter.
    course_name: parameter.
    """'''
        if course_id in self.courses:
            raise ValidationError(f"Course ID '{course_id}' exists.")
        c = Course(course_id, course_name)
        self.courses[course_id] = c
        return c
    adstudent = add_student
    adinstructor = add_instructor
    adcourse = add_course

    def enroll_student_in_course(self, student_id: str, course_id: str) -> None:
        '''    """Register a student into a course.

Parameters:
    student_id: parameter.
    course_id: parameter.
    """'''
        s = self._get_student(student_id)
        c = self._get_course(course_id)
        c.add_student(s)
        if c not in s.registered_courses:
            s.registered_courses.append(c)

    def drop_student_from_course(self, student_id: str, course_id: str) -> None:
        '''    """Unenroll a student from a course.

Parameters:
    student_id: parameter.
    course_id: parameter.
    """'''
        s = self._get_student(student_id)
        c = self._get_course(course_id)
        c.drop_student(s)
        if c in s.registered_courses:
            s.registered_courses.remove(c)

    def assign_instructor_to_course(self, instructor_id: str, course_id: str) -> None:
        '''    """Assign an instructor to a course.

Parameters:
    instructor_id: parameter.
    course_id: parameter.
    """'''
        i = self._get_instructor(instructor_id)
        c = self._get_course(course_id)
        c.set_instructor(i)
        if c not in i.assigned_courses:
            i.assigned_courses.append(c)

    def unassign_instructor_from_course(self, course_id: str) -> None:
        '''    """Unassign the instructor from a course.

Parameters:
    course_id: parameter.
    """'''
        c = self._get_course(course_id)
        old = c.instructor
        if old and c in old.assigned_courses:
            old.assigned_courses.remove(c)
        c.clear_instructor()

    def _get_student(self, student_id: str) -> Student:
        '''    """ get student.

Parameters:
    student_id: parameter.
    """'''
        if student_id not in self.students:
            raise ValidationError(f"Unknown student_id '{student_id}'.")
        return self.students[student_id]

    def _get_instructor(self, instructor_id: str) -> Instructor:
        '''    """ get instructor.

Parameters:
    instructor_id: parameter.
    """'''
        if instructor_id not in self.instructors:
            raise ValidationError(f"Unknown instructor_id '{instructor_id}'.")
        return self.instructors[instructor_id]

    def _get_course(self, course_id: str) -> Course:
        '''    """ get course.

Parameters:
    course_id: parameter.
    """'''
        if course_id not in self.courses:
            raise ValidationError(f"Unknown course_id '{course_id}'.")
        return self.courses[course_id]

    def save_all(self) -> None:
        '''"""Persist in-memory data into JSON files.

"""'''
        STUDENTS_JSON.write_text(json.dumps([{'student_id': s.student_id, 'name': s.name, 'age': s.age, 'email': s.email, 'registered_course_ids': [c.course_id for c in s.registered_courses]} for s in self.students.values()], indent=2), encoding='utf-8')
        INSTRUCTORS_JSON.write_text(json.dumps([{'instructor_id': i.instructor_id, 'name': i.name, 'age': i.age, 'email': i.email, 'assigned_course_ids': [c.course_id for c in i.assigned_courses]} for i in self.instructors.values()], indent=2), encoding='utf-8')
        COURSES_JSON.write_text(json.dumps([{'course_id': c.course_id, 'course_name': c.course_name, 'instructor_id': c.instructor.instructor_id if c.instructor else None, 'enrolled_student_ids': [s.student_id for s in c.enrolled_students]} for c in self.courses.values()], indent=2), encoding='utf-8')

    @classmethod
    def load_all(cls) -> 'DataStore':
        '''"""Load data into memory from JSON files.

"""'''
        ds = cls()
        if STUDENTS_JSON.exists():
            for s in json.loads(STUDENTS_JSON.read_text(encoding='utf-8')):
                ds.students[s['student_id']] = Student(s['name'], int(s['age']), s['email'], s['student_id'])
        if INSTRUCTORS_JSON.exists():
            for rec in json.loads(INSTRUCTORS_JSON.read_text(encoding='utf-8')):
                ds.instructors[rec['instructor_id']] = Instructor(rec['name'], int(rec['age']), rec['email'], rec['instructor_id'])
        if COURSES_JSON.exists():
            for c in json.loads(COURSES_JSON.read_text(encoding='utf-8')):
                ds.courses[c['course_id']] = Course(c['course_id'], c['course_name'])
        if STUDENTS_JSON.exists():
            for s in json.loads(STUDENTS_JSON.read_text(encoding='utf-8')):
                st = ds.students[s['student_id']]
                for cid in s.get('registered_course_ids', []):
                    st.register_course(ds._get_course(cid))
        if INSTRUCTORS_JSON.exists():
            for rec in json.loads(INSTRUCTORS_JSON.read_text(encoding='utf-8')):
                ins = ds.instructors[rec['instructor_id']]
                for cid in rec.get('assigned_course_ids', []):
                    ins.assign_course(ds._get_course(cid))
        if COURSES_JSON.exists():
            for c in json.loads(COURSES_JSON.read_text(encoding='utf-8')):
                crs = ds.courses[c['course_id']]
                ins_id = c.get('instructor_id')
                if ins_id:
                    crs.set_instructor(ds._get_instructor(ins_id))
                for sid in c.get('enrolled_student_ids', []):
                    crs.add_student(ds._get_student(sid))
        return ds