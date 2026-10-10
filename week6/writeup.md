# Week 6 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: Fibbin\
SUNet ID: Null \
Citations: Gemini Pro supported

This assignment took me about 4 hours to do. 


## Brief findings overview 
> TODO
# Week 6 Security Assignment Writeup

## Fix #1: SQL Injection
* **a. File and line(s):** `week6/backend/app/routers/notes.py`, line 72 (`/unsafe-search` endpoint).
* **b. Rule/category Semgrep flagged:** SQL Injection with SQLAlchemy (Critical)
* **c. Brief risk description:** Untrusted user input was directly concatenated into an SQL query string. An attacker could exploit this to execute malicious SQL statements, potentially gaining unauthorized access to sensitive data or modifying the database.
* **d. Your change:** I used Cursor (AI tool) to rewrite the query using SQLAlchemy's parameterized queries (bind parameters). I replaced the f-string with a `:pattern` placeholder and passed the user input as a parameter dictionary `{"pattern": "%" + q + "%"}` to `db.execute()`.
* **e. Why this mitigates the issue:** Parameterized queries treat user input strictly as data rather than executable code. The database driver automatically escapes the input, completely preventing attackers from altering the SQL logic.

## Fix #2: OS Command Injection
* **a. File and line(s):** `week6/backend/app/routers/notes.py`, line 112 (`/debug/run` endpoint).
* **b. Rule/category Semgrep flagged:** OS Command Injection with FastAPI (High)
* **c. Brief risk description:** The application executed user-supplied strings directly as system commands. An attacker could append malicious commands (e.g., using `;` or `|`) to gain full control of the host system.
* **d. Your change:** I used Cursor to implement a secure command execution logic. The fix uses `shlex.split()` to safely parse the input string into a list of arguments, implements a strict allowlist (`allowed_commands = {"echo"}`), and explicitly sets `shell=False` in `subprocess.run()`.
* **e. Why this mitigates the issue:** Setting `shell=False` disables the shell interpreter, preventing the execution of shell metacharacters like pipes or semicolons. The allowlist further restricts execution strictly to approved, harmless commands, eliminating the attack vector.

## Fix #3: Path Traversal
* **a. File and line(s):** `week6/backend/app/routers/notes.py`, line 128 (`/debug/read` endpoint).
* **b. Rule/category Semgrep flagged:** Path Traversal with FastAPI (High)
* **c. Brief risk description:** The endpoint built file paths using unvalidated user input. An attacker could use `../` sequences to escape the intended directory and read sensitive files on the server, such as `/etc/passwd`.
* **d. Your change:** I used Cursor to sanitize the file path using Python's `pathlib`. The code now resolves the absolute path of the base directory and the requested file, and uses `requested.relative_to(base_dir)` to ensure the requested file is strictly inside the intended `./data` directory.
* **e. Why this mitigates the issue:** The `resolve()` method normalizes all `../` characters, and `relative_to()` throws a `ValueError` if the requested path is outside the base directory. This acts as a strict sandbox, preventing attackers from accessing anything outside the designated folder.