thinX
=====

thinX is a GUI that implements various utilities for manipulating XBRL files.


### Version

0.1.0


### Dependencies

thinX is developed with Python 3.3 and PyQt4. It should work with other versions of Python, as well; however, no guarantees are made. It will also likely work with PySide by simply swapping out the import.


### cx_Freeze Support

setup.py is provided for creating executables using cx_Freeze.


### Versioning

* Major version bumps accompany the passing of milestones.
* Minor version bumps accompany new features.
* Patch version bumps accompany bug fixes.


Utilities
---------

### Comply with UTR

The UTR utility adds each namespace supplied in the units.ini configuration file and searches the selected instance document for measures which match those defined in units.ini. If a match is found under a different namespace, the prefix for the proper namespace is used, and the capitalization of the measure is corrected if necessary.


### Remove Unused Contexts

The Unused Contexts utility searches the selected instance document for declared contexts that are not in use. All unused contexts are logged and removed from the file.
