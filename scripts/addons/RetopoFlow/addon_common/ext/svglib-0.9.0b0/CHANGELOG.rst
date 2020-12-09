.. -*- mode: rst -*-

ChangeLog
=========

Sadly, no condensed changelog exists prior to version 0.6.3.

0.6.3:

- frozen last version maintained at https://bitbucket.org/deeplook/svglib/

0.8.0:

- moved repository to https://github.com/deeplook/svglib
- skipped version 0.7.0 to indicate tons of fixes regarding the points below
- added support for elliptical arcs
- fixed open/closed path issues
- fixed clip path issues
- fixed text issues
- replaced ``minidom`` with ``lxml``
- added ``logging`` support
- added a few more sample SVG files
- migrated test suite from unittest to pytest
- improved test documentation

0.8.1:

- added support for the ``stroke-opacity`` property
- added basic em unit support for text placement
- added respecting absolute coordinates for tspan
- fixed crash with empty path definitions
- symbol definitions are considered when referenced in nodes
- fixed compatibility with recent ReportLab versions

0.9.0b0:

- countless improvements to be hopefully listed in more detail in 0.9.0
