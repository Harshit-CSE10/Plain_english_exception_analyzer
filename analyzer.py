import sys
import re
import os
import subprocess


stop_words = {"the", "a", "an", "is", "in", "at", "of", "to", "for", "and", "or", "not"}

def extract_keywords(text):
    tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text.lower())
    return [t for t in tokens if t not in stop_words]


EXCEPTION_RULES = {
    "IndexError": {
        "pattern": re.compile(r"list index out of range|string index out of range|tuple index out of range", re.I),
        "plain": (
            "You tried to access an item at a position that doesn't exist.\n"
            "  • Think of a list like a row of lockers numbered 0, 1, 2 ...\n"
            "  • If the list has {length} items, valid positions are 0 to {max_idx}.\n"
            "  • You tried to open locker number {index}.\n"
            "  Fix: Check your loop boundaries or use 'len()' before accessing."
        ),
        "hint": "Check loop range — use `for i in range(len(your_list))` or just `for item in your_list`.",
    },
    "KeyError": {
        "pattern": re.compile(r"KeyError", re.I),
        "plain": (
            "You tried to access a key in a dictionary that doesn't exist.\n"
            "  • The key {key} was not found in your dictionary.\n"
            "  Fix: Use `dict.get(key, default)` or check with `if key in dict:` first."
        ),
        "hint": "Use `.get()` instead of `[]` to avoid KeyErrors safely.",
    },
    "TypeError": {
        "pattern": re.compile(r"unsupported operand|not subscriptable|object is not iterable|'NoneType'", re.I),
        "plain": (
            "You used a value in a way that doesn't make sense for its type.\n"
            "  • Example: adding a number to a string, or calling a method on None.\n"
            "  Fix: Use `type(variable)` to inspect what you're working with before using it."
        ),
        "hint": "Print `type(your_variable)` before the failing line to see what you actually have.",
    },
    "NameError": {
        "pattern": re.compile(r"name '.*' is not defined", re.I),
        "plain": (
            "You used a variable or function name that Python has never heard of.\n"
            "  • Either it was never assigned, or it was spelled differently.\n"
            "  Fix: Check for typos, or make sure you defined the variable before using it."
        ),
        "hint": "Python is case-sensitive — `Score` and `score` are different variables!",
    },
    "AttributeError": {
        "pattern": re.compile(r"has no attribute", re.I),
        "plain": (
            "You called a method or property that doesn't exist on that object.\n"
            "  • Maybe you made a typo, or you're calling a list method on a string (or vice versa).\n"
            "  Fix: Use `dir(your_object)` to list all valid methods."
        ),
        "hint": "Run `print(dir(your_variable))` to see all available methods and attributes.",
    },
    "ZeroDivisionError": {
        "pattern": re.compile(r"division by zero|modulo by zero", re.I),
        "plain": (
            "You divided a number by zero — which is mathematically undefined.\n"
            "  Fix: Add a guard: `if denominator != 0: result = numerator / denominator`"
        ),
        "hint": "Always check that your denominator is not zero before dividing.",
    },
    "FileNotFoundError": {
        "pattern": re.compile(r"No such file or directory", re.I),
        "plain": (
            "Python couldn't find the file you asked it to open.\n"
            "  • Check that the filename is spelled correctly and the path is right.\n"
            "  Fix: Use `os.path.exists(filename)` to check before opening."
        ),
        "hint": "Use `os.getcwd()` to print your current directory and verify the file location.",
    },
    "RecursionError": {
        "pattern": re.compile(r"maximum recursion depth exceeded", re.I),
        "plain": (
            "Your recursive function kept calling itself with no end in sight.\n"
            "  • Every function call uses stack memory — Python stops after around 1000 calls.\n"
            "  Fix: Make sure your recursive function has a base case that returns without calling itself."
        ),
        "hint": "Every recursive function needs a base case — a condition where it stops calling itself.",
    },
    "ValueError": {
        "pattern": re.compile(r"invalid literal|could not convert|not enough values", re.I),
        "plain": (
            "A function received the right type of value, but the value itself was wrong.\n"
            "  • For example, `int('hello')` — Python can't convert letters to a number.\n"
            "  Fix: Validate input before passing it to functions like `int()` or `float()`."
        ),
        "hint": "Wrap conversions in try/except: `try: x = int(input()) except ValueError: print('Not a number!')`",
    },
    "ImportError": {
        "pattern": re.compile(r"No module named|cannot import name", re.I),
        "plain": (
            "Python couldn't find a module or function you tried to import.\n"
            "  Fix: Install it with `pip install <module_name>` or check the spelling."
        ),
        "hint": "Run `pip list` to see all installed packages.",
    },
    "IndentationError": {
        "pattern": re.compile(r"unexpected indent|expected an indented block", re.I),
        "plain": (
            "Your code's indentation (spacing) is wrong.\n"
            "  • Python uses indentation to define code blocks — be consistent with spaces or tabs, not both.\n"
            "  Fix: Use 4 spaces per level consistently."
        ),
        "hint": "Never mix tabs and spaces. Configure your editor to always use spaces.",
    },
}


