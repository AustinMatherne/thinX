thinX
=====

thinX is a GUI that implements various utilities for manipulating XBRL files.


### Dependencies

thinX is developed with Python 3 and PyQt 5.


### Versioning

* Major version bumps accompany the passing of milestones.
* Minor version bumps accompany new features.
* Patch version bumps accompany bug fixes.


Utilities
---------

### Remove Unused Extension Concepts

The Unused Extension Concepts utility searches the extension schema of the selected instance document for declared concepts that are not in use by any of the related linkbases. All unused concepts are logged and removed from the file.


### Remove Unused Labels

The Unused Labels utility searches the corresponding label linkbase of the selected instance document for labels which are not used in the corresponding presentation linkbase. All unused labels are removed and logged.


### Consolidate Labels

The Consolidate Labels utility searches the corresponding label linkbase of the selected instance document for concepts with labels which both have the same textual content and are semantically the same in usage. Any labels which are found to be redundant are removed and references to it in the related presentation linkbase are updated. An example of this would be a concept with a terse and verbose label which are identical, in this case the verbose label would be removed and any references to the verbose label in the presentation linkbase would be changed to refer to the terse label.


### Duplicate Calculations

The Duplicate Calculations utility searches the corresponding calculation linkbase of the selected instance document for duplicate calculation relationships. All duplicate calculations, including subsets, are logged.


### Remove Unused Contexts

The Unused Contexts utility searches the selected instance document for declared contexts that are not in use. All unused contexts are logged and removed from the file.


### Comply with UTR

The UTR utility adds each namespace supplied in the units.ini configuration file and searches the selected instance document for measures which match those defined in units.ini. If a match is found under a different namespace, the prefix for the proper namespace is used, and the capitalization of the measure is corrected if necessary. thinX is compliant as of 2012-11-30, which is the version of the UTR accepted by the SEC as of this writing.
