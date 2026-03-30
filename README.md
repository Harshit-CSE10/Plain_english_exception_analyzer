# Plain English Python Exception Analyzer

**Course:** CSA2001 — Fundamentals in AI and ML  

This is a Python debugging tool I built to help beginners understand runtime errors. Instead of just printing a standard Python traceback, this script reads the error and tries to explain what went wrong in plain English.

## The Problem
When I started learning Python, getting an error like `IndexError: list index out of range` was super confusing. It tells you the script crashed, but it doesn't really explain *why* or how to fix it. I built this tool to bridge that gap using basic string matching and NLP concepts.

## Features
* **Custom Error Explanations:** Explains 11 common Python exceptions (IndexError, KeyError, TypeError, etc.) in simple terms.
* **Source Context:** Actually opens the file that crashed and prints the lines of code around the error.
* **Fix Suggestions:** Gives a quick hint on what to check to fix the bug.
* **Interactive Menu:** Includes a CLI menu to either run a buggy file, paste a traceback, or test built-in examples.

## How to Run It

You just need standard Python installed (3.10+ recommended). No external libraries are required.

1. Clone or download this repository.
2. Open your terminal in the project folder.
3. Run the interactive menu:
   ```bash
   python app.py
