import React from 'react';
import { render, screen } from '@testing-library/react';
import Badge from '../../../src/components/badges/Badge';
import { describe, it, expect } from 'vitest';

describe('Badge Component', () => {
  it('renders without errors', () => {
    render(<Badge />);
    const badgeElement = screen.getByRole('img');
    expect(badgeElement).toBeInTheDocument();
  });
});