import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BadgeSettingsPanel } from '../components/BadgeSettingsPanel';
import { 
  AudioBadgeSettings, 
  ResolutionBadgeSettings, 
  ReviewBadgeSettings,
  BadgePosition,
  DisplayFormat, 
  DEFAULT_AUDIO_BADGE_SETTINGS,
  DEFAULT_RESOLUTION_BADGE_SETTINGS,
  DEFAULT_REVIEW_BADGE_SETTINGS
} from '@/types/unifiedBadgeSettings';

// Mock the badge control components to simplify testing
jest.mock('@/components/badges/unified', () => ({
  AudioBadgeControls: () => <div data-testid="audio-badge-controls">Audio Badge Controls</div>,
  ResolutionBadgeControls: () => <div data-testid="resolution-badge-controls">Resolution Badge Controls</div>,
  ReviewBadgeControls: () => <div data-testid="review-badge-controls">Review Badge Controls</div>,
}));

describe('BadgeSettingsPanel', () => {
  const mockAudioBadge = { ...DEFAULT_AUDIO_BADGE_SETTINGS, user_id: '1' };
  const mockResolutionBadge = { ...DEFAULT_RESOLUTION_BADGE_SETTINGS, user_id: '1' };
  const mockReviewBadge = { ...DEFAULT_REVIEW_BADGE_SETTINGS, user_id: '1' };
  
  const mockOnAudioBadgeChange = jest.fn();
  const mockOnResolutionBadgeChange = jest.fn();
  const mockOnReviewBadgeChange = jest.fn();
  const mockOnTabChange = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  it('renders the component with the correct tabs', () => {
    render(
      <BadgeSettingsPanel
        audioBadge={mockAudioBadge}
        resolutionBadge={mockResolutionBadge}
        reviewBadge={mockReviewBadge}
        onAudioBadgeChange={mockOnAudioBadgeChange}
        onResolutionBadgeChange={mockOnResolutionBadgeChange}
        onReviewBadgeChange={mockOnReviewBadgeChange}
      />
    );
    
    // Check that the component renders with the expected title
    expect(screen.getByText('Badge Settings')).toBeInTheDocument();
    
    // Check that all the tabs are rendered
    expect(screen.getByText('Audio')).toBeInTheDocument();
    expect(screen.getByText('Resolution')).toBeInTheDocument();
    expect(screen.getByText('Review')).toBeInTheDocument();
    
    // Check that the audio tab is active by default and shows audio controls
    expect(screen.getByTestId('audio-badge-controls')).toBeInTheDocument();
  });
  
  it('changes tabs correctly when clicked', () => {
    render(
      <BadgeSettingsPanel
        audioBadge={mockAudioBadge}
        resolutionBadge={mockResolutionBadge}
        reviewBadge={mockReviewBadge}
        onAudioBadgeChange={mockOnAudioBadgeChange}
        onResolutionBadgeChange={mockOnResolutionBadgeChange}
        onReviewBadgeChange={mockOnReviewBadgeChange}
        onTabChange={mockOnTabChange}
      />
    );
    
    // Click the Resolution tab
    fireEvent.click(screen.getByText('Resolution'));
    
    // Check that the resolution controls are shown
    expect(screen.getByTestId('resolution-badge-controls')).toBeInTheDocument();
    expect(mockOnTabChange).toHaveBeenCalledWith('resolution');
    
    // Click the Review tab
    fireEvent.click(screen.getByText('Review'));
    
    // Check that the review controls are shown
    expect(screen.getByTestId('review-badge-controls')).toBeInTheDocument();
    expect(mockOnTabChange).toHaveBeenCalledWith('review');
  });
  
  it('renders with a specified active tab', () => {
    render(
      <BadgeSettingsPanel
        audioBadge={mockAudioBadge}
        resolutionBadge={mockResolutionBadge}
        reviewBadge={mockReviewBadge}
        onAudioBadgeChange={mockOnAudioBadgeChange}
        onResolutionBadgeChange={mockOnResolutionBadgeChange}
        onReviewBadgeChange={mockOnReviewBadgeChange}
        activeTab="review"
      />
    );
    
    // Check that the review tab is active
    expect(screen.getByTestId('review-badge-controls')).toBeInTheDocument();
  });
  
  it('handles null badge settings gracefully', () => {
    render(
      <BadgeSettingsPanel
        audioBadge={null}
        resolutionBadge={null}
        reviewBadge={null}
        onAudioBadgeChange={mockOnAudioBadgeChange}
        onResolutionBadgeChange={mockOnResolutionBadgeChange}
        onReviewBadgeChange={mockOnReviewBadgeChange}
      />
    );
    
    // The component should render without errors
    expect(screen.getByText('Badge Settings')).toBeInTheDocument();
    
    // No controls should be visible since all badge settings are null
    expect(screen.queryByTestId('audio-badge-controls')).not.toBeInTheDocument();
    expect(screen.queryByTestId('resolution-badge-controls')).not.toBeInTheDocument();
    expect(screen.queryByTestId('review-badge-controls')).not.toBeInTheDocument();
  });
});
