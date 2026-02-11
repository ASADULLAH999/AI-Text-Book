import React, { useEffect, useRef, useState } from 'react';
import HomeNavbar from '../components/HomeNavbar';
import Hero from '../components/Hero';
import ModuleCards from '../components/ModuleCards';
import WhyPhysicalAI from '../components/WhyPhysicalAI';
import Timeline from '../components/Timeline';
import CurriculumGuidance from '../components/CurriculumGuidance';
import HardwareTabs from '../components/HardwareTabs';
import styles from './styles.module.css';

interface Section {
  id: string;
  title: string;
  ref?: React.RefObject<HTMLDivElement>;
}

export default function HomePage() {
  const heroRef = useRef<HTMLDivElement>(null);
  const modulesRef = useRef<HTMLDivElement>(null);
  const whyRef = useRef<HTMLDivElement>(null);
  const timelineRef = useRef<HTMLDivElement>(null);
  const curriculumRef = useRef<HTMLDivElement>(null);
  const hardwareRef = useRef<HTMLDivElement>(null);

  const [visibleSections, setVisibleSections] = useState<Set<string>>(new Set());

  const sections: Section[] = [
    { id: 'hero', title: 'Hero', ref: heroRef },
    { id: 'modules', title: 'Modules', ref: modulesRef },
    { id: 'why', title: 'Why Physical AI', ref: whyRef },
    { id: 'timeline', title: 'Timeline', ref: timelineRef },
    { id: 'curriculum', title: 'Curriculum', ref: curriculumRef },
    { id: 'hardware', title: 'Hardware', ref: hardwareRef },
  ];

  // Setup Intersection Observer for scroll-triggered animations
  useEffect(() => {
    const observerOptions = {
      threshold: 0.15,
      rootMargin: '0px 0px -100px 0px',
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setVisibleSections((prev) => new Set([...prev, entry.target.id]));
          // Only observe once per element
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    sections.forEach((section) => {
      if (section.ref?.current) {
        section.ref.current.id = section.id;
        observer.observe(section.ref.current);
      }
    });

    return () => observer.disconnect();
  }, []);

  // Handle scroll-to-section from URL hash
  useEffect(() => {
    const hash = window.location.hash.slice(1);
    if (hash) {
      const section = sections.find((s) => s.id === hash);
      if (section?.ref?.current) {
        setTimeout(() => {
          section.ref?.current?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      }
    }
  }, []);

  // Handle module click navigation
  const handleModuleClick = (moduleId: string) => {
    // Map module IDs to documentation paths
    const modulePaths: Record<string, string> = {
      'module-1': '/docs/module-1-ros2/',
      'module-2': '/docs/module-2-simulation/',
      'module-3': '/docs/module-3-isaac/',
      'module-4': '/docs/module-4-voice/',
    };

    if (modulePaths[moduleId]) {
      window.location.href = modulePaths[moduleId];
    }
  };

  // Handle hero CTA click
  const handleStartReading = () => {
    handleModuleClick('module-1');
  };

  return (
    <div className={styles.homepage}>
      <HomeNavbar />

      {/* Hero Section */}
      <div ref={heroRef} className={`${styles.section} ${visibleSections.has('hero') ? styles.visible : ''}`}>
        <Hero onStartReading={handleStartReading} />
      </div>

      {/* Modules Section */}
      <div ref={modulesRef} className={`${styles.section} ${visibleSections.has('modules') ? styles.visible : ''}`}>
        <ModuleCards onModuleClick={handleModuleClick} />
      </div>

      {/* Why Physical AI Section */}
      <div ref={whyRef} className={`${styles.section} ${visibleSections.has('why') ? styles.visible : ''}`}>
        <WhyPhysicalAI />
      </div>

      {/* Timeline Section */}
      <div ref={timelineRef} className={`${styles.section} ${visibleSections.has('timeline') ? styles.visible : ''}`}>
        <Timeline />
      </div>

      {/* Curriculum Guidance Section */}
      <div ref={curriculumRef} className={`${styles.section} ${visibleSections.has('curriculum') ? styles.visible : ''}`}>
        <CurriculumGuidance />
      </div>

      {/* Hardware Requirements Section */}
      <div ref={hardwareRef} className={`${styles.section} ${visibleSections.has('hardware') ? styles.visible : ''}`}>
        <HardwareTabs />
      </div>
    </div>
  );
}
