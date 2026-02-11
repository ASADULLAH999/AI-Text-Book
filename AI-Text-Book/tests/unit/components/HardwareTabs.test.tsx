import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import HardwareTabs from '../../../src/components/HardwareTabs';

describe('HardwareTabs Component', () => {
  it('should render section title', () => {
    render(<HardwareTabs />);
    expect(screen.getByText('Hardware Requirements')).toBeInTheDocument();
  });

  it('should render section subtitle', () => {
    render(<HardwareTabs />);
    expect(screen.getByText('Choose the setup that fits your learning path')).toBeInTheDocument();
  });

  it('should render all hardware tabs', () => {
    render(<HardwareTabs />);
    expect(screen.getByRole('button', { name: /Workstation/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Edge Kit/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Robot Lab/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Cloud Option/i })).toBeInTheDocument();
  });

  it('should display workstation content by default', () => {
    render(<HardwareTabs />);
    expect(screen.getByText('Development Workstation')).toBeInTheDocument();
  });

  it('should switch to Edge Kit tab when clicked', () => {
    render(<HardwareTabs />);
    const edgeKitTab = screen.getByRole('button', { name: /Edge Kit/i });
    fireEvent.click(edgeKitTab);

    expect(screen.getByText('Jetson Edge AI Kit')).toBeInTheDocument();
  });

  it('should switch to Robot Lab tab when clicked', () => {
    render(<HardwareTabs />);
    const robotLabTab = screen.getByRole('button', { name: /Robot Lab/i });
    fireEvent.click(robotLabTab);

    expect(screen.getByText('Humanoid Robot Lab')).toBeInTheDocument();
  });

  it('should switch to Cloud Option tab when clicked', () => {
    render(<HardwareTabs />);
    const cloudTab = screen.getByRole('button', { name: /Cloud Option/i });
    fireEvent.click(cloudTab);

    expect(screen.getByText('AWS EC2 + RoboMaker')).toBeInTheDocument();
  });

  it('should display pricing information', () => {
    render(<HardwareTabs />);
    expect(screen.getByText(/\$1500 - \$3000/)).toBeInTheDocument();
  });

  it('should display hardware specifications in table', () => {
    render(<HardwareTabs />);
    expect(screen.getByText('CPU')).toBeInTheDocument();
    expect(screen.getByText('RAM')).toBeInTheDocument();
    expect(screen.getByText('GPU')).toBeInTheDocument();
  });

  it('should display pros and cons for Robot Lab', () => {
    render(<HardwareTabs />);
    const robotLabTab = screen.getByRole('button', { name: /Robot Lab/i });
    fireEvent.click(robotLabTab);

    expect(screen.getByText(/Real-world robotics experience/i)).toBeInTheDocument();
    expect(screen.getByText(/Significant investment required/i)).toBeInTheDocument();
  });

  it('should display cloud option advantages', () => {
    render(<HardwareTabs />);
    const cloudTab = screen.getByRole('button', { name: /Cloud Option/i });
    fireEvent.click(cloudTab);

    expect(screen.getByText(/No hardware to purchase/i)).toBeInTheDocument();
    expect(screen.getByText(/Scalable resources/i)).toBeInTheDocument();
  });

  it('should have accessible tab navigation', () => {
    render(<HardwareTabs />);
    const tabs = screen.getAllByRole('button');

    tabs.forEach((tab) => {
      expect(tab).toBeEnabled();
    });
  });
});
