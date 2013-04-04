from esky.bdist_esky import Executable
from distutils.core import setup

exe = Executable("thinX.py",
            icon = "logo.ico",
            gui_only = True,
          )

project_files = ["AUTHORS.md", "LICENSE.md", "README.md", "TODO.md",
                 "units.ini"]

setup(
  name = "thinX",
  version = "0.2.1",
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
        "Programming Language :: Python :: 3.2",
        ],
  license="WTFPL",
  keywords="XBRL",
  scripts = [exe],
  data_files = project_files,
  options = {"bdist_esky":{
               "includes": [],
               "excludes": [],
               "freezer_module": "cxfreeze",}
            },
)