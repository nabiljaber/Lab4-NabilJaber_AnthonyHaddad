'''"""
Core Domain Model — Student Subclass

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
from typing import List
from person import Person, ValidationError
from course import Course

class Student(Person):
    """Represents a student entity with a unique student_id and course registrations."""

    def __init__(self, name: str, age: int, email: str, student_id: str):
        '''    """  init  .

Parameters:
    name: parameter.
    age: parameter.
    email: parameter.
    student_id: parameter.
    """'''
        super().__init__(name, age, email)
        if not isinstance(student_id, str) or not student_id.strip():
            raise ValidationError('Student ID cannot be empty.')
        self.student_id = student_id.strip()
        self.registered_courses: List[Course] = []

    def register_course(self, course: Course) -> None:
        '''    """Register course.

Parameters:
    course: parameter.
    """'''
        if not isinstance(course, Course):
            raise ValidationError('register_course expects a Course object.')
        if course in self.registered_courses:
            raise ValidationError(f"Already registered in '{course.course_name}'.")
        self.registered_courses.append(course)

    def drop_course(self, course: Course) -> None:
        '''    """Drop course.

Parameters:
    course: parameter.
    """'''
        if course not in self.registered_courses:
            raise ValidationError(f"Not registered in '{course.course_name}'.")
        self.registered_courses.remove(course)

    def list_courses(self) -> str:
        '''"""List all courses.

"""'''
        return ', '.join((c.course_name for c in self.registered_courses)) or 'No courses'

    def introduce(self) -> str:
        '''"""Return a concise descriptive string for the entity.

"""'''
        return f'Hi, I’m {self.name} (ID: {self.student_id}), {self.age} years old.'

    def __repr__(self) -> str:
        '''"""  repr  .

"""'''
        return f'Student(name={self.name!r}, age={self.age!r}, email={self.email!r}, student_id={self.student_id!r}, registered_courses={[c.course_id for c in self.registered_courses]!r})'