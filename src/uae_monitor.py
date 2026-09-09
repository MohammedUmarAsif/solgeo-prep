"""Backward-compatible imports for the original UAE monitor notebook.

New work should import from :mod:`solgeo_prep`; this module remains so existing
notebooks and scripts do not break during the package transition.
"""

from solgeo_prep import *  # noqa: F403
