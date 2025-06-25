"""
Badge Positioning

Pure V2 badge positioning and layout utilities.
"""

from typing import Tuple, Dict, Any
from aphrodite_logging import get_logger


class BadgePositioning:
    """Pure V2 badge positioning utilities"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.positioning", service="badge")
    
    def calculate_dynamic_padding(self, poster_width: int, poster_height: int, base_padding: int) -> int:
        """Calculate dynamic padding based on poster aspect ratio"""
        try:
            # Get poster aspect ratio
            aspect_ratio = poster_width / poster_height
            
            # Standard poster aspect ratio is around 0.67 (2:3)
            # Adjust padding based on how far we are from standard
            if aspect_ratio > 0.8:  # Wide poster
                padding_multiplier = 1.2
            elif aspect_ratio < 0.6:  # Narrow poster
                padding_multiplier = 0.8
            else:  # Standard poster
                padding_multiplier = 1.0
            
            dynamic_padding = int(base_padding * padding_multiplier)
            
            # Ensure minimum and maximum padding
            dynamic_padding = max(15, min(dynamic_padding, 60))
            
            self.logger.debug(f"Dynamic padding: {dynamic_padding} (aspect: {aspect_ratio:.2f}, base: {base_padding})")
            return dynamic_padding
            
        except Exception as e:
            self.logger.error(f"Error calculating dynamic padding: {e}")
            return base_padding
    
    def calculate_badge_position(
        self, 
        poster_size: Tuple[int, int], 
        badge_size: Tuple[int, int], 
        position: str,
        edge_padding: int
    ) -> Tuple[int, int]:
        """Calculate badge position coordinates"""
        try:
            poster_width, poster_height = poster_size
            badge_width, badge_height = badge_size
            
            # Calculate position based on string
            if position == 'top-left':
                x = edge_padding
                y = edge_padding
            elif position == 'top-right':
                x = poster_width - badge_width - edge_padding
                y = edge_padding
            elif position == 'bottom-left':
                x = edge_padding
                y = poster_height - badge_height - edge_padding
            elif position == 'bottom-right':
                x = poster_width - badge_width - edge_padding
                y = poster_height - badge_height - edge_padding
            elif position == 'top-center':
                x = (poster_width - badge_width) // 2
                y = edge_padding
            elif position == 'center-left':
                x = edge_padding
                y = (poster_height - badge_height) // 2
            elif position == 'center':
                x = (poster_width - badge_width) // 2
                y = (poster_height - badge_height) // 2
            elif position == 'center-right':
                x = poster_width - badge_width - edge_padding
                y = (poster_height - badge_height) // 2
            elif position == 'bottom-center':
                x = (poster_width - badge_width) // 2
                y = poster_height - badge_height - edge_padding
            elif position == 'bottom-right-flush':
                x = poster_width - badge_width
                y = poster_height - badge_height
            else:
                # Default to top-right
                self.logger.warning(f"Unknown position '{position}', using top-right")
                x = poster_width - badge_width - edge_padding
                y = edge_padding
            
            # Ensure coordinates are within bounds
            x = max(0, min(x, poster_width - badge_width))
            y = max(0, min(y, poster_height - badge_height))
            
            self.logger.debug(f"Badge position: ({x}, {y}) for {position}")
            return (x, y)
            
        except Exception as e:
            self.logger.error(f"Error calculating badge position: {e}")
            # Return safe default position
            return (edge_padding, edge_padding)
    
    def calculate_multi_badge_layout(
        self, 
        poster_size: Tuple[int, int],
        badge_sizes: list[Tuple[int, int]],
        settings: Dict[str, Any]
    ) -> list[Tuple[int, int]]:
        """Calculate positions for multiple badges"""
        try:
            poster_width, poster_height = poster_size
            positions = []
            
            # Get layout settings
            position = settings.get('General', {}).get('general_badge_position', 'bottom-left')
            edge_padding = settings.get('General', {}).get('general_edge_padding', 30)
            badge_spacing = settings.get('General', {}).get('badge_spacing', 15)
            orientation = settings.get('General', {}).get('badge_orientation', 'vertical')
            
            # Calculate dynamic padding
            edge_padding = self.calculate_dynamic_padding(poster_width, poster_height, edge_padding)
            
            if orientation == 'horizontal':
                # Arrange badges horizontally
                total_width = sum(size[0] for size in badge_sizes) + badge_spacing * (len(badge_sizes) - 1)
                
                # Start position based on desired position
                if 'right' in position:
                    start_x = poster_width - total_width - edge_padding
                elif 'center' in position:
                    start_x = (poster_width - total_width) // 2
                else:  # left
                    start_x = edge_padding
                
                if 'bottom' in position:
                    y = poster_height - max(size[1] for size in badge_sizes) - edge_padding
                elif 'center' in position and 'top' not in position and 'bottom' not in position:
                    y = (poster_height - max(size[1] for size in badge_sizes)) // 2
                else:  # top
                    y = edge_padding
                
                # Place badges horizontally
                current_x = start_x
                for badge_size in badge_sizes:
                    positions.append((current_x, y))
                    current_x += badge_size[0] + badge_spacing
            
            else:  # vertical (default)
                # Arrange badges vertically
                total_height = sum(size[1] for size in badge_sizes) + badge_spacing * (len(badge_sizes) - 1)
                
                # Start position based on desired position
                if 'bottom' in position:
                    start_y = poster_height - total_height - edge_padding
                elif 'center' in position:
                    start_y = (poster_height - total_height) // 2
                else:  # top
                    start_y = edge_padding
                
                if 'right' in position:
                    x = poster_width - max(size[0] for size in badge_sizes) - edge_padding
                elif 'center' in position and 'left' not in position and 'right' not in position:
                    x = (poster_width - max(size[0] for size in badge_sizes)) // 2
                else:  # left
                    x = edge_padding
                
                # Place badges vertically
                current_y = start_y
                for badge_size in badge_sizes:
                    positions.append((x, current_y))
                    current_y += badge_size[1] + badge_spacing
            
            self.logger.debug(f"Multi-badge layout: {len(positions)} badges in {orientation} orientation")
            return positions
            
        except Exception as e:
            self.logger.error(f"Error calculating multi-badge layout: {e}")
            # Return safe default positions
            return [(30, 30 + i * 50) for i in range(len(badge_sizes))]
