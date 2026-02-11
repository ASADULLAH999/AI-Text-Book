import React from 'react';
import { render, screen } from '@testing-library/react';
import WhyPhysicalAI from '../../../src/components/WhyPhysicalAI';

describe('WhyPhysicalAI Component', () => {
  it('should render section title', () => {
    render(<WhyPhysicalAI />);
    expect(screen.getByText('Why Physical AI Matters')).toBeInTheDocument();
  });

  it('should render section subtitle', () => {
    render(<WhyPhysicalAI />);
    expect(screen.getByText(/AI systems need to understand and interact/i)).toBeInTheDocument();
  });

  it('should render all default key points', () => {
    render(<WhyPhysicalAI />);
    expect(screen.getByText('Embodied Intelligence')).toBeInTheDocument();
    expect(screen.getByText('Human-Robot Interaction')).toBeInTheDocument();
    expect(screen.getByText('Sim-to-Real Transfer')).toBeInTheDocument();
  });

  it('should render key point descriptions', () => {
    render(<WhyPhysicalAI />);
    expect(screen.getByText(/Learn how physical systems interact/i)).toBeInTheDocument();
    expect(screen.getByText(/Master the principles of safe/i)).toBeInTheDocument();
  });

  it('should render key point icons', () => {
    const { container } = render(<WhyPhysicalAI />);
    const icons = container.querySelectorAll('[class*="iconBox"]');
    expect(icons.length).toBeGreaterThan(0);
  });

  it('should render CTA button', () => {
    render(<WhyPhysicalAI />);
    expect(screen.getByRole('button', { name: /Learn More About Physical AI/i })).toBeInTheDocument();
  });

  it('should have SVG robot illustration', () => {
    const { container } = render(<WhyPhysicalAI />);
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('should have robot elements in SVG', () => {
    const { container } = render(<WhyPhysicalAI />);
    const robotElements = container.querySelectorAll('[class*="robot"]');
    expect(robotElements.length).toBeGreaterThan(0);
  });

  it('should have neural network elements in SVG', () => {
    const { container } = render(<WhyPhysicalAI />);
    const neuralElements = container.querySelectorAll('[class*="neuralNet"]');
    expect(neuralElements.length).toBeGreaterThan(0);
  });

  it('should accept custom key points', () => {
    const customPoints = [
      {
        icon: '⚙️',
        title: 'Custom Point',
        description: 'Custom Description',
      },
    ];

    render(<WhyPhysicalAI keyPoints={customPoints} />);
    expect(screen.getByText('Custom Point')).toBeInTheDocument();
  });

  it('should render text column with content', () => {
    const { container } = render(<WhyPhysicalAI />);
    const textColumn = container.querySelector('[class*="textColumn"]');
    expect(textColumn).toBeInTheDocument();
  });

  it('should render visual column with illustration', () => {
    const { container } = render(<WhyPhysicalAI />);
    const visualColumn = container.querySelector('[class*="visualColumn"]');
    expect(visualColumn).toBeInTheDocument();
  });

  it('should have accessible CTA button', () => {
    render(<WhyPhysicalAI />);
    const button = screen.getByRole('button', { name: /Learn More/i });
    expect(button).toBeEnabled();
  });
});
