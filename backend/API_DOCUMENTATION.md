# Jobs API Documentation

## Overview

The Jobs API provides endpoints for managing batch poster processing jobs in Aphrodite. It allows users to create jobs, track their progress, and view results.

## API Endpoints

### Get All Jobs

```
GET /api/jobs
```

Retrieves all jobs for a specific user with pagination.

**Query Parameters:**
- `userId` (required): The ID of the user
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)

**Response:**
```json
{
  "jobs": [...],
  "total": 25,
  "page": 1,
  "limit": 10,
  "totalPages": 3
}
```

### Create a New Job

```
POST /api/jobs
```

Creates a new job to process media items.

**Request Body:**
```json
{
  "user_id": 1,
  "name": "Process Action Movies",
  "items": [
    {
      "jellyfin_item_id": "abc123",
      "title": "Movie Title"
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Process Action Movies",
  "status": "pending",
  "items_total": 1,
  "items_processed": 0,
  "items_failed": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### Get Job Details

```
GET /api/jobs/:id
```

Gets details for a specific job.

**Query Parameters:**
- `userId` (required): The ID of the user (for security)

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Process Action Movies",
  "status": "running",
  "items_total": 10,
  "items_processed": 5,
  "items_failed": 1,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "completed_at": null
}
```

### Update Job Status

```
PUT /api/jobs/:id
```

Updates the status of a job.

**Request Body:**
```json
{
  "status": "running",
  "items_processed": 5,
  "items_failed": 1
}
```

**Valid Status Values:**
- `pending`: Job created but not started
- `running`: Job is currently processing
- `completed`: Job finished successfully
- `failed`: Job failed

**Response:**
Returns the updated job object.

### Get Job Items

```
GET /api/jobs/:id/items
```

Gets all items for a specific job with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 50)

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "job_id": 1,
      "jellyfin_item_id": "abc123",
      "title": "Movie Title",
      "status": "completed",
      "error_message": null,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "limit": 50,
  "totalPages": 1
}
```

### Start Job Processing

```
POST /api/jobs/:id/process
```

Starts processing a job asynchronously.

**Response:**
```json
{
  "message": "Job processing started",
  "jobId": "1"
}
```

### Update Job/Item Status (Internal)

```
POST /api/jobs/update-status
```

Internal endpoint used by the job processor to update status.

**Request Body:**
```json
{
  "jobId": 1,
  "status": "running",
  "itemId": 1,
  "itemStatus": "completed",
  "errorMessage": null
}
```

**Response:**
```json
{
  "success": true
}
```

## Docker Configuration

The job processing system is Docker-aware and uses the following environment variables:

- `IS_DOCKER`: Set to `true` when running in Docker
- `DATA_DIR`: Directory for persistent data storage
- `TEMP_DIR`: Directory for temporary files during processing

### Volume Mounts

In Docker environments, the following volumes should be mounted:

- `/app/data`: Persistent data storage
- `/app/temp`: Temporary files during processing
- `/app/logs`: Application logs

## Implementation Status

✅ **Completed:**
- Database schema (jobs and job_items tables)
- All API endpoints
- Job status update handlers
- Docker-aware file paths
- Basic job processing service
- Error handling and logging

🚧 **Still Needed:**
- Actual image processing logic (currently placeholder)
- WebSocket support for real-time updates
- Frontend components for job management
- Integration with badge overlay logic

## Next Steps

1. Implement the actual image processing logic in `imageProcessor.js`
2. Add WebSocket support for real-time job status updates
3. Create React components for the Run Aphrodite page
4. Test the complete end-to-end workflow
5. Add job scheduling capabilities
