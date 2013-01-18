from cx_Freeze import setup, Executable


project_files = ["AUTHORS.md", "LICENSE.md", "README.md", "TODO.md",
                 "units.ini"]

exe = Executable(
    script="thinX.py",
    base="Win32GUI")

setup(
    name="thinX",
    version="0.1",
    description="GUI with various utilities for manipulating XBRL files.",
    author="Austin M. Matherne",
    author_email="AustinMatherne@Gmail.com",
    options={"build_exe": {"include_files": project_files}},
    executables=[exe])
