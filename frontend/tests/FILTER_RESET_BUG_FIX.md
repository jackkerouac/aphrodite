# Poster Manager Filter Reset Bug Fix

## Issue Summary
When users selected 'Original Only' or 'Badged Only' filters in the poster manager and then changed libraries, the filters remained active in the UI but were not being applied to the search results. This caused confusion as the filter dropdown still showed the selected state but the results showed all items.

## Root Cause
The `useEffect` that handles library changes (`[selectedLibrary]`) was calling `loadLibraryItems()` which does not apply filters. The search/badge filters (`searchQuery` and `badgeFilter`) were not being reset when the library changed, so they stayed in their previous state visually but weren't being applied to the new library's data.

## Solution
Modified the `useEffect` for `selectedLibrary` changes to:
1. Reset `searchQuery` to empty string
2. Reset `badgeFilter` to 'all'
3. Reset `currentPage` to 1
4. Clear selection state (`selectedItems` and `selectionMode`)
5. Then load the new library's items

## Files Changed
- `E:\programming\aphrodite\frontend\src\app\poster-manager\page.tsx`

## Code Changes
```typescript
useEffect(() => {
  if (selectedLibrary) {
    // Reset filters and selection when library changes
    setSearchQuery("")
    setBadgeFilter('all')
    setCurrentPage(1)
    setSelectedItems(new Set())
    setSelectionMode(false)
    
    loadLibraryItems()
    loadLibraryStats()
  }
}, [selectedLibrary])
```

## Expected Behavior After Fix
1. User selects a library
2. User sets badge filter to "Badged Only" or "Original Only"
3. User enters a search query (optional)
4. User changes to a different library
5. ✅ Badge filter resets to "All Items"
6. ✅ Search query is cleared
7. ✅ Page resets to 1
8. ✅ Selection is cleared
9. ✅ Results show all items from the new library (no filters applied)

## Testing Steps
1. Build and start the Docker container
2. Navigate to Poster Manager
3. Run the test script in browser console: `/frontend/tests/poster-manager-filter-reset.test.js`
4. Follow the manual test steps output by the script
5. Verify that filters reset when changing libraries

## Backward Compatibility
This fix is completely backward compatible and only improves the user experience. No API changes were required.
