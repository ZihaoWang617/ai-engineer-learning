from practice.day4_project.src.models import Student, Course
from practice.day4_project.src.utils import find_best_student, sort_by_gpa

def main():
    s1 = Student("Zihao", 24, 3.5, ["CS5010", "CS5200"])
    s2 = Student("Alice", 22, 3.9, ["CS5010", "CS6620"])
    s3 = Student("Bob", 23, 3.2, ["CS5200", "CS5600"])
    students = [s1, s2, s3]

    print("All students:")
    for s in students:
        print(f"{s.name}, Age: {s.age}, GPA: {s.gpa}, Courses: {s.courses}")
    print(f"\nBest Student: {find_best_student(students).name}")
    print(f"\nRanked by GPA:")
    for s in sort_by_gpa(students):
        print(f"{s.name}: {s.gpa}")
    c1 = Course("CS5010", "Programming Design Paradigms", 4, "Professor Smith")
    c2 = Course("CS6620", "Cloud Computing", 4)
    print(f"\nCourses: {c1.code} - {c1.title}, {c2.code} - {c2.title}")

if __name__ == "__main__":
    main()  