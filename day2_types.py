def add(a: int, b: int) -> int:
    return a + b
def is_adult(age:int)-> bool:
    return age >= 18
def format_name(names:list[str]) -> str:
    return ",".join(names)
print(add(3,5))
print(is_adult(20))
print(format_name(["Alice", "Bob", "Charlie"]))

from typing import Optional
def find_student(name:str, students:list[str]) ->Optional[str]:
    for s in students:
        if s == name:
            return s
        return None
class_list= ["zihao", "xiao", "zhang"]
print(find_student("zihao", class_list))

def calculate_gpa(grades: list[float]) -> float:
    return sum(grades) / len(grades)

def student_info(name:str, age:int, courses:list[str])->dict[str,any]:
    return {
        "name": name,
        "age": age,
        "courses": courses,
        "num_courses": len(courses)
    }

def pass_or_fail(score:float, threshold:float=60.0) -> str:
    if score >=threshold:
        return "Pass"
    return "Fail"

print(calculate_gpa([3.5, 4.0, 3.8]))
print(student_info("Zihao", 24, ["CS5010", "CS5200", "CS6620"]))
print(pass_or_fail(85.5))
print(pass_or_fail(50.0))