thinX
=====

thinX is a set of utilities for manipulating XBRL files.


### Dependencies

thinX is developed with Python 3 and PyQt 5.


### Versioning

* Major version bumps accompany the passing of milestones.
* Minor version bumps accompany new features.
* Patch version bumps accompany bug fixes.


Schema Utilities
----------------

### Remove Unused Link Roles

The Remove Unused Link Roles utility searches the extension schema of the selected instance document for extension link roles that are not in use by any of the related linkbases. All unused link roles are logged and removed from the file.


### Remove Unused Labels

The Unused Labels utility searches the corresponding label linkbase of the selected instance document for labels which are not used in the corresponding presentation linkbase. All unused labels are removed and logged.


### Consolidate Labels

The Consolidate Labels utility searches the corresponding label linkbase of the selected instance document for concepts with labels which both have the same textual content and are semantically the same in usage. Any labels which are found to be redundant are removed and references to them in the related presentation linkbase are updated. An example of this would be a concept with a terse and verbose label which are identical, in this case the verbose label would be removed and any references to the verbose label in the presentation linkbase would be changed to refer to the terse label.


### Remove Unused Extension Concepts

The Unused Extension Concepts utility searches the extension schema of the selected instance document for declared concepts that are not in use by any of the related linkbases. All unused concepts are logged and removed from the file.


### Report Duplicate Calculations

The Duplicate Calculations utility searches the corresponding calculation linkbase of the selected instance document for duplicate calculation relationships. All duplicate calculations, including subsets, are logged.


Instance Utilities
----------------

### Remove Unused Contexts

The Unused Contexts utility searches the selected instance document for declared contexts that are not in use. All unused contexts are logged and removed from the file.


### Report Two Day Contexts

The Report Two Day Contexts utility searches and logs durational contexts with an end date precisely one day after the start date in the selected instance document. This is useful for finding contexts that should start and end on the same day, but were setup prior to the EFM allowing one day contexts.


### Comply with UTR

The UTR utility adds each namespace supplied in the units.ini configuration file and searches the selected instance document for measures which match those defined in units.ini. If a match is found under a different namespace, the prefix for the proper namespace is used, and the capitalization of the measure is corrected if necessary. thinX is compliant as of 2012-11-30, which is the version of the UTR accepted by the SEC as of this writing.


Bridge Utilities
----------------

### Merrill Bridge Prep

The Merrill Bridge Prep utility prepares a taxonomy for import into Merrill Bridge. It removes the date from the entity namespace, adds a comment header to all of the files, converts link role sort codes to the Bridge standard (from the previous Merrill sorting standard), deletes the instance document, and renames the schema and linkbases to remove the date.


### Merrill Bridge Sort

The Merrill Bridge Sort utility converts link role sort codes to the Bridge standard from the previous Merrill sorting standard. This is useful for comparing a taxonomy from a previous filing prepared by Merrill outside of Bridge to a current filing prepared in Bridge.


[1]: http://scottchacon.com/2011/08/31/github-flow.html
