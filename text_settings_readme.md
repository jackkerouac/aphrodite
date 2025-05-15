# Text Settings for Aphrodite Badges

This document explains how to configure text settings for audio badges in Aphrodite.

## Configuration

Text settings are defined in the `badge_settings_audio.yml` file under the `Text` section:

```yaml
Text:
  font: "Arial"                # Font name or file
  fallback_font: "DejaVuSans.ttf"  # Fallback font if primary not found
  text-color: "#FFFFFF"        # Text color (hex format)
  text-size: 40                # Font size in pixels
```

## Font Settings

### Font Family

- `font`: Specifies the primary font to use for badges.
  - You can use a system font name (e.g., "Arial", "Helvetica") 
  - Or specify a font file path relative to the project root
  - For best results, place custom fonts in the `fonts/` directory

### Fallback Font

- `fallback_font`: Used if the primary font cannot be loaded
  - Recommended to keep "DejaVuSans.ttf" as fallback
  - If you add custom fonts, place them in the `fonts/` directory

### Text Color

- `text-color`: Hex color code for the text
  - Standard hex format: "#FFFFFF" (white)
  - May be wrapped in backticks in YAML: "`#FFFFFF`"

### Text Size

- `text-size`: Font size in pixels
  - Recommended: 30-50 for most badges
  - Smaller sizes may be needed for longer text

## Font Search Order

When loading fonts, Aphrodite will search in this order:
1. Exact path specified
2. Project root directory
3. `fonts/` subdirectory
4. System fonts
5. Fallback font (using the same search order)
6. If all fails, the default PIL font is used

## Testing Text Settings

You can test text settings using the provided test script:

```bash
python test_text_settings.py --text "DTS-HD MA" --font "Arial" --font-size 40 --text-color "#FF0000"
```

This will generate a test badge with the specified text and settings.
