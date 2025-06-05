#!/usr/bin/env python3
# aphrodite_helpers/badge_components/badge_settings.py

import os
import yaml
import logging

# Import the compatibility layer
from aphrodite_helpers.settings_compat import load_badge_settings as load_badge_settings_compat

def load_badge_settings(settings_file="badge_settings_audio.yml"):
    """Load badge settings from the provided YAML file or database."""
    # Use the compatibility layer which handles both SQLite and YAML
    return load_badge_settings_compat(settings_file)
