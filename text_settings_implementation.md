# Aphrodite Text Settings Implementation

## Overview

The text settings for Aphrodite badges have been implemented, allowing for customization of:
- Font family
- Fallback font
- Text color
- Text size

## Files Modified/Created

1. **Modified Files**:
   - `aphrodite_helpers/apply_badge.py` - Updated with improved font and text handling

2. **New Files**:
   - `fonts/README.md` - Instructions for adding custom fonts
   - `test_text_settings.py` - Script to test text settings
   - `test_badge_appearance.py` - Script to test badge appearance with different settings
   - `test_download_and_badge.py` - Script to test downloading and badging a poster
   - `text_settings_readme.md` - Documentation for text settings

3. **Directories Created**:
   - `fonts/` - Directory for custom fonts
   - `posters/original` - Directory for original posters
   - `posters/working` - Working directory for processing
   - `posters/modified` - Directory for modified posters

## How to Use

### 1. Configure Text Settings

Edit the `badge_settings_audio.yml` file:

```yaml
Text:
  font: "Arial"                # Font name or file
  fallback_font: "DejaVuSans.ttf"  # Fallback font if primary not found
  text-color: "#FFFFFF"        # Text color (hex format)
  text-size: 40                # Font size in pixels
```

### 2. Add Custom Fonts (Optional)

Place your custom font files in the `fonts/` directory, then reference them in the settings file.

### 3. Test Badge Appearance

Use the `test_badge_appearance.py` script to test different badge settings:

```bash
python test_badge_appearance.py --text "DTS-HD MA" --bg-color "#FF0000" --text-color "#FFFFFF" --text-size 35
```

### 4. Test with Jellyfin

Use the `test_download_and_badge.py` script to test with a real Jellyfin item:

```bash
python test_download_and_badge.py --itemid "your-item-id" --text "DTS-HD MA"
```

## Implementation Notes

1. **Font Loading Improvements**:
   - Added a robust font loading system with multiple fallback options
   - Improved error handling when fonts cannot be loaded
   - Added support for both system fonts and custom font files

2. **Color Handling**:
   - Added support for backtick-quoted colors in YAML (e.g., "`#FFFFFF`")
   - Improved validation of hex color formats

3. **Text Rendering**:
   - Ensured proper text centering on badges
   - Enhanced text size calculations for dynamic badge sizing

4. **Testing Tools**:
   - Created specialized testing scripts to verify different aspects of the badge system
   - Added command-line options to easily override settings for testing

## Next Steps

1. **Font Installation**:
   - Add popular fonts to the `fonts/` directory for wider compatibility
   - Document system font availability on different platforms

2. **Text Styling**:
   - Consider adding support for text styling (bold, italic, etc.)
   - Implement multi-line text support for longer codec names

3. **Badge Templates**:
   - Create template presets for common audio codecs
   - Allow users to save and load custom badge templates
