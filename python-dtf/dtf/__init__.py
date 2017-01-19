"""Main dtf Module"""

from __future__ import absolute_import
import pkg_resources

# Here we use the installed version as version number. For tests,
# this may not exist so we just fake it and return unknown.
# pylint: disable=maybe-no-member
try:
    __version__ = pkg_resources.get_distribution('dtf').version
except pkg_resources.DistributionNotFound:
    __version__ = "???"
