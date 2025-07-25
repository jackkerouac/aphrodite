# Schedules Overview

The Schedules module provides comprehensive automated poster processing capabilities, allowing you to set up recurring jobs that enhance your media library posters on a predetermined schedule with full customization and monitoring.

## Interface Tabs

### Schedules Tab
Manage active automated schedules with real-time status monitoring and control options.

### History Tab  
Review completed schedule executions with detailed processing results and performance metrics.

### Create Schedule Tab
Configure new automated poster processing schedules with advanced timing and processing options.

## Schedule Creation & Configuration

### Basic Information Setup

**Schedule Identity**  
- **Schedule Name**: Custom naming for easy identification and management
- **Timezone Configuration**: UTC and local timezone support for accurate timing
- **Quick Presets**: Pre-configured timing templates for common scheduling needs
- **Custom Expression**: Advanced cron expression support for precise timing control

**Advanced Timing Control**  
- **Cron Expression**: Manual cron configuration (e.g., "0 2 * * *" for daily 2 AM execution)
- **Enable/Disable Toggle**: Instant schedule activation control
- **Preset Options**: Common schedules like daily, weekly, monthly patterns

### Processing Options Configuration

<img width="1214" height="525" alt="schedules-create01" src="https://github.com/user-attachments/assets/5e91406c-d325-4022-bccb-3dfc91671efe" />
<img width="1223" height="625" alt="schedules-create02" src="https://github.com/user-attachments/assets/6f678ff2-edf8-41dc-b98b-44bdc90ac043" />

**Badge Type Selection**  
Customize which enhancements to apply during scheduled runs:
- **Resolution Badges**: 4K, 1080p, HDR quality indicators
- **Review Badges**: IMDb, TMDb, Rotten Tomatoes ratings
- **Audio Badges**: DTS-HD, Atmos, Dolby Digital codec indicators
- **Awards Badges**: Oscar, Emmy, Golden Globe recognition markers

**Processing Behavior**  
- **Reprocess All Items**: When enabled, processes all items regardless of existing 'aphrodite-overlay' metadata
- **Selective Processing**: Only enhance items without existing badges for efficiency
- **Smart Detection**: Automatically skip previously processed items to avoid duplication

### Target Library Selection

**Library Targeting**  
Choose specific Jellyfin libraries for scheduled processing:
- **Movies Library**: "movies" collection targeting
- **Television Library**: "tvshows" collection processing  
- **Anime Library**: "tvshows" specialized anime collections
- **All Libraries**: Process entire media collection when no specific libraries selected

**Flexible Targeting**  
- **Selective Processing**: Choose specific libraries for targeted enhancement
- **Global Processing**: Leave all unchecked to process all movie and TV show libraries
- **Library Status**: Real-time indication of selection status and processing scope

## Active Schedule Management

### Schedule Overview Display

<img width="1228" height="442" alt="schedules-overview" src="https://github.com/user-attachments/assets/4382fc05-5d3e-4f05-b77e-990c13785cc4" />

**Schedule Information Card**  
Active schedules show comprehensive details:
- **Schedule Name**: "[Daily] Movies, Television Scan" with clear identification
- **Execution Timing**: "Daily at 2:00 AM • America/Toronto" timezone specification
- **Status Indicator**: "Enabled" badge showing current operational state
- **Badge Configuration**: "resolution, review, awards" showing applied enhancement types
- **Target Scope**: "2 selected" libraries indicating processing coverage
- **Reprocess Setting**: "No" indicating selective processing mode

### Schedule Controls

**Real-time Management**  
- **Enable/Disable Toggle**: Instant schedule activation/deactivation
- **Manual Execution**: Trigger immediate schedule run with play button
- **Edit Configuration**: Modify schedule settings with edit button
- **Delete Schedule**: Remove schedules with confirmation protection

**Status Monitoring**  
- **Active Status**: Visual indicators showing schedule operational state
- **Next Execution**: Automatic calculation of upcoming run times
- **Configuration Summary**: At-a-glance view of all schedule parameters

