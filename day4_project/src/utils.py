from src.models import Student

def find_best_student(students: list[Student]) -> Student:
    best = students[0]
    for s in students:
        if best.gpa < s.gpa:
            best = s
    return best 

def sort_by_gpa(students:list[Student]) -> list[Student]:
    return sorted(students, key = lambda s: s.gpa, reverse=True)
