#!/usr/bin/env python3
# aphrodite_helpers/badge_components/__init__.py

# Import key functions to make them available at package level
from .badge_settings import load_badge_settings
from .badge_generator import create_badge
from .badge_applicator import apply_badge_to_poster, process_posters
from .workflow import download_and_badge_poster, process_all_posters, save_test_badge
