'''"""
Core Domain Model — Instructor Subclass

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

class Instructor(Person):
    """Represents an instructor with a unique instructor_id and course assignments."""

    def __init__(self, name: str, age: int, email: str, instructor_id: str):
        '''    """  init  .

Parameters:
    name: parameter.
    age: parameter.
    email: parameter.
    instructor_id: parameter.
    """'''
        super().__init__(name, age, email)
        if not isinstance(instructor_id, str) or not instructor_id.strip():
            raise ValidationError("Instructor ID can't be empty.")
        self.instructor_id = instructor_id.strip()
        self.assigned_courses: List[Course] = []

    def assign_course(self, course: Course):
        '''    """Assign course.

Parameters:
    course: parameter.
    """'''
        if not isinstance(course, Course):
            raise ValidationError('assign_course expects a Course object.')
        if course in self.assigned_courses:
            raise ValidationError(f"Already assigned to '{course.course_name}'.")
        self.assigned_courses.append(course)

    def unassign_course(self, course: Course):
        '''    """Unassign course.

Parameters:
    course: parameter.
    """'''
        if course not in self.assigned_courses:
            raise ValidationError(f"Not assigned to '{course.course_name}'.")
        self.assigned_courses.remove(course)

    def list_courses(self):
        '''"""List all courses.

"""'''
        return ', '.join((c.course_name for c in self.assigned_courses)) or 'No assigned courses'

    def introduce(self):
        '''"""Return a concise descriptive string for the entity.

"""'''
        return f'Hello, I’m Professor {self.name} (ID: {self.instructor_id}), age {self.age}.'

    def __repr__(self):
        '''"""  repr  .

"""'''
        return f'Instructor(name={self.name!r}, age={self.age!r}, email={self.email!r}, instructor_id={self.instructor_id!r}, assigned_courses={[c.course_id for c in self.assigned_courses]!r})'