import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { PreviewControls } from '../components/PreviewControls';

describe('PreviewControls', () => {
  const mockToggleTheme = jest.fn();
  const mockToggleBadgeVisibility = jest.fn();
  const mockDownload = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  it('renders with light theme', () => {
    render(
      <PreviewControls
        theme="light"
        onThemeToggle={mockToggleTheme}
        visibleBadges={['audio', 'resolution', 'review']}
        onToggleBadgeVisibility={mockToggleBadgeVisibility}
      />
    );
    
    // Check title is rendered
    expect(screen.getByText('Preview Controls')).toBeInTheDocument();
    
    // Check theme toggle button (should show moon icon for light theme)
    expect(screen.getByTitle('Switch to Dark Mode')).toBeInTheDocument();
    
    // Check badge visibility toggles
    expect(screen.getByText('Audio Badge')).toBeInTheDocument();
    expect(screen.getByText('Resolution Badge')).toBeInTheDocument();
    expect(screen.getByText('Review Badge')).toBeInTheDocument();
    
    // All toggles should be on
    const switches = screen.getAllByRole('switch');
    expect(switches.length).toBe(3);
    switches.forEach(switchEl => {
      expect(switchEl).toBeChecked();
    });
    
    // Download button should not be present by default
    expect(screen.queryByText('Download Badge')).not.toBeInTheDocument();
  });
  
  it('renders with dark theme', () => {
    render(
      <PreviewControls
        theme="dark"
        onThemeToggle={mockToggleTheme}
        visibleBadges={['audio', 'resolution', 'review']}
        onToggleBadgeVisibility={mockToggleBadgeVisibility}
      />
    );
    
    // Should show sun icon for dark theme
    expect(screen.getByTitle('Switch to Light Mode')).toBeInTheDocument();
  });
  
  it('renders with partial badge visibility', () => {
    render(
      <PreviewControls
        theme="light"
        onThemeToggle={mockToggleTheme}
        visibleBadges={['audio']} // Only audio is visible
        onToggleBadgeVisibility={mockToggleBadgeVisibility}
      />
    );
    
    // Get all switches
    const switches = screen.getAllByRole('switch');
    
    // Check that only the audio switch is checked
    expect(switches[0]).toBeChecked(); // Audio
    expect(switches[1]).not.toBeChecked(); // Resolution
    expect(switches[2]).not.toBeChecked(); // Review
  });
  
  it('handles theme toggle click', () => {
    render(
      <PreviewControls
        theme="light"
        onThemeToggle={mockToggleTheme}
        visibleBadges={['audio', 'resolution', 'review']}
        onToggleBadgeVisibility={mockToggleBadgeVisibility}
      />
    );
    
    // Click the theme toggle button
    fireEvent.click(screen.getByTitle('Switch to Dark Mode'));
    
    // Check that the theme toggle function was called
    expect(mockToggleTheme).toHaveBeenCalledTimes(1);
  });
  
  it('handles badge visibility toggle clicks', () => {
    render(
      <PreviewControls
        theme="light"
        onThemeToggle={mockToggleTheme}
        visibleBadges={['audio', 'resolution', 'review']}
        onToggleBadgeVisibility={mockToggleBadgeVisibility}
      />
    );
    
    // Click the audio badge toggle
    fireEvent.click(screen.getByLabelText('Audio Badge'));
    
    // Check that the toggle function was called with 'audio'
    expect(mockToggleBadgeVisibility).toHaveBeenCalledWith('audio');
    
    // Click the resolution badge toggle
    fireEvent.click(screen.getByLabelText('Resolution Badge'));
    
    // Check that the toggle function was called with 'resolution'
    expect(mockToggleBadgeVisibility).toHaveBeenCalledWith('resolution');
    
    // Click the review badge toggle
    fireEvent.click(screen.getByLabelText('Review Badge'));
    
    // Check that the toggle function was called with 'review'
    expect(mockToggleBadgeVisibility).toHaveBeenCalledWith('review');
  });
  
  it('renders and handles download button when provided', () => {
    render(
      <PreviewControls
        theme="light"
        onThemeToggle={mockToggleTheme}
        visibleBadges={['audio', 'resolution', 'review']}
        onToggleBadgeVisibility={mockToggleBadgeVisibility}
        onDownload={mockDownload}
      />
    );
    
    // Download button should be present
    const downloadButton = screen.getByText('Download Badge');
    expect(downloadButton).toBeInTheDocument();
    
    // Click the download button
    fireEvent.click(downloadButton);
    
    // Check that the download function was called
    expect(mockDownload).toHaveBeenCalledTimes(1);
  });
  
  it('disables download button when no badges are visible', () => {
    render(
      <PreviewControls
        theme="light"
        onThemeToggle={mockToggleTheme}
        visibleBadges={[]} // No visible badges
        onToggleBadgeVisibility={mockToggleBadgeVisibility}
        onDownload={mockDownload}
      />
    );
    
    // Download button should be disabled
    const downloadButton = screen.getByText('Download Badge');
    expect(downloadButton).toBeDisabled();
  });
});
