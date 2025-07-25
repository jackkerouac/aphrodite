# Maintenance Overview

The Maintenance module provides comprehensive system management tools and diagnostics for Aphrodite v2, offering administrators essential capabilities for monitoring system health, managing external service connections, and maintaining database integrity.

## Interface Tabs

### Connection Check Tab
Validates connectivity to all configured external services and APIs essential for Aphrodite's operation.

### Database Operations Tab  
Manages database health, integrity checks, backup operations, and storage monitoring.

### Logs Tab
Provides access to application logs with filtering, searching, and management capabilities.

## Connection Check System

<img width="1223" height="868" alt="maintenance-connection" src="https://github.com/user-attachments/assets/9c3d7953-8a7a-4a68-a06b-9099af6f2d14" />

### API Service Validation

**External Service Testing**  
The Connection Check tab provides comprehensive connectivity testing for all integrated external services:

**Jellyfin Integration**  
- **Purpose**: Media server connectivity for library access and poster management
- **Test Function**: Validates connection using configured API key
- **Status**: Real-time connection status with "Not tested" initial state
- **Action**: Manual test trigger with "Test Connection" button

**OMDB Service**  
- **Purpose**: Movie database integration for metadata and rating information
- **Test Function**: Validates OMDB API connectivity with configured credentials
- **Status**: Connection health indicator showing current test results
- **Action**: On-demand connection verification

**TMDB Integration**  
- **Purpose**: The Movie Database API for comprehensive movie and TV show metadata
- **Test Function**: Validates TMDB API access using configured API key
- **Status**: Real-time connectivity status monitoring
- **Action**: Manual connection testing capability

**MDBList Service**  
- **Purpose**: Movie database list integration for enhanced metadata
- **Test Function**: Validates MDBList API connectivity and authentication
- **Status**: Current connection state with detailed status reporting
- **Action**: Immediate connection verification

**AniDB Integration**  
- **Purpose**: Anime database connectivity for specialized anime metadata
- **Test Function**: Validates AniDB connection using configured credentials
- **Status**: Authentication and connectivity status monitoring
- **Action**: Manual connection testing with detailed feedback

### Service Health Monitoring

**Comprehensive Connectivity Overview**  
- **Unified Testing**: Single interface to test all external service connections
- **Status Tracking**: Real-time connection status for each integrated service
- **Error Detection**: Immediate identification of connectivity issues
- **Configuration Validation**: Ensures all API keys and credentials are properly configured

## Database Operations Management

<img width="1216" height="878" alt="maintenance-database" src="https://github.com/user-attachments/assets/ceb778fb-af2f-48f5-bffb-ecb7b875e5d9" />

### Database Health Dashboard

**Database Status Monitoring**  
Real-time database health information with comprehensive metrics:

**Connection Status**  
- **Active Connection**: Green "Active" status indicator showing healthy database connection
- **Connection String**: Full PostgreSQL connection details
- **Real-time Monitoring**: Continuous connection health verification

**Database Metrics**  
- **Database Size**: Current storage utilization (9149 kB)
- **Schema Information**: Table count and structure details
- **Storage Monitoring**: Track database growth and storage consumption

**Backup Management**  
- **Available Backups**: Count of existing database backups 
- **Backup Location**: Storage path for backup files
- **Backup History**: Track of previous backup operations

**Integrity Monitoring**  
- **Integrity Status**: Database consistency verification
- **Manual Checking**: "Check Now" button for immediate integrity verification
- **Health Validation**: Comprehensive database health assessment

### Backup Operations System

**Database Backup Management**  
Comprehensive backup creation and management capabilities:

**Create New Backup**  
- **Compression Option**: "Compress backup" checkbox for storage efficiency
- **Backup Creation**: "Create Backup" button for immediate backup generation
- **Automated Processing**: Background backup creation with progress monitoring

**Available Backups Display**  
- **Backup Inventory**: List of all available database backups
- **Backup Metadata**: Creation timestamps and backup sizes
- **Restore Capabilities**: Easy restoration from any available backup point

## Application Logs Management

<img width="1232" height="772" alt="maintenance-logs" src="https://github.com/user-attachments/assets/587d855e-d42b-4fb3-ba97-49c0e337e49c" />

### Log Viewing and Analysis

**Comprehensive Log Access**  
Advanced log management with filtering and search capabilities:

**Log Level Filtering**  
- **Level Selection**: "All Levels" dropdown for filtering by log severity
- **Granular Control**: Filter by specific log levels (ERROR, WARNING, INFO, DEBUG)
- **Targeted Monitoring**: Focus on specific types of log entries

**Log Search Functionality**  
- **Message Search**: "Search log messages..." field for content-specific searching
- **Pattern Matching**: Find specific error messages or system events
- **Real-time Filtering**: Instant search results as you type

**Log Management Actions**  
- **Search Execution**: Magnifying glass icon for search activation
- **Refresh Logs**: Real-time log updates with refresh capability
- **Copy Logs**: Export log content for external analysis
- **Download Logs**: Save log files for archival or support purposes
- **Clear Logs**: Remove old log entries for system maintenance

### Log Status Display

**Log Information Overview**  
- **Total Lines**: Current log file size (0 total lines in example)
- **File Status**: Log file existence and modification tracking
- **Storage Size**: Log file size monitoring (0 B)
- **Last Modified**: Timestamp tracking for log activity

**Empty State Handling**  
- **No Logs Found**: Clear indication when log file is empty or doesn't exist
- **Status Message**: "The log file is empty or doesn't exist yet."
- **System Readiness**: Indicates clean system start or successful log rotation

## System Integration Benefits

### Proactive System Management

**Health Monitoring**  
- **Service Connectivity**: Immediate identification of external service issues
- **Database Health**: Continuous monitoring of data integrity and performance
- **Log Analysis**: Real-time system behavior monitoring and troubleshooting

**Preventive Maintenance**  
- **Connection Validation**: Regular testing prevents service interruptions
- **Database Backups**: Automated backup scheduling protects against data loss
- **Integrity Checks**: Proactive database health verification

### Troubleshooting Support

**Diagnostic Capabilities**  
- **Service Testing**: Individual service connectivity verification
- **Error Identification**: Immediate detection of configuration or connectivity issues
- **Log Analysis**: Detailed system behavior tracking for issue resolution

**Administrative Control**  
- **Manual Testing**: On-demand verification of system components
- **Backup Management**: Flexible backup creation and restoration options
- **Log Management**: Comprehensive log viewing and maintenance tools

## Use Cases and Workflows

### Routine System Checks

**Daily Health Verification**  
- **Connection Testing**: Verify all external services remain accessible
- **Database Monitoring**: Check database size and performance metrics
- **Log Review**: Monitor system activity and identify potential issues

### Troubleshooting Workflows

**Service Issue Resolution**  
- **Connection Diagnosis**: Test individual services to isolate connectivity problems
- **Error Investigation**: Use log analysis to identify root causes
- **Configuration Validation**: Verify API keys and service settings

### Backup and Recovery Operations

**Data Protection**  
- **Regular Backups**: Create scheduled database backups for data protection
- **Integrity Verification**: Perform regular database consistency checks
- **Recovery Planning**: Maintain backup inventory for disaster recovery

The Maintenance module ensures system reliability through comprehensive monitoring, proactive health checks, and robust backup capabilities, providing administrators with essential tools for maintaining optimal Aphrodite performance.
