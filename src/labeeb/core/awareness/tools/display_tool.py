"""
Labeeb Display Tool

This module provides display-related functionality for Labeeb.
It handles screen management, display settings, and visual output capabilities.
""" 

import gettext
import os

# Set up internationalization
locale_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'locale')
gettext.bindtextdomain('labeeb', locale_dir)
gettext.textdomain('labeeb')
_ = gettext.gettext

# Replace any user-facing strings with _() function 