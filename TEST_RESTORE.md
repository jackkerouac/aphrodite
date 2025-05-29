# Test Restore Endpoint

You can test the restore endpoint in several ways:

## 1. Using the Web Interface
1. Restart your application (Docker or development)
2. Go to http://localhost:2125 (or your dev port)
3. Navigate to Execute → Poster Management
4. Click "Restore Originals" tab
5. Click "Restore Original Posters" button

## 2. Using curl (command line)
```bash
curl -X POST http://localhost:2125/api/process/restore-originals
```

## 3. Using browser console
```javascript
fetch('/api/process/restore-originals', { method: 'POST' })
  .then(response => response.json())
  .then(data => console.log(data));
```

## Expected Response
If directories are empty:
```json
{
  "success": true,
  "message": "Restore completed. Restored 0 posters.",
  "restored_count": 0,
  "total_processed": 0,
  "errors": []
}
```

If directories don't exist:
```json
{
  "success": false,
  "message": "Original posters directory not found: [path]"
}
```

## Creating Test Files
To test with actual files, you can create some test files:

```bash
# Create directories
mkdir -p posters/original posters/modified

# Create test files
echo "original content" > posters/original/test.jpg
echo "modified content" > posters/modified/test.jpg

# Test restore
curl -X POST http://localhost:2125/api/process/restore-originals

# Check if modified file now has original content
cat posters/modified/test.jpg
```