def parse_traceback(tb_text):
    info = {
        "exception_type": "Unknown",
        "exception_msg": "",
        "file": "",
        "line_no": None,
        "code_line": "",
    }

    exc_match = re.search(r"^(\w+(?:Error|Exception|Warning|Interrupt|Exit)):\s*(.*)", tb_text, re.M)
    if exc_match:
        info["exception_type"] = exc_match.group(1)
        info["exception_msg"] = exc_match.group(2).strip()

    file_matches = re.findall(r'File "([^"]+)", line (\d+)', tb_text)
    if file_matches:
        info["file"], info["line_no"] = file_matches[-1]
        info["line_no"] = int(info["line_no"])

    lines = re.findall(r"^\s{4}(.+)$", tb_text, re.M)
    if lines:
        info["code_line"] = lines[-1].strip()

    return info


def get_source_context(filepath, line_no, context=3):
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
        start = max(0, line_no - context - 1)
        end = min(len(lines), line_no + context)
        result = []
        for i, line in enumerate(lines[start:end], start=start + 1):
            marker = ">>>" if i == line_no else "   "
            result.append(f"{marker} {i:3d} | {line.rstrip()}")
        return result
    except Exception:
        return []


def match_rule(exc_type, exc_msg):
    if exc_type in EXCEPTION_RULES:
        return EXCEPTION_RULES[exc_type]

    msg_keywords = set(extract_keywords(exc_msg))
    best_rule, best_score = None, 0
    for rule_name, rule in EXCEPTION_RULES.items():
        rule_keywords = set(extract_keywords(rule_name + " " + rule["hint"]))
        score = len(msg_keywords & rule_keywords)
        if score > best_score:
            best_score, best_rule = score, rule
    return best_rule if best_score > 0 else None


def build_explanation(parsed, rule):
    msg = parsed["exception_msg"]

    numbers = re.findall(r"\d+", msg)
    index = numbers[0] if numbers else "?"
    length = numbers[1] if len(numbers) > 1 else "?"
    max_idx = str(int(length) - 1) if length != "?" else "?"

    key_match = re.search(r"'([^']+)'", msg)
    key = f"'{key_match.group(1)}'" if key_match else "(unknown key)"

    return rule["plain"].format(index=index, length=length, max_idx=max_idx, key=key)


DIVIDER = "=" * 65

def analyze(tb_text, verbose=True):
    parsed = parse_traceback(tb_text)
    rule = match_rule(parsed["exception_type"], parsed["exception_msg"])

    lines = [
        "",
        DIVIDER,
        "  PLAIN ENGLISH PYTHON EXCEPTION ANALYZER",
        "  CSA2001 - Fundamentals in AI and ML | VIT Bhopal",
        DIVIDER,
        f"  Exception : {parsed['exception_type']}",
        f"  Message   : {parsed['exception_msg']}",
    ]

    if parsed["file"]:
        lines.append(f"  File      : {parsed['file']}, line {parsed['line_no']}")
    if parsed["code_line"]:
        lines.append(f"  Code      : {parsed['code_line']}")

    lines.append("")

    if rule:
        explanation = build_explanation(parsed, rule)
        lines.append("-" * 65)
        lines.append("  WHAT HAPPENED (Plain English)")
        lines.append("-" * 65)
        for ln in explanation.splitlines():
            lines.append("  " + ln)
        lines.append("")
        lines.append("-" * 65)
        lines.append("  QUICK FIX TIP")
        lines.append("-" * 65)
        lines.append("  " + rule["hint"])
    else:
        lines.append("  No specific explanation available for this exception type.")
        lines.append("  Tip: Copy the error message and search it on docs.python.org")

    if parsed["file"] and parsed["line_no"] and os.path.isfile(parsed["file"]):
        context = get_source_context(parsed["file"], parsed["line_no"])
        if context:
            lines.append("")
            lines.append("-" * 65)
            lines.append("  SOURCE CONTEXT")
            lines.append("-" * 65)
            for cl in context:
                lines.append("  " + cl)

    lines.append("")
    lines.append(DIVIDER)

    report = "\n".join(lines)
    if verbose:
        print(report)
    return report


def run_and_analyze(script_path):
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True
    )
    stderr = result.stderr.strip()
    if stderr and "Traceback" in stderr:
        analyze(stderr)
    elif result.returncode == 0:
        print(f"  '{script_path}' ran successfully with no errors!")
    else:
        print(f"  Script exited with code {result.returncode}.")
        if stderr:
            print(stderr)


def main():
    print("\n" + DIVIDER)
    print("  Plain English Python Exception Analyzer")
    print("  CSA2001 - VIT Bhopal  |  Type 'quit' to exit")
    print(DIVIDER)
    print("\nUsage options:")
    print("  1. Run a Python file  -> Enter its path (e.g. my_script.py)")
    print("  2. Paste a traceback  -> Type 'paste', then paste the error, then type 'END'")
    print()

    while True:
        choice = input("Enter file path or 'paste': ").strip()
        if choice.lower() in ("quit", "exit", "q"):
            print("\nGoodbye! Happy debugging.")
            break
        elif choice.lower() == "paste":
            print("Paste your traceback below. Type 'END' on a new line when done:")
            tb_lines = []
            while True:
                ln = input()
                if ln.strip() == "END":
                    break
                tb_lines.append(ln)
            analyze("\n".join(tb_lines))
        elif os.path.isfile(choice):
            run_and_analyze(choice)
        else:
            print(f"  File not found: '{choice}'. Try again or type 'paste'.\n")


if __name__ == "__main__":
    main()

