import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { UnsavedChangesAlert } from '../components/UnsavedChangesAlert';

describe('UnsavedChangesAlert', () => {
  const mockOnCancel = jest.fn();
  const mockOnContinue = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  it('renders nothing when not open', () => {
    const { container } = render(
      <UnsavedChangesAlert
        isOpen={false}
        onCancel={mockOnCancel}
        onContinue={mockOnContinue}
      />
    );
    
    // The dialog should not be in the document
    expect(screen.queryByText('Unsaved Changes')).not.toBeInTheDocument();
    expect(container.firstChild).toBeNull();
  });
  
  it('renders correctly when open', () => {
    render(
      <UnsavedChangesAlert
        isOpen={true}
        onCancel={mockOnCancel}
        onContinue={mockOnContinue}
      />
    );
    
    // The dialog should be in the document
    expect(screen.getByText('Unsaved Changes')).toBeInTheDocument();
    expect(screen.getByText(/You have unsaved changes/)).toBeInTheDocument();
    
    // Both buttons should be rendered
    expect(screen.getByText('Save Changes')).toBeInTheDocument();
    expect(screen.getByText('Discard Changes')).toBeInTheDocument();
  });
  
  it('calls onCancel when "Save Changes" is clicked', () => {
    render(
      <UnsavedChangesAlert
        isOpen={true}
        onCancel={mockOnCancel}
        onContinue={mockOnContinue}
      />
    );
    
    // Click the "Save Changes" button
    fireEvent.click(screen.getByText('Save Changes'));
    
    // Check that onCancel was called
    expect(mockOnCancel).toHaveBeenCalledTimes(1);
    expect(mockOnContinue).not.toHaveBeenCalled();
  });
  
  it('calls onContinue when "Discard Changes" is clicked', () => {
    render(
      <UnsavedChangesAlert
        isOpen={true}
        onCancel={mockOnCancel}
        onContinue={mockOnContinue}
      />
    );
    
    // Click the "Discard Changes" button
    fireEvent.click(screen.getByText('Discard Changes'));
    
    // Check that onContinue was called
    expect(mockOnContinue).toHaveBeenCalledTimes(1);
    expect(mockOnCancel).not.toHaveBeenCalled();
  });
});
