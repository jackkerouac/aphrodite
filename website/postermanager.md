# Poster Manager Overview

The Poster Manager is Aphrodite's core media management interface, providing comprehensive tools for browsing, enhancing, and processing your Jellyfin library posters with intelligent batch operations and detailed poster customization.

## Main Interface Tabs

### Library Tab
The primary workspace for managing your media collection with visual poster browsing and advanced processing capabilities.

### Jobs Tab  
Background processing monitor showing active, completed, and failed poster enhancement jobs with real-time progress tracking.

## Library Management Features

### Library Selection & Overview

<img width="1224" height="844" alt="postermanager-overview01" src="https://github.com/user-attachments/assets/803efcee-4c65-4dd5-82a9-1aa47affde55" />

**Library Selector**  
Choose from your available Jellyfin libraries (Movies, TV Shows, etc.) with automatic detection and connection status indicators.

**Library Statistics Dashboard**  
Comprehensive overview showing:
- **Total Items**: Complete media count (1,386 items shown in example)
- **Movies**: Film collection size (1,378 movies)
- **TV Shows**: Series collection count (0 TV shows in example)
- **Genres**: Unique genre categories (19 genres)

Real-time statistics help you understand your collection size and distribution across different media types.

### Search & Filtering System

**Advanced Search Capabilities**  
- **Title Search**: Find specific media by title with real-time filtering
- **Badge Status Filter**: View All Items, only Badged items, or Original posters
- **Content Type Filter**: Separate movies, TV shows, and other media types

**Filter Management**  
- Clear all filters with one click
- Persistent filter states during library browsing
- Search result pagination with customizable items per page (50 items default)

## Poster Grid Interface

### Visual Poster Display

<img width="1231" height="881" alt="postermanager-overview02" src="https://github.com/user-attachments/assets/1f84cf8e-32e5-4bab-b6c9-556fee94cd26" />

**Enhanced Poster Cards**  
Each media item displays:
- **High-Quality Poster**: Full-resolution poster artwork with 1080p FHD badges
- **Rating Indicators**: Multiple rating sources (IMDb 82%, TMDb 80%, RT 88%)
- **Genre Tags**: Visual genre categories (War, Drama, Action, etc.)
- **Year Information**: Release year badges (2019, 1968, etc.)
- **Badge Status**: Clear indicators showing BADGED vs ORIGINAL status
- **Quality Metrics**: Resolution and processing status indicators

**Interactive Elements**  
- Click any poster to open detailed view modal
- Checkbox selection for batch operations
- Visual selection highlighting with blue borders
- Hover effects showing additional metadata

### Pagination & Navigation

**Flexible Viewing Options**  
- **Page Controls**: Navigate through large collections (Page 1 of 28 shown)
- **Items per Page**: Customize display density (50, 100, 200 items)
- **Total Count Display**: "Showing 1 to 50 of 1378 items"
- **Quick Navigation**: Jump to specific pages or use next/previous controls

## Individual Poster Management

### Detailed Poster Modal

<img width="541" height="668" alt="postermanager-overview03" src="https://github.com/user-attachments/assets/f82b5147-1bc1-407a-bd2c-821b9e673706" />

**Comprehensive Media Information**  
- **Movie Details**: Title, year, rating, genres, and overview
- **Technical Specifications**: Jellyfin ID and internal tracking numbers
- **Rating Display**: 8.0/10 with R rating indicator
- **Genre Tags**: War, Drama, Action, Thriller, History classifications

**Poster Enhancement Options**  
- **Apply Badges**: Add resolution, rating, and award badges
- **Remove Aphrodite Tag**: Clear enhancement markers
- **Replace Poster**: Search and select alternative poster artwork
- **Restore to Original**: Revert to unmodified poster

### Badge Application System

<img width="547" height="570" alt="postermanager-overview04" src="https://github.com/user-attachments/assets/5298557e-a185-4847-b678-61115731e44f" />

**Selective Badge Types**  
- **Audio Codec**: DTS-HD MA, Atmos, Dolby Digital Plus indicators
- **Resolution**: 4K, 1080p, HDR, Dolby Vision quality badges
- **Reviews & Ratings**: IMDb, TMDb, Rotten Tomatoes, Metacritic scores
- **Awards**: Oscars, Emmys, Golden Globes recognition badges

**Batch Badge Operations**  
- Select multiple badge types simultaneously
- Apply to single poster or entire selection
- Preview badge combinations before applying
- "Apply 3 Badges" button for streamlined processing

### Poster Replacement System

<img width="540" height="856" alt="postermanager-overview05" src="https://github.com/user-attachments/assets/5d0a5088-4931-4ea6-a3d5-b45db49d7b87" />

**External Source Integration**  
- **Automatic Search**: "Searching external sources for alternative posters for 1917 (2019)"
- **Language Filtering**: English (27) posters with language selection
- **Quality Metrics**: File size (14.3 MB), resolution (TMDb 3000), and rating data
- **Community Ratings**: User vote counts and score averages (5.9/10, 7.0/10, etc.)

**Poster Selection Grid**  
- **Multiple Options**: 27 of 30 available posters displayed
- **Preview Thumbnails**: High-quality poster previews
- **Metadata Display**: Language, size, rating, and vote information
- **Easy Selection**: Click to select replacement poster

## Batch Processing Capabilities

### Multi-Selection Operations

<img width="1220" height="815" alt="postermanager-overview06" src="https://github.com/user-attachments/assets/17ad4c69-7197-46e9-95ce-52c13ddbfa50" />

**Selection Management**  
- **Individual Selection**: Checkbox on each poster for precise control
- **Bulk Selection**: "Select All" and "Select None" operations
- **Selection Counter**: "4 posters selected" with clear selection indicators
- **Visual Feedback**: Blue highlighted borders on selected items

**Batch Processing Options**  
- **Create Batch Job**: Process multiple posters simultaneously
- **Replace Posters**: Bulk poster replacement operations
- **Track in Jobs Tab**: Monitor batch progress with real-time updates

### ⚙️ Background Processing

**Job Management**  
- **Progress Tracking**: "4 posters will be processed in the background"
- **Real-time Updates**: Live progress monitoring during batch operations
- **Job History**: Complete processing history with timestamps and results

**Processing Results**  
Recent batch operations show:
- **Batch Processing - 2025-07-22**: 10 posters with completion status
- **Success Indicators**: "All 10 posters processed successfully"
- **Job Completion**: Green "completed" badges with processing times

## Workflow Integration

### Seamless Job Processing

**Background Operations**  
- Non-blocking poster enhancement processing
- Real-time job status updates
- Automatic library refresh after completion
- Progress tracking with estimated completion times

**Quality Assurance**  
- **Success Rate Monitoring**: 100% completion rates displayed
- **Error Handling**: Failed operations clearly marked
- **Retry Capabilities**: Re-process failed items individually
- **Cache Management**: Automatic poster cache refresh after modifications

## Key Benefits

The Poster Manager transforms complex media library management into an intuitive, visual experience:

- **Visual Discovery**: Browse your entire collection with high-quality poster previews
- **Intelligent Enhancement**: Apply appropriate badges based on media characteristics
- **Batch Efficiency**: Process hundreds of posters with minimal manual intervention
- **Quality Control**: Preview and select optimal poster artwork from multiple sources
- **Real-time Feedback**: Immediate visual updates showing enhancement progress
- **Flexible Workflow**: Switch between individual poster fine-tuning and bulk processing

The Poster Manager ensures your media library maintains consistent, professional-quality poster artwork while providing the flexibility to customize individual items according to your preferences.
