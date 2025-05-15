# Fonts Directory

This directory is used to store font files that can be used by the Aphrodite badge system.

## Adding Fonts

To add a font:

1. Place the font file (e.g., `.ttf`, `.otf`) in this directory
2. Update the `badge_settings_audio.yml` file to reference the font:

```yaml
Text:
  font: "YourFontName.ttf"  # Font file name
  fallback_font: "DejaVuSans.ttf"  # Fallback font if primary is not found
  text-color: "#FFFFFF"  # Text color (hexadecimal)
  text-size: 40  # Font size in pixels
```

## Default Behavior

If the specified font cannot be found:
1. The system will try to load the fallback font
2. If the fallback font cannot be found, the system will use the default PIL font

## Recommended Fonts

- Arial (system font)
- DejaVuSans.ttf (recommended to include in this directory for fallback)
- Any TrueType (.ttf) or OpenType (.otf) font file

## Font Search Paths

The system will search for fonts in the following locations:
1. System fonts (by font name)
2. Root project directory
3. This fonts directory (recommended location)
