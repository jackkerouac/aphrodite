# Badge Color Test Script

This script (`test-badge-colors.js`) verifies that badge background colors are correctly applied in the badge rendering process.

## Purpose

The test script validates that:
1. Custom background colors are properly applied when specified
2. Brand colors are correctly applied when `use_brand_colors` is set to `true`
3. The priority order of background colors is functioning as expected

## Running the Test

To run the test:

```bash
node backend/test-badge-colors.js
```

## What the Test Does

1. Sets up a test database environment with badge settings
2. Creates test badge configurations:
   - Audio badge with `use_brand_colors = true` (should be BLUE)
   - Resolution badge with custom color (should be GREEN)
   - Review badge with standard color (should be BLACK)
3. Applies these badge configurations to a test poster
4. Saves the result to `temp/test-color-output.png`

## Expected Results

The output image should show:
- An audio badge in the top-left with a BLUE (#2E51A2) background
- A resolution badge in the top-right with a GREEN (#00AA00) background
- Review badges at the bottom with BLACK (#000000) backgrounds

## Troubleshooting

If colors are not appearing as expected, check:
1. The `use_brand_colors` setting in the badge configurations
2. The background color priority logic in `canvasUtils.js`
3. Whether badge types are being correctly identified
4. The console logs for any warnings or errors during the rendering process