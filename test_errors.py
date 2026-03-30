
def index_error_demo():
    fruits = ["apple", "banana", "cherry"]
    print(fruits[10])  # Only 3 items — index 10 doesn't exist!

def key_error_demo():
    student = {"name": "Ravi", "grade": "A"}
    print(student["age"])  # "age" key doesn't exist

def type_error_demo():
    message = "Your score is: " + 95  # Can't add string + int

def zero_division_demo():
    total = 100
    count = 0
    average = total / count  # Division by zero!

def name_error_demo():
    print(scroe)  # Typo: should be 'score'

def recursion_error_demo():
    def countdown(n):
        return countdown(n - 1)  # No base case!
    countdown(5)

index_error_demo()
