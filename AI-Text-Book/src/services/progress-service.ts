import { ModuleProgress, UserProgress, SectionProgress } from '../types/progress';
import { storageService } from './storage-service';

/**
 * ProgressService - Manages reading progress tracking
 * MVP: Scroll + 30s timer threshold per section
 */
class ProgressService {
  private storage = storageService;
  private readonly PROGRESS_KEY_PREFIX = 'ai_textbook_progress';
  private readonly MIN_READ_TIME = 30000; // 30 seconds
  private readonly MIN_SCROLL_PERCENTAGE = 1.0; // 100%
  private sectionTimers: Map<string, number> = new Map();
  private sectionStartTimes: Map<string, number> = new Map();

  constructor() {
    // Use the singleton storageService instance
  }

  /**
   * Track section visibility using IntersectionObserver
   */
  trackSectionVisibility(
    section_id: string,
    element: HTMLElement,
    callback: (progress: number) => void
  ): IntersectionObserver {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // Section became visible
            if (!this.sectionStartTimes.has(section_id)) {
              this.sectionStartTimes.set(section_id, Date.now());
            }

            // Start timer for this section
            const timer = window.setInterval(() => {
              const timeSpent = this.getSectionTimeSpent(section_id);
              const scrollPercentage = this.getScrollPercentage(element);
              const progress = this.calculateSectionProgress(timeSpent, scrollPercentage);
              callback(progress);
            }, 1000); // Update every second

            this.sectionTimers.set(section_id, timer);
          } else {
            // Section became invisible
            this.clearSectionTimer(section_id);
          }
        });
      },
      {
        threshold: [0, 0.25, 0.5, 0.75, 1.0],
        rootMargin: '0px',
      }
    );

    observer.observe(element);
    return observer;
  }

  /**
   * Calculate reading progress percentage
   * Threshold: 30s continuous visibility + scroll depth
   */
  calculateProgressPercentage(sections: SectionProgress[]): number {
    if (sections.length === 0) return 0;

    const completed = sections.filter((s) => s.status === 'completed').length;
    return Math.round((completed / sections.length) * 100);
  }

  /**
   * Mark section as read after 30s visibility + 100% scroll
   */
  markSectionAsRead(
    section_id: string,
    time_spent: number,
    scroll_percentage: number
  ): boolean {
    return time_spent >= this.MIN_READ_TIME && scroll_percentage >= this.MIN_SCROLL_PERCENTAGE;
  }

  /**
   * Update module progress
   */
  async updateModuleProgress(
    user_id: string,
    module_id: string,
    progress: ModuleProgress
  ): Promise<void> {
    try {
      const userProgress = await this.getUserProgress(user_id);

      // Update module
      userProgress.modules[module_id] = {
        ...progress,
        last_visited: Date.now(),
      };

      // Recalculate overall progress
      userProgress.overall_progress_percentage = this.calculateOverallProgress(
        userProgress.modules
      );
      userProgress.last_updated = Date.now();

      await this.persistProgress(user_id, userProgress);
    } catch (error) {
      console.error('Failed to update module progress:', error);
      throw error;
    }
  }

  /**
   * Update section progress within a module
   */
  async updateSectionProgress(
    user_id: string,
    module_id: string,
    section: SectionProgress
  ): Promise<void> {
    try {
      const userProgress = await this.getUserProgress(user_id);

      // Get or create module progress
      const moduleProgress: ModuleProgress = userProgress.modules[module_id] || {
        module_id,
        status: 'not_started',
        sections: [],
        overall_percentage: 0,
        last_visited: Date.now(),
        quiz_attempts: [],
      };

      // Find and update section
      const sectionIndex = moduleProgress.sections.findIndex((s) => s.section_id === section.section_id);
      if (sectionIndex >= 0) {
        moduleProgress.sections[sectionIndex] = section;
      } else {
        moduleProgress.sections.push(section);
      }

      // Update module status
      moduleProgress.overall_percentage = this.calculateProgressPercentage(moduleProgress.sections);
      moduleProgress.status = this.getModuleStatus(moduleProgress.sections);

      await this.updateModuleProgress(user_id, module_id, moduleProgress);
    } catch (error) {
      console.error('Failed to update section progress:', error);
      throw error;
    }
  }

  /**
   * Get user progress
   */
  async getUserProgress(user_id: string): Promise<UserProgress> {
    try {
      const key = `${this.PROGRESS_KEY_PREFIX}_${user_id}`;
      const stored = this.storage.get<UserProgress>(key, undefined);

      if (stored) {
        return stored;
      }

      // Return empty progress for new user
      return {
        user_id,
        modules: {},
        total_reading_time: 0,
        total_quiz_attempts: 0,
        overall_progress_percentage: 0,
        last_updated: Date.now(),
      };
    } catch (error) {
      console.error('Failed to get user progress:', error);
      throw error;
    }
  }

  /**
   * Calculate overall reading progress percentage
   */
  calculateOverallProgress(modules: Record<string, ModuleProgress>): number {
    const moduleIds = Object.keys(modules);
    if (moduleIds.length === 0) return 0;

    const totalProgress = moduleIds.reduce((sum, moduleId) => {
      return sum + modules[moduleId].overall_percentage;
    }, 0);

    return Math.round(totalProgress / moduleIds.length);
  }

  /**
   * Get "Continue Reading" data (last visited section)
   */
  getContinueReadingData(user_id: string): { module_id: string; section_id: string } | null {
    try {
      const key = `${this.PROGRESS_KEY_PREFIX}_${user_id}`;
      const progress = this.storage.get<UserProgress>(key, undefined);

      if (!progress || Object.keys(progress.modules).length === 0) {
        return null;
      }

      // Find most recently visited module
      let lastModule: ModuleProgress | null = null;
      let lastModuleId = '';

      Object.entries(progress.modules).forEach(([moduleId, module]) => {
        if (!lastModule || module.last_visited > lastModule.last_visited) {
          lastModule = module;
          lastModuleId = moduleId;
        }
      });

      if (!lastModule) {
        return null;
      }

      // Type guard: ensure lastModule is ModuleProgress
      const module = lastModule as ModuleProgress;

      if (!module.sections || module.sections.length === 0) {
        return null;
      }

      // Find first incomplete section or last visited section
      const incompleteSection = module.sections.find((s: SectionProgress) => s.status !== 'completed');
      if (incompleteSection) {
        return {
          module_id: lastModuleId,
          section_id: incompleteSection.section_id,
        };
      }

      // All sections complete, return last section
      const lastSection = module.sections[module.sections.length - 1];
      return {
        module_id: lastModuleId,
        section_id: lastSection.section_id,
      };
    } catch (error) {
      console.error('Failed to get continue reading data:', error);
      return null;
    }
  }

  /**
   * Get section time spent
   */
  private getSectionTimeSpent(section_id: string): number {
    const startTime = this.sectionStartTimes.get(section_id);
    if (!startTime) return 0;
    return Date.now() - startTime;
  }

  /**
   * Calculate scroll percentage for an element
   */
  private getScrollPercentage(element: HTMLElement): number {
    const rect = element.getBoundingClientRect();
    const windowHeight = window.innerHeight;
    const elementHeight = rect.height;

    // Element fully visible
    if (rect.top >= 0 && rect.bottom <= windowHeight) {
      return 1.0;
    }

    // Element partially visible
    const visibleHeight = Math.min(rect.bottom, windowHeight) - Math.max(rect.top, 0);
    return Math.max(0, Math.min(1, visibleHeight / elementHeight));
  }

  /**
   * Calculate section progress based on time and scroll
   */
  private calculateSectionProgress(timeSpent: number, scrollPercentage: number): number {
    const timeProgress = Math.min(1, timeSpent / this.MIN_READ_TIME);
    const scrollProgress = scrollPercentage;

    // Average of time and scroll progress
    return (timeProgress + scrollProgress) / 2;
  }

  /**
   * Get module status based on sections
   */
  private getModuleStatus(
    sections: SectionProgress[]
  ): 'not_started' | 'in_progress' | 'completed' {
    if (sections.length === 0) return 'not_started';

    const allCompleted = sections.every((s) => s.status === 'completed');
    if (allCompleted) return 'completed';

    const anyStarted = sections.some((s) => s.status !== 'not_started');
    return anyStarted ? 'in_progress' : 'not_started';
  }

  /**
   * Clear section timer
   */
  private clearSectionTimer(section_id: string): void {
    const timer = this.sectionTimers.get(section_id);
    if (timer) {
      clearInterval(timer);
      this.sectionTimers.delete(section_id);
    }
  }

  /**
   * Store progress in localStorage with user ID
   */
  private async persistProgress(user_id: string, progress: UserProgress): Promise<void> {
    try {
      const key = `${this.PROGRESS_KEY_PREFIX}_${user_id}`;
      this.storage.set<UserProgress>(key, progress);
    } catch (error) {
      console.error('Failed to persist progress:', error);
      throw error;
    }
  }

  /**
   * Clear all progress for a user
   */
  async clearProgress(user_id: string): Promise<void> {
    try {
      const key = `${this.PROGRESS_KEY_PREFIX}_${user_id}`;
      this.storage.remove(key);
    } catch (error) {
      console.error('Failed to clear progress:', error);
      throw error;
    }
  }
}

export const progressService = new ProgressService();
