thinX
=====

thinX is a GUI that implements various utilities for manipulating XBRL files.


### Version

0.6.0


### Dependencies

thinX is developed with Python 3 and PyQt.


### Versioning

* Major version bumps accompany the passing of milestones.
* Minor version bumps accompany new features.
* Patch version bumps accompany bug fixes.


### Contributing

thinX follows the [GitHub Flow][1] branching model.

* Anything in the master branch is deployable
* To work on something new, create a descriptively named branch off of master (ie: new-oauth2-scopes)
* Commit to that branch locally and regularly push your work to the same named branch on the server
* When you need feedback or help, or you think the branch is ready for merging, open a pull request
* After someone else has reviewed and signed off on the feature, you can merge it into master
* Once it is merged and pushed to ‘master’, you can and should deploy immediately


Utilities
---------

### Comply with UTR

The UTR utility adds each namespace supplied in the units.ini configuration file and searches the selected instance document for measures which match those defined in units.ini. If a match is found under a different namespace, the prefix for the proper namespace is used, and the capitalization of the measure is corrected if necessary.

### Remove Unused Contexts

The Unused Contexts utility searches the selected instance document for declared contexts that are not in use. All unused contexts are logged and removed from the file.


### Duplicate Calculations

The Duplicate Calculations utility searches the corresponding calculation linkbase of the selected instance document for duplicate calculation relationships. All duplicate calculations are logged.


[1]: http://scottchacon.com/2011/08/31/github-flow.html
