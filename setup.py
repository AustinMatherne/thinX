from distutils.core import setup
import re

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

setup(
    name = "thinX",
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
)
