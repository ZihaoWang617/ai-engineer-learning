from dataclasses import dataclass
from typing import Union, Optional

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

def find_best_student(students: list[Student]) -> Student:
    best = students[0]
    for s in students:
        if s.gpa > best.gpa:
            best = s
    return best

def sort_by_gpa(students:list[Student]) -> list[Student]:
    return sorted(students, key=lambda s: s.gpa, reverse=True)

#test
s1 = Student("Alice", 20, 3.8, ["CS101", "MATH201"])
s2 = Student("Bob", 22, 3.5, ["CS101", "HIST101"])
s3 = Student("Charlie", 21, 3.9, ["CS101", "PHYS101"])

print("all students:")
for s in [s1, s2, s3]:
    print(f"{s.name}, AGE: {s.age}, GPA: {s.gpa}, Courses: {s.courses}")
print("\nBest student:")
print(f"{find_best_student([s1, s2, s3]).name}, GPA: {find_best_student([s1, s2, s3]).gpa}, Courses: {find_best_student([s1, s2, s3]).courses}")

print("\nStudents sorted by GPA:")
for s in sort_by_gpa([s1, s2, s3]):
    print(f"{s.name}: {s.gpa}")

c1 = Course("CS101", "Intro to Computer Science", 4, "Dr. Smith")
c2 = Course("MATH201", "Calculus II", 3)
print("\nCourses:")
print(c1)  
print(c2)
