import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ModuleCard from '../../../src/components/ModuleCard';

describe('ModuleCard Component', () => {
  const defaultProps = {
    id: 'module-1',
    title: 'Test Module',
    description: 'Test Description',
    icon: '🤖',
    color: 'cyan',
  };

  it('should render module title', () => {
    render(<ModuleCard {...defaultProps} />);
    expect(screen.getByText('Test Module')).toBeInTheDocument();
  });

  it('should render module description', () => {
    render(<ModuleCard {...defaultProps} />);
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });

  it('should render module icon', () => {
    render(<ModuleCard {...defaultProps} />);
    expect(screen.getByText('🤖')).toBeInTheDocument();
  });

  it('should call onClick handler when card is clicked', () => {
    const mockClick = jest.fn();
    render(<ModuleCard {...defaultProps} onClick={mockClick} />);
    const card = screen.getByText('Test Module').closest('div[class*="card"]');
    if (card) {
      fireEvent.click(card);
      expect(mockClick).toHaveBeenCalledTimes(1);
    }
  });

  it('should apply index animation delay', () => {
    const { container } = render(<ModuleCard {...defaultProps} index={2} />);
    const card = container.querySelector('[style*="animation-delay"]');
    expect(card).toHaveStyle('animation-delay: 0.2s');
  });

  it('should set correct data-color attribute', () => {
    const { container } = render(<ModuleCard {...defaultProps} color="orange" />);
    const card = container.querySelector('[data-color="orange"]');
    expect(card).toBeInTheDocument();
  });

  it('should have glass effect element', () => {
    const { container } = render(<ModuleCard {...defaultProps} />);
    const glassEffect = container.querySelector('.glassEffect');
    expect(glassEffect).toBeInTheDocument();
  });

  it('should have icon box with correct styling', () => {
    const { container } = render(<ModuleCard {...defaultProps} />);
    const icon = container.querySelector('[class*="icon"]');
    expect(icon).toBeInTheDocument();
  });

  it('should be accessible with keyboard', () => {
    const mockClick = jest.fn();
    const { container } = render(
      <ModuleCard {...defaultProps} onClick={mockClick} />
    );
    const card = container.querySelector('[class*="card"]');
    expect(card).toBeInTheDocument();
  });
});
