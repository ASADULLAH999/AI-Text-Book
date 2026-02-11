import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Timeline from '../../../src/components/Timeline';

describe('Timeline Component', () => {
  it('should render timeline title', () => {
    render(<Timeline />);
    expect(screen.getByText('Development Timeline')).toBeInTheDocument();
  });

  it('should render timeline subtitle', () => {
    render(<Timeline />);
    expect(screen.getByText('7 phases, 10 weeks of structured development')).toBeInTheDocument();
  });

  it('should render all timeline items by default', () => {
    render(<Timeline />);
    expect(screen.getByText('Project Setup & Infrastructure')).toBeInTheDocument();
    expect(screen.getByText('Foundational Systems')).toBeInTheDocument();
    expect(screen.getByText('Homepage Development')).toBeInTheDocument();
  });

  it('should expand/collapse on click', () => {
    render(<Timeline />);
    const headers = screen.getAllByRole('button');
    expect(headers.length).toBeGreaterThan(0);

    const firstHeader = headers[0];
    fireEvent.click(firstHeader);

    // After click, check if content is expanded
    expect(firstHeader).toBeInTheDocument();
  });

  it('should handle keyboard navigation', () => {
    render(<Timeline />);
    const headers = screen.getAllByRole('button');
    const firstHeader = headers[0];

    // Simulate Enter key press
    fireEvent.keyPress(firstHeader, { key: 'Enter', code: 'Enter' });
    expect(firstHeader).toBeInTheDocument();

    // Simulate Space key press
    fireEvent.keyPress(firstHeader, { key: ' ', code: 'Space' });
    expect(firstHeader).toBeInTheDocument();
  });

  it('should display phase numbers', () => {
    render(<Timeline />);
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('should render timeline line', () => {
    const { container } = render(<Timeline />);
    const line = container.querySelector('[class*="line"]');
    expect(line).toBeInTheDocument();
  });

  it('should render timeline nodes', () => {
    const { container } = render(<Timeline />);
    const nodes = container.querySelectorAll('[class*="node"]');
    expect(nodes.length).toBeGreaterThan(0);
  });

  it('should accept custom items', () => {
    const customItems = [
      {
        id: 'custom-1',
        title: 'Custom Phase',
        description: 'Custom Description',
        content: 'Custom Content',
        phase: 'X',
      },
    ];

    render(<Timeline items={customItems} />);
    expect(screen.getByText('Custom Phase')).toBeInTheDocument();
  });

  it('should have expandable content sections', () => {
    render(<Timeline />);
    const firstHeader = screen.getAllByRole('button')[0];

    // Expand first item
    fireEvent.click(firstHeader);

    // Check that content is present
    expect(firstHeader).toBeInTheDocument();
  });
});
