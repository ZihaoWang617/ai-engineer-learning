from dataclasses import dataclass
from typing import Optional

@dataclass
class Student:
    name: str
    age: int
    gpa: float
    courses: list[str]
@dataclass
class Course:
    code: str
    title: str
    credits: int
    professor: Optional[str] = None