import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import CurriculumGuidance from '../../../src/components/CurriculumGuidance';

describe('CurriculumGuidance Component', () => {
  it('should render section title', () => {
    render(<CurriculumGuidance />);
    expect(screen.getByText('Curriculum Guidance')).toBeInTheDocument();
  });

  it('should render section subtitle', () => {
    render(<CurriculumGuidance />);
    expect(screen.getByText('What you\'ll learn and how you\'ll be assessed')).toBeInTheDocument();
  });

  it('should render all tab buttons', () => {
    render(<CurriculumGuidance />);
    expect(screen.getByRole('button', { name: /Learning Outcomes/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Assessments/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Prerequisites/i })).toBeInTheDocument();
  });

  it('should display learning outcomes by default', () => {
    render(<CurriculumGuidance />);
    expect(screen.getByText(/Understand ROS 2 architecture/i)).toBeInTheDocument();
  });

  it('should switch to assessments tab when clicked', () => {
    render(<CurriculumGuidance />);
    const assessmentsTab = screen.getByRole('button', { name: /Assessments/i });
    fireEvent.click(assessmentsTab);

    expect(screen.getByText(/Module Quizzes/i)).toBeInTheDocument();
  });

  it('should switch to prerequisites tab when clicked', () => {
    render(<CurriculumGuidance />);
    const prerequisitesTab = screen.getByRole('button', { name: /Prerequisites/i });
    fireEvent.click(prerequisitesTab);

    expect(screen.getByText(/Basic Python programming knowledge/i)).toBeInTheDocument();
  });

  it('should display assessment percentages', () => {
    render(<CurriculumGuidance />);
    const assessmentsTab = screen.getByRole('button', { name: /Assessments/i });
    fireEvent.click(assessmentsTab);

    expect(screen.getByText('30%')).toBeInTheDocument();
    expect(screen.getByText('40%')).toBeInTheDocument();
  });

  it('should accept custom learning outcomes', () => {
    const customOutcomes = ['Custom Outcome 1', 'Custom Outcome 2'];
    render(<CurriculumGuidance learningOutcomes={customOutcomes} />);

    expect(screen.getByText('Custom Outcome 1')).toBeInTheDocument();
    expect(screen.getByText('Custom Outcome 2')).toBeInTheDocument();
  });

  it('should accept custom assessments', () => {
    const customAssessments = [
      { name: 'Custom Assessment', percentage: 50 },
    ];
    render(<CurriculumGuidance assessments={customAssessments} />);

    const assessmentsTab = screen.getByRole('button', { name: /Assessments/i });
    fireEvent.click(assessmentsTab);

    expect(screen.getByText(/Custom Assessment/i)).toBeInTheDocument();
  });

  it('should accept custom prerequisites', () => {
    const customPrereqs = ['Custom Prerequisite'];
    render(<CurriculumGuidance prerequisites={customPrereqs} />);

    const prerequisitesTab = screen.getByRole('button', { name: /Prerequisites/i });
    fireEvent.click(prerequisitesTab);

    expect(screen.getByText('Custom Prerequisite')).toBeInTheDocument();
  });

  it('should have accessible tab navigation', () => {
    render(<CurriculumGuidance />);
    const tabs = screen.getAllByRole('button');

    tabs.forEach((tab) => {
      expect(tab).toBeEnabled();
    });
  });
});
