# Glossary

Every technical term used in Capsa, in plain language. Alphabetical.

**Dataclass:** a small Python class that only holds values, like a row in a spreadsheet. `FileRecord` is one: path, size, date, kind.

**Dependency:** code somebody else wrote that Capsa uses, such as pytest. Like a plugin: Capsa does not work without it, and it has its own version.

**Enum:** a fixed list of allowed values with names. `Kind` is one: USD, texture, HDRI and so on. A typo such as `Kind.TEXTRUE` fails at once, where a misspelt word in quotes would pass unnoticed.

**Library root:** a folder you point Capsa at. Everything inside it belongs to the library.

**Lockfile (`uv.lock`):** the exact version of every dependency, written by uv. Like caching a simulation to disk: everybody who opens the project gets the same result, not whatever is newest that day.

**Package:** a folder of Python code that can be imported by name. `src/capsa/` is the `capsa` package.

**pytest:** the program that runs the tests. A test is a small script that checks one behaviour and fails loudly when the behaviour changes.

**ruff:** the program that checks Python code for mistakes and formats it the same way everywhere.

**Suffix:** the end of a file name that says what the file is, such as `.usd` or `.bgeo.sc`.

**uv:** the tool that installs Python, creates the project's private environment (`.venv`) and runs commands inside it. `uv run pytest` means "run pytest with exactly this project's dependencies".

**Virtual environment (`.venv`):** a private copy of Python's installed packages for one project, so two projects cannot break each other. It is rebuilt from the lockfile and never committed.
