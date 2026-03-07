import React, { useEffect, useRef } from 'react';
import { useHistory } from '@docusaurus/router';
import styles from './styles.module.css';

interface HeroProps {
  onStartReading?: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onStartReading }) => {
  const history = useHistory();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const orbsRef = useRef<Orb[]>([]);
  const animationFrameRef = useRef<number>();

  interface Particle {
    x: number;
    y: number;
    vx: number;
    vy: number;
    size: number;
    opacity: number;
    life: number;
    maxLife: number;
  }

  interface Orb {
    x: number;
    y: number;
    radius: number;
    color: string;
    opacity: number;
    vx: number;
    vy: number;
    targetX: number;
    targetY: number;
  }

  // Initialize particles
  const createParticle = (x: number, y: number): Particle => {
    const angle = Math.random() * Math.PI * 2;
    const velocity = 1 + Math.random() * 2;
    return {
      x,
      y,
      vx: Math.cos(angle) * velocity,
      vy: Math.sin(angle) * velocity,
      size: 1 + Math.random() * 2,
      opacity: 1,
      life: 0,
      maxLife: 60 + Math.random() * 60,
    };
  };

  // Initialize orbs
  const createOrb = (): Orb => {
    const isCyan = Math.random() > 0.5;
    const canvas = canvasRef.current;
    if (!canvas) return {} as Orb;

    return {
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      radius: 30 + Math.random() * 50,
      color: isCyan ? 'rgba(34, 211, 238, ' : 'rgba(251, 146, 60, ',
      opacity: 0.1 + Math.random() * 0.2,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      targetX: Math.random() * (canvas?.width || 800),
      targetY: Math.random() * (canvas?.height || 600),
    };
  };

  // Animate canvas with neural grid, particles, and orbs
  const animate = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.fillStyle = 'rgba(15, 23, 42, 0.5)';
    ctx.fillRect(0, 0, width, height);

    // Draw neural grid
    const gridSize = 50;
    ctx.strokeStyle = 'rgba(34, 211, 238, 0.15)';
    ctx.lineWidth = 1;

    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }

    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Animate orbs
    orbsRef.current.forEach((orb) => {
      const dx = orb.targetX - orb.x;
      const dy = orb.targetY - orb.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < 50) {
        orb.targetX = Math.random() * width;
        orb.targetY = Math.random() * height;
      }

      orb.vx += dx * 0.001;
      orb.vy += dy * 0.001;
      orb.x += orb.vx;
      orb.y += orb.vy;

      // Draw gradient circle for orb
      const gradient = ctx.createRadialGradient(orb.x, orb.y, 0, orb.x, orb.y, orb.radius);
      gradient.addColorStop(0, orb.color + orb.opacity + ')');
      gradient.addColorStop(1, orb.color + '0)');

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(orb.x, orb.y, orb.radius, 0, Math.PI * 2);
      ctx.fill();
    });

    // Draw and animate particles
    particlesRef.current = particlesRef.current.filter((p) => p.life < p.maxLife);
    particlesRef.current.forEach((p) => {
      p.x += p.vx;
      p.y += p.vy;
      p.life++;
      p.opacity = 1 - p.life / p.maxLife;
      p.vy += 0.1; // gravity

      ctx.fillStyle = `rgba(34, 211, 238, ${p.opacity})`;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    });

    // Randomly create new particles
    if (Math.random() < 0.3) {
      const angle = Math.random() * Math.PI * 2;
      const distance = 150;
      const centerX = width / 2;
      const centerY = height / 2;
      const x = centerX + Math.cos(angle) * distance;
      const y = centerY + Math.sin(angle) * distance;
      particlesRef.current.push(createParticle(x, y));
    }

    animationFrameRef.current = requestAnimationFrame(animate);
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Set canvas size
    const updateCanvasSize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };

    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);

    // Initialize orbs
    orbsRef.current = Array.from({ length: 3 }, () => createOrb());

    // Start animation
    animate();

    return () => {
      window.removeEventListener('resize', updateCanvasSize);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return (
    <section className={styles.hero}>
      <canvas ref={canvasRef} className={styles.canvas} />

      <div className={styles.content}>
        <div className={styles.textContainer}>
          <h1 className={styles.title}>
            Master <span className={styles.gradient}>Physical AI</span>
            <br /> & Humanoid Robotics
          </h1>

          <p className={styles.subtitle}>
            Learn robotics from fundamentals to advanced capstone projects. Hands-on labs with ROS 2, Gazebo, NVIDIA Isaac
            Sim, and real humanoid robots.
          </p>

          <div className={styles.buttons}>
            <button
              className={`${styles.btn} ${styles.btnPrimary} ${styles.btnLarge}`}
              onClick={() => {
                // AUTHENTICATION DISABLED - Direct access to content
                history.push('/docs/module-1-ros2/');

                // Still call the original callback if provided
                if (onStartReading) {
                  onStartReading();
                }
              }}
            >
              <span className={styles.btnText}>Start Reading</span>
              <svg className={styles.btnIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M13 7l5 5m0 0l-5 5m5-5H6" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span className={styles.btnShine}></span>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
