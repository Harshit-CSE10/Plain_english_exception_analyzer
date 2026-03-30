import os
import sys
import subprocess
import tempfile
import re

from analyzer import parse_traceback, match_rule, build_explanation, DIVIDER, analyze


def run_file(path):
    result = subprocess.run(
        [sys.executable, path],
        capture_output=True,
        text=True
    )
    stderr = result.stderr.strip()

    if result.returncode == 0:
        print("\n  Your code ran with no errors!")
        if result.stdout.strip():
            print("\n  Output:")
            for line in result.stdout.strip().splitlines():
                print("    " + line)
        return

    if "SyntaxError" in stderr or "IndentationError" in stderr:
        print("\n" + DIVIDER)
        print("  SYNTAX ERROR DETECTED")
        print(DIVIDER)
        line_match   = re.search(r"line (\d+)", stderr)
        detail_match = re.search(r"(SyntaxError|IndentationError): (.+)", stderr)
        detail = detail_match.group(2) if detail_match else stderr.split("\n")[-1]
        line   = line_match.group(1) if line_match else "unknown"
        print(f"\n  Python could not even start running your code.")
        print(f"  There is a syntax error on or near line {line}.")
        print(f"  Detail: {detail}")
        print("\n" + "-" * 65)
        print("  Things to check:")
        print("  - Did you close all your quotes?")
        print("  - Missing colon after if, for, or def?")
        print("  - Any unmatched brackets ( [ { ?")
        print("  - Semicolons at end of lines are not needed in Python")
        print(DIVIDER)
        return

    if "Traceback" in stderr:
        analyze(stderr)
    else:
        print("\n  Script exited with an error but no traceback was found.")
        print("  " + stderr)


def paste_mode():
    print("\n  Paste your traceback below.")
    print("  When you are done, type END on a new line and press Enter.\n")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    tb_text = "\n".join(lines).strip()
    if tb_text:
        analyze(tb_text)
    else:
        print("\n  Nothing was pasted. Try again.")


def show_examples():
    examples = {
        "1": ("IndexError", 'fruits = ["apple", "banana", "cherry"]\nprint(fruits[10])'),
        "2": ("KeyError",   'student = {"name": "Ravi", "grade": "A"}\nprint(student["age"])'),
        "3": ("ZeroDivisionError", 'total = 100\ncount = 0\nprint(total / count)'),
        "4": ("NameError",  'print(scroe)'),
        "5": ("TypeError",  'result = "Score: " + 95'),
        "6": ("RecursionError", 'def countdown(n):\n    return countdown(n - 1)\ncountdown(5)'),
    }

    print("\n" + "-" * 65)
    print("  Pick an example to run:")
    print("-" * 65)
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. Go back")
    print()

    choice = input("  Enter number: ").strip()
    if choice == "0" or choice not in examples:
        return

    name, code = examples[choice]
    print(f"\n  Running example: {name}")
    print("  Code:")
    for line in code.splitlines():
        print("    " + line)
    print()

    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
        f.write(code)
        tmp_path = f.name

    try:
        run_file(tmp_path)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def main():
    print("\n" + DIVIDER)
    print("  Plain English Python Exception Analyzer")
    print("  CSA2001 - Fundamentals in AI and ML | VIT Bhopal")
    print(DIVIDER)

    while True:
        print("\n  What would you like to do?")
        print("  1. Run a Python file and analyze any error")
        print("  2. Paste a traceback and get an explanation")
        print("  3. Try a built-in example")
        print("  4. Exit")
        print()

        choice = input("  Enter your choice (1/2/3/4): ").strip()

        if choice == "1":
            path = input("\n  Enter the path to your Python file: ").strip()
            if os.path.isfile(path):
                run_file(path)
            else:
                print(f"\n  Could not find the file: '{path}'")
                print("  Make sure the file exists and the path is correct.")

        elif choice == "2":
            paste_mode()

        elif choice == "3":
            show_examples()

        elif choice in ("4", "q", "quit", "exit"):
            print("\n  Goodbye! Happy debugging.\n")
            break

        else:
            print("\n  Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
