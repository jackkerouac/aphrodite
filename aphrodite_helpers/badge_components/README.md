# Badge Components

This directory contains modular components for the badge generation and application system.

## Structure

- `badge_settings.py`: Handles loading and parsing badge settings from YAML files
- `color_utils.py`: Utilities for color processing (hex to RGBA conversion)
- `font_utils.py`: Font loading with fallback mechanisms
- `badge_generator.py`: Creates badge images with proper styling and text
- `badge_applicator.py`: Applies badges to poster images
- `workflow.py`: Higher-level functions for end-to-end processing

## Font Requirements

Fonts should be placed in the `fonts` directory at the project root. The system will look for fonts in this priority order:

1. The `fonts` directory (e.g., `E:\programming\aphrodite-python\fonts\Arial.ttf`)
2. System fonts
3. Project root directory

## Usage

Use the main `apply_badge.py` script outside this directory as the entry point.