## Schedule History & Monitoring

<img width="1231" height="717" alt="schedules-history" src="https://github.com/user-attachments/assets/8608b35f-730b-4844-83a9-bd3cc313cb29" />

### Execution History Tracking

**Detailed Execution Records**  
Complete history shows:
- **Execution ID**: Unique identifiers (f8bec3a4, f2de10aa) for precise tracking
- **Creation Timestamps**: Exact schedule creation times (2025-07-23, 2:00:11 a.m.)
- **Processing Duration**: Execution time tracking (Duration: 6s)
- **Completion Status**: "Completed" badges with visual success indicators

**Performance Metrics**  
- **Started Time**: Precise execution start timestamps
- **Completed Time**: Exact completion timestamps for duration calculation
- **Processing Statistics**: Detailed item processing counts and results

### Execution Details

**Comprehensive Processing Data**  
Each execution provides detailed metrics:
- **Total Items**: Complete library scan results
- **Processed Items**: Actual enhancement count
- **Failed Items**: Error tracking for troubleshooting
- **Badge Types Applied**: Specific enhancements used ["resolution", "review", "awards"]
- **Target Libraries**: Library IDs processed during execution
- **Processing Method**: Job-based or direct processing indication

**History Management**  
- **Status Filtering**: "All Status" dropdown for filtering by completion state
- **Refresh Capability**: Real-time history updates with refresh button
- **Clear History**: Bulk removal option for history maintenance
- **Execution Search**: Find specific executions by ID or characteristics

## Automation Benefits

### Hands-Free Processing

**Automated Enhancement**  
- **Scheduled Execution**: Set-and-forget poster enhancement runs
- **Consistent Quality**: Uniform badge application across entire library
- **New Media Detection**: Automatic processing of newly added content
- **Maintenance Scheduling**: Regular library optimization without manual intervention

**Smart Processing Logic**  
- **Efficient Operations**: Skip already-processed items for faster execution
- **Selective Enhancement**: Target specific badge types based on media characteristics
- **Library-Specific Rules**: Different processing profiles for movies vs TV shows
- **Resource Optimization**: Background processing during low-usage periods

### Monitoring & Control

**Execution Transparency**  
- **Real-time Status**: Live monitoring of schedule execution progress
- **Historical Analysis**: Track processing patterns and performance over time
- **Success Metrics**: Monitor completion rates and processing efficiency
- **Error Detection**: Immediate notification of processing issues

**Flexible Management**  
- **Dynamic Scheduling**: Modify schedules without losing historical data
- **Emergency Controls**: Instant enable/disable for schedule management
- **Manual Override**: Trigger immediate execution when needed
- **Configuration Backup**: Preserve schedule settings for easy restoration

## Use Cases & Workflows

### Daily Library Maintenance
**Scenario**: Automatically enhance new movie additions every night
- **Schedule**: Daily at 2:00 AM during low system usage
- **Target**: Movies library only for focused processing
- **Badges**: Resolution, review, and awards for comprehensive enhancement
- **Mode**: Selective processing to handle only new additions efficiently

### Weekly TV Show Updates
**Scenario**: Process TV show library weekly after new episode releases
- **Schedule**: Weekly on Sunday mornings for fresh content
- **Target**: Television library with episode-specific processing
- **Badges**: Resolution and review badges for episode quality indicators
- **Mode**: Full reprocessing to catch metadata updates and new episodes

### Complete Library Refresh
**Scenario**: Monthly comprehensive library enhancement
- **Schedule**: First Sunday of each month for complete maintenance
- **Target**: All libraries for system-wide consistency
- **Badges**: All badge types for maximum enhancement coverage
- **Mode**: Reprocess all items to ensure uniform quality standards

The Schedules module transforms manual poster management into an automated, reliable system that maintains consistent library quality while providing complete control and transparency over processing operations.
