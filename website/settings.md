# Settings Overview

The Settings module provides comprehensive configuration management for all aspects of Aphrodite's poster enhancement system, from external service integration to detailed badge customization across multiple categories.

## Settings Categories

### API Tab
Configure connections to external services including Jellyfin, OMDB, and other metadata providers.

### Audio Tab
Customize audio codec badge appearance, positioning, and styling with advanced configuration options.

### Resolution Tab
Configure resolution quality badge settings including size, position, and visual properties.

### Review Tab
Manage review source integration and badge display settings for rating information from multiple platforms.

### Awards Tab
Configure awards badge display for recognition markers like Oscars, Emmys, and other prestigious awards.

## API Settings Configuration

<img width="1277" height="895" alt="settings-api" src="https://github.com/user-attachments/assets/f7d0671e-3bf6-4a5c-9951-cf84fc4f8afa" />

### Jellyfin Connection Setup

**Media Server Integration**  
Primary connection configuration for Jellyfin media server access:

**Server Configuration**  
- **Server URL**: Full Jellyfin server address (https://jellyfin.example.com)
- **API Key**: Secure authentication token for server access
- **User ID**: Specific Jellyfin user account identifier
- **Required Fields**: All fields marked with asterisks are mandatory for connection

**Connection Validation**  
- **Test Connection**: Built-in connectivity testing to verify configuration
- **Real-time Validation**: Immediate feedback on connection status
- **Configuration Help**: "How to find your Jellyfin User ID" guidance link

### External Metadata Services

**OMDB API Integration**  
Open Movie Database configuration for additional metadata:
- **API Key**: Authentication key for OMDB service access
- **Cache Expiration**: Configurable cache duration in minutes for performance optimization

**Service Integration Benefits**  
- **Enhanced Metadata**: Additional movie and TV show information
- **Rating Aggregation**: Multiple rating source integration
- **Performance Optimization**: Intelligent caching to reduce API calls

## Badge Configuration System

<img width="1268" height="741" alt="settings-audio" src="https://github.com/user-attachments/assets/1474042e-fce0-4d41-990c-5871f508f2d8" />

### Audio Badge Settings

**Advanced Audio Configuration**  
Comprehensive audio codec badge customization with multiple configuration tabs:

**General Badge Settings**  
- **Badge Size**: Configurable dimensions (300px default)
- **Badge Position**: Placement options (Top Right positioning)
- **Edge Padding**: Border spacing control (30px default)
- **Text Padding**: Internal text spacing (12px default)
- **Use Dynamic Sizing**: Automatic size adjustment based on content

**Advanced Configuration Tabs**  
- **General**: Basic positioning and sizing controls
- **Text**: Typography and text styling options
- **Background**: Badge background appearance settings
- **Border**: Edge styling and border configuration
- **Shadow**: Drop shadow and depth effects
- **Images**: Icon and image integration settings
- **Enhanced**: Advanced visual effects and features
- **Performance**: Rendering optimization settings
- **Diagnostics**: Configuration validation and troubleshooting

### Resolution Badge Settings

<img width="1277" height="739" alt="settings-resolution" src="https://github.com/user-attachments/assets/9109a995-9971-4e0f-acd5-feb18fc554e1" />

**Resolution Quality Configuration**  
Specialized settings for video quality badge display:

**Basic Configuration**  
- **Badge Size**: Resolution-specific sizing (300px standard)
- **Badge Position**: Strategic placement (Top Left positioning)
- **Edge Padding**: Optimal spacing for resolution badges (30px)
- **Text Padding**: Internal text positioning (12px)
- **Dynamic Sizing**: Automatic adjustment for different resolution labels

**Configuration Consistency**  
- **Unified Interface**: Consistent configuration structure across badge types
- **Visual Harmony**: Coordinated settings ensure badges work well together
- **Template System**: Reusable configuration patterns for efficiency

### Review Badge Settings

<img width="1246" height="900" alt="settings-review" src="https://github.com/user-attachments/assets/1be551a9-00da-4dbf-b425-82058c4d83f8" />

**Review Source Management**  
Comprehensive review and rating badge configuration system:

**Review Source Availability**  
Currently functional review sources with active integration:
- **IMDb**: Internet Movie Database ratings
- **Metacritic**: Professional critic aggregation scores
- **MyAnimeList**: Specialized anime and manga ratings
- **Rotten Tomatoes Critics**: Professional critic consensus ratings
- **TMDb**: The Movie Database community ratings

**Review Sources Control**  
- **Max Badges to Display**: Limit number of review badges (4 badges maximum)
- **Selection Mode**: Priority-based badge selection algorithm
- **Convert to Percentage**: Standardize all ratings to percentage format
- **Priority Order**: Drag-to-reorder source priority system

**Source Priority Management**  
- **Drag-to-Reorder Interface**: "Review Sources (Drag to reorder)" functionality
- **IMDb Priority**: Currently positioned as primary source
- **Max Variants**: Configurable variant count (3 variants for IMDb)
- **Enable/Disable Toggle**: Individual source activation control
- **Dynamic Ordering**: Real-time priority adjustment with visual feedback

### Awards Badge Settings

<img width="1269" height="883" alt="settings-awards" src="https://github.com/user-attachments/assets/25ed6457-e367-4459-97d1-14cf9296d120" />

**Awards Recognition Configuration**  
Specialized settings for prestigious awards badge display:

**General Awards Settings**  
- **Enable Awards Badges**: Master toggle for awards badge functionality
- **Badge Description**: "Awards badges appear flush in the bottom-right corner when media has won specific awards"
- **Badge Size**: Awards-specific sizing (351px recommended for full native resolution)
- **Badge Position**: Fixed "Bottom-Right Flush" positioning for optimal ribbon appearance

**Awards-Specific Features**  
- **Flush Positioning**: Awards badges positioned flush to bottom-right corner with no padding
- **Dynamic Sizing**: Automatic badge size adjustment based on award content
- **Edge Padding**: Zero padding for flush positioning (0px)
- **Text Padding**: Minimal internal padding for awards display (0px)
- **Specialized Rendering**: Optimized for award ribbon and trophy display

## Configuration Management

### Settings Persistence

**Individual Category Saving**  
- **Save Audio Settings**: Dedicated save button for audio badge configuration
- **Save Awards Settings**: Separate save function for awards badge settings
- **Save Resolution Settings**: Independent resolution configuration saving
- **Category Isolation**: Changes in one category don't affect others until saved

### Advanced Configuration Features

**Professional Customization**  
- **Granular Control**: Detailed configuration options for every visual aspect
- **Template System**: Reusable configuration patterns across badge types
- **Preview Integration**: Settings automatically applied to Preview module
- **Performance Optimization**: Efficient rendering with configurable performance settings

**Configuration Validation**  
- **Real-time Feedback**: Immediate validation of configuration changes
- **Error Prevention**: Smart defaults and validation prevent invalid configurations
- **Help Integration**: Contextual guidance for complex configuration options

## Integration Benefits

### Unified System Configuration

**Centralized Management**  
- **Single Interface**: All Aphrodite configuration accessible from one location
- **Consistent Structure**: Uniform configuration interface across all badge types
- **Professional Results**: Fine-tuned control ensures high-quality badge output
- **Workflow Integration**: Settings automatically apply to all processing operations

### Flexible Customization

**Adaptive Configuration**  
- **Per-Badge-Type Settings**: Independent configuration for each badge category
- **Dynamic Adjustment**: Real-time preview of configuration changes
- **Professional Standards**: Advanced options support broadcast-quality badge output
- **User Experience**: Intuitive interface balances power with ease of use

The Settings module provides the foundation for Aphrodite's professional-quality poster enhancement capabilities, offering detailed control over every aspect of badge appearance while maintaining an intuitive configuration experience.
