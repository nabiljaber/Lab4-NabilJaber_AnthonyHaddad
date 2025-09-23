'''"""
Core Domain Model — Person Base Class

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
import re

class ValidationError(Exception):
    """ValidationError class used within the School Management System."""
    pass

class Person:
    """Base class for people in the system with validated name, age, and email fields."""
    EMAIL_RE = re.compile('^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')

    def __init__(self, name: str, age: int, email: str):
        '''    """  init  .

Parameters:
    name: parameter.
    age: parameter.
    email: parameter.
    """'''
        self.name = name
        self.age = age
        self.email = email

    @property
    def name(self) -> str:
        '''"""Name.

"""'''
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        '''    """Name.

Parameters:
    value: parameter.
    """'''
        if not isinstance(value, str) or not value.strip():
            raise ValidationError('Name cannot be empty.')
        self._name = value.strip()

    @property
    def age(self) -> int:
        '''"""Age.

"""'''
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        '''    """Age.

Parameters:
    value: parameter.
    """'''
        if not isinstance(value, int) or value < 0:
            raise ValidationError('Age must be a non-negative integer.')
        self._age = value

    @property
    def email(self) -> str:
        '''"""Email.

"""'''
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        '''    """Email.

Parameters:
    value: parameter.
    """'''
        if not isinstance(value, str) or not self.EMAIL_RE.match(value):
            raise ValidationError(f'Invalid email format: {value}')
        self._email = value

    def introduce(self) -> str:
        '''"""Return a concise descriptive string for the entity.

"""'''
        return f'Hi, I’m {self.name}, {self.age} years old.'

    def __repr__(self) -> str:
        '''"""  repr  .

"""'''
        return f'Person(name={self.name!r}, age={self.age!r}, email={self.email!r})'