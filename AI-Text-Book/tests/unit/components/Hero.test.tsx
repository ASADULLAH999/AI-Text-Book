import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Hero from '../../../src/components/Hero';

describe('Hero Component', () => {
  it('should render the hero section with title', () => {
    render(<Hero />);
    expect(screen.getByText(/Master/i)).toBeInTheDocument();
    expect(screen.getByText(/Physical AI/i)).toBeInTheDocument();
  });

  it('should render subtitle text', () => {
    render(<Hero />);
    expect(screen.getByText(/Learn robotics from fundamentals/i)).toBeInTheDocument();
  });

  it('should render Start Reading button', () => {
    render(<Hero />);
    const button = screen.getByRole('button', { name: /Start Reading/i });
    expect(button).toBeInTheDocument();
  });

  it('should render View Curriculum button', () => {
    render(<Hero />);
    const button = screen.getByRole('button', { name: /View Curriculum/i });
    expect(button).toBeInTheDocument();
  });

  it('should render stats section with correct values', () => {
    render(<Hero />);
    expect(screen.getByText('156')).toBeInTheDocument();
    expect(screen.getByText('7')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('Tasks')).toBeInTheDocument();
    expect(screen.getByText('Phases')).toBeInTheDocument();
    expect(screen.getByText('Modules')).toBeInTheDocument();
  });

  it('should call onStartReading callback when Start Reading button is clicked', () => {
    const mockCallback = jest.fn();
    render(<Hero onStartReading={mockCallback} />);
    const button = screen.getByRole('button', { name: /Start Reading/i });
    fireEvent.click(button);
    expect(mockCallback).toHaveBeenCalledTimes(1);
  });

  it('should have canvas element for animations', () => {
    const { container } = render(<Hero />);
    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('should have accessible button elements', () => {
    render(<Hero />);
    const buttons = screen.getAllByRole('button');
    buttons.forEach((button) => {
      expect(button).toBeEnabled();
    });
  });

  it('should contain gradient text element', () => {
    const { container } = render(<Hero />);
    const gradientText = container.querySelector('.gradient');
    expect(gradientText).toBeInTheDocument();
  });
});
