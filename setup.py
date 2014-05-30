import re
import sys
from cx_Freeze import setup, Executable


def get_version(filename):
    try:
        f = open(filename)
    except EnvironmentError:
        return None
    for line in f.readlines():
        mo = re.match("__version__ = \"([^']+)\"", line)
        if mo:
            ver = mo.group(1)
            return ver
    return None

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

project_files = [
    "_version.py",
    "AUTHORS.md",
    "LICENSE.md",
    "README.md",
    "units.ini"
]

options = {
    "build_exe": {
        "include_files":    project_files,
        "includes":         ["sip", "lxml._elementpath"],
        "icon":             "logo.ico",
        "optimize":         2,
        "base":             base
    }
}

exe = Executable(
    "thinX.pyw"
)

setup(
    name="thinX",
    version=get_version("_version.py"),
    description="GUI with various utilities for manipulating XBRL files.",
    author="Austin M. Matherne",
    author_email="AustinMatherne@Gmail.com",
    url="https://github.com/AustinMatherne/thinX",
    download_url="https://github.com/AustinMatherne/thinX/archive/master.zip",
    classifiers=[
        "Topic :: Desktop Environment",
        "Topic :: Office/Business",
        "Topic :: Text Processing",
        "Topic :: Utilities",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.3",
        ],
    license="WTFPL",
    keywords="XBRL",
    options=options,
    executables=[exe]
)
