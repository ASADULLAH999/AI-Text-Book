import { useEffect, useState, useCallback } from 'react';
import { ModuleProgress, ProgressState } from '../types/progress';
import { progressService } from '../services/progress-service';

/**
 * useProgress - Manage user progress state
 */
export function useProgress(user_id: string): {
  progress: ProgressState;
  updateProgress: (module_id: string, progress: ModuleProgress) => Promise<void>;
  getOverallProgress: () => number;
  resetProgress: () => void;
  isLoading: boolean;
  error: string | null;
} {
  const [progress, setProgress] = useState<ProgressState>({
    modules: {},
    total_progress: 0,
    is_loading: true,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load progress on mount
  useEffect(() => {
    const loadProgress = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const userProgress = await progressService.getUserProgress(user_id);

        setProgress({
          modules: userProgress.modules,
          total_progress: userProgress.overall_progress_percentage,
          is_loading: false,
        });

        setIsLoading(false);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load progress';
        setError(errorMessage);
        setIsLoading(false);
      }
    };

    loadProgress();
  }, [user_id]);

  const updateProgress = useCallback(
    async (module_id: string, moduleProgress: ModuleProgress) => {
      try {
        await progressService.updateModuleProgress(user_id, module_id, moduleProgress);

        // Refresh progress state
        const userProgress = await progressService.getUserProgress(user_id);
        setProgress({
          modules: userProgress.modules,
          total_progress: userProgress.overall_progress_percentage,
          is_loading: false,
        });
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to update progress';
        setError(errorMessage);
        throw err;
      }
    },
    [user_id]
  );

  const getOverallProgress = useCallback(() => {
    return progressService.calculateOverallProgress(progress.modules);
  }, [progress.modules]);

  const resetProgress = useCallback(async () => {
    try {
      await progressService.clearProgress(user_id);

      // Reset state
      setProgress({
        modules: {},
        total_progress: 0,
        is_loading: false,
      });
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to reset progress';
      setError(errorMessage);
    }
  }, [user_id]);

  return {
    progress,
    updateProgress,
    getOverallProgress,
    resetProgress,
    isLoading,
    error,
  };
}
