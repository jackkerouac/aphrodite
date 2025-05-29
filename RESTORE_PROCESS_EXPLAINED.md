# Aphrodite Poster Restore - How It Works

## What the Restore Function Does

The "Restore Originals" feature in Aphrodite performs a **file-level restore** of your poster collection:

### ✅ What It Does:
1. **Copies original poster files** from `posters/original/` to `posters/modified/`
2. **Replaces modified versions** with the clean originals (removes all badges)
3. **Reports success/error statistics** for each file operation
4. **Preserves original files** (they remain untouched as backups)

### ⚠️ What It Doesn't Do (And Why):
- **Does NOT automatically re-upload to Jellyfin**
- **Jellyfin will still show the old modified posters** until you re-upload

## Why Jellyfin Still Shows Modified Posters

When Aphrodite processes posters, it follows this workflow:
1. **Download** original poster from Jellyfin → `posters/original/`
2. **Modify** poster (add badges) → `posters/modified/`
3. **Upload** modified poster back to Jellyfin's database

The restore function only handles step 1→2 (file copying), but **step 3 (upload) requires knowing which Jellyfin item ID each poster belongs to**.

Since poster filenames don't contain item IDs, the restore function cannot automatically re-upload them.

## How to Complete the Restore Process

After running "Restore Originals", you have several options to re-upload the clean posters to Jellyfin:

### Option 1: Re-process Individual Items
If you know specific item IDs that need restoring:
```bash
python aphrodite.py item [ITEM_ID] --no-audio --no-resolution --no-reviews
```
This will upload the restored (clean) poster without adding any badges.

### Option 2: Re-process Entire Libraries
To restore all posters in a library:
```bash
python aphrodite.py library [LIBRARY_ID] --no-audio --no-resolution --no-reviews
```
This uploads all restored posters without adding badges.

### Option 3: Manual Upload via Web Interface
Use the "Process Single Item" tab in the web interface:
- Enter the item ID
- **Uncheck all badge types** (audio, resolution, review)
- Enable "Skip Upload" = **OFF**
- Click "Process Item"

## File Structure After Restore

```
posters/
├── original/          # ✅ Clean originals (unchanged)
│   ├── movie1.jpg     # Original poster
│   └── show1.jpg      # Original poster
├── modified/          # ✅ Now contains restored clean posters
│   ├── movie1.jpg     # ← Restored from original (was badged)
│   └── show1.jpg      # ← Restored from original (was badged)
└── working/           # ⚠️ May contain outdated files
    └── temp files...
```

## Best Practices

1. **Run cleanup after restore** to clear working directory:
   ```bash
   python aphrodite.py cleanup --no-original --no-modified
   ```

2. **Test with a single item first** before restoring entire libraries

3. **Keep backups** - the original files serve as your backup, but consider additional backups for important collections

4. **Document your workflow** - keep track of which libraries/items you've restored vs. re-uploaded

## Future Enhancement Ideas

Possible improvements to make restore more seamless:
- Store item ID → filename mapping during processing
- Add option to automatically re-upload during restore
- Batch restore + re-upload workflows
- Integration with Jellyfin API to refresh poster cache

The current implementation prioritizes **safety and transparency** - you can see exactly what files were restored and manually control the re-upload process.
