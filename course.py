'''"""
Core Domain Model — Course Entity

This module is part of a course project that demonstrates a simple School Management System.
It follows the same documentation style across modules: a clear overview, responsibilities,
and how this component interacts with others in the project.

Date: 2025-09-22
Anthony Haddad

Contents:
- High-level responsibilities of this module
- Key classes and functions defined here
- Notes on usage and important behaviors
"""'''
from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from person import ValidationError
if TYPE_CHECKING:
    from instructor import Instructor
    from Student import Student

class Course:
    """Domain entity for a course, including instructor assignment and enrolled students."""

    def __init__(self, course_id: str, course_name: str):
        '''    """  init  .

Parameters:
    course_id: parameter.
    course_name: parameter.
    """'''
        if not isinstance(course_id, str) or not course_id.strip():
            raise ValidationError('Course ID is empty]')
        if not isinstance(course_name, str) or not course_name.strip():
            raise ValidationError("Course doesn't have a name.")
        self.course_id: str = course_id.strip()
        self.course_name: str = course_name.strip()
        self.enrolled_students: List['Student'] = []

    def setinstructor(self, instructor: 'Instructor'):
        '''    """Setinstructor.

Parameters:
    instructor: parameter.
    """'''
        from instructor import Instructor
        if not isinstance(instructor, Instructor):
            raise ValidationError('It has to be an instructor Object.')
        self.instructor = instructor

    def clearinstructor(self):
        '''"""Clearinstructor.

"""'''
        self.instructor = None

    def addstudent(self, student: 'Student'):
        '''    """Addstudent.

Parameters:
    student: parameter.
    """'''
        from Student import Student
        if not isinstance(student, Student):
            raise ValidationError('expects a Student object.')
        if student in self.enrolled_students:
            raise ValidationError(f"Student '{student.student_id}' already enrolled.")
        self.enrolled_students.append(student)

    def dropstudent(self, student: 'Student') -> None:
        '''    """Dropstudent.

Parameters:
    student: parameter.
    """'''
        if student not in self.enrolled_students:
            sid = getattr(student, 'student_id')
            raise ValidationError(f"Student '{sid}' is not enrolled.")
        self.enrolled_students.remove(student)

    def liststudents(self):
        '''"""Liststudents.

"""'''
        if self.enrolled_students:
            return ', '.join((s.student_id for s in self.enrolled_students))
        else:
            return 'No students'

    def print_course(self):
        '''"""Print course.

"""'''
        if self.instructor:
            iid = self.instructor.instructor_id
        else:
            None
        sids = [s.student_id for s in self.enrolled_students]
        return f'Course(course_id={self.course_id!r}, course_name={self.course_name!r}, instructor_id={iid!r}, enrolled_student_ids={sids!r})'