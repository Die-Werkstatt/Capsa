# Glossary

Every technical term used in Capsa, in plain language. Alphabetical.

**Dependency:** code somebody else wrote that Capsa uses, such as pytest. Like a plugin: Capsa does not work without it, and it has its own version.

**Lockfile (`uv.lock`):** the exact version of every dependency, written by uv. Like caching a simulation to disk: everybody who opens the project gets the same result, not whatever is newest that day.

**Package:** a folder of Python code that can be imported by name. `src/capsa/` is the `capsa` package.

**pytest:** the program that runs the tests. A test is a small script that checks one behaviour and fails loudly when the behaviour changes.

**ruff:** the program that checks Python code for mistakes and formats it the same way everywhere.

**uv:** the tool that installs Python, creates the project's private environment (`.venv`) and runs commands inside it. `uv run pytest` means "run pytest with exactly this project's dependencies".

**Virtual environment (`.venv`):** a private copy of Python's installed packages for one project, so two projects cannot break each other. It is rebuilt from the lockfile and never committed.
