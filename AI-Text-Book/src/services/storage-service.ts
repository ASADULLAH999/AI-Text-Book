import { StorageSchema } from '../types/entities';

/**
 * StorageService - Manages localStorage with schema validation and migration
 * Provides typed access to localStorage with automatic serialization
 */
class StorageService {
  private readonly STORAGE_KEY_PREFIX = 'ai_textbook';
  private readonly SCHEMA_VERSION = 1;
  private readonly SCHEMA_KEY = 'ai_textbook_schema_version';

  constructor() {
    if (typeof window !== 'undefined') {
      this.validateAndMigrate();
    }
  }

  /**
   * Get value from localStorage with type safety
   * @param key - Storage key
   * @param defaultValue - Default value if key doesn't exist
   * @returns Value from storage or default
   */
  get<T>(key: string, defaultValue?: T): T | undefined {
    if (typeof window === 'undefined') return defaultValue;
    try {
      const item = localStorage.getItem(this.prefixKey(key));
      if (item === null) {
        return defaultValue;
      }
      return JSON.parse(item) as T;
    } catch (error) {
      console.warn(`Error retrieving storage key "${key}":`, error);
      return defaultValue;
    }
  }

  /**
   * Set value in localStorage with type safety
   * @param key - Storage key
   * @param value - Value to store
   */
  set<T>(key: string, value: T): void {
    if (typeof window === 'undefined') return;
    try {
      localStorage.setItem(this.prefixKey(key), JSON.stringify(value));
    } catch (error) {
      console.warn(`Error setting storage key "${key}":`, error);
      // Handle quota exceeded
      if (error instanceof DOMException && error.code === 22) {
        this.handleQuotaExceeded();
      }
    }
  }

  /**
   * Remove value from localStorage
   * @param key - Storage key
   */
  remove(key: string): void {
    if (typeof window === 'undefined') return;
    try {
      localStorage.removeItem(this.prefixKey(key));
    } catch (error) {
      console.warn(`Error removing storage key "${key}":`, error);
    }
  }

  /**
   * Clear all application data from localStorage
   */
  clear(): void {
    if (typeof window === 'undefined') return;
    try {
      const keys = Object.keys(localStorage);
      keys.forEach((key) => {
        if (key.startsWith(this.STORAGE_KEY_PREFIX)) {
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      console.warn('Error clearing storage:', error);
    }
  }

  /**
   * Check if a key exists in localStorage
   * @param key - Storage key
   */
  has(key: string): boolean {
    if (typeof window === 'undefined') return false;
    return localStorage.getItem(this.prefixKey(key)) !== null;
  }

  /**
   * Get all keys in storage
   */
  keys(): string[] {
    if (typeof window === 'undefined') return [];
    const keys: string[] = [];
    const prefix = this.STORAGE_KEY_PREFIX + '_';
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(prefix)) {
        keys.push(key.substring(prefix.length));
      }
    }
    return keys;
  }

  /**
   * Get storage size in bytes
   */
  getStorageSize(): number {
    if (typeof window === 'undefined') return 0;
    let size = 0;
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.STORAGE_KEY_PREFIX)) {
        const value = localStorage.getItem(key);
        if (value) {
          size += key.length + value.length;
        }
      }
    }
    return size;
  }

  /**
   * Get storage size in MB
   */
  getStorageSizeMB(): number {
    return Math.round((this.getStorageSize() / 1024 / 1024) * 100) / 100;
  }

  /**
   * Validate schema version and migrate if needed
   */
  private validateAndMigrate(): void {
    if (typeof window === 'undefined') return;
    try {
      const storedVersion = localStorage.getItem(this.SCHEMA_KEY);
      const currentVersion = this.SCHEMA_VERSION.toString();

      if (!storedVersion) {
        // First time initialization
        localStorage.setItem(this.SCHEMA_KEY, currentVersion);
        return;
      }

      const version = parseInt(storedVersion, 10);
      if (version < this.SCHEMA_VERSION) {
        // Perform migrations here as needed
        this.performMigration(version, this.SCHEMA_VERSION);
        localStorage.setItem(this.SCHEMA_KEY, currentVersion);
      }
    } catch (error) {
      console.warn('Error during schema validation:', error);
    }
  }

  /**
   * Perform schema migrations between versions
   * @param fromVersion - Current version in storage
   * @param toVersion - Target version
   */
  private performMigration(fromVersion: number, toVersion: number): void {
    for (let v = fromVersion + 1; v <= toVersion; v++) {
      switch (v) {
        case 2:
          // Example migration: move old keys to new format
          // This is a placeholder for future migrations
          break;
        default:
          break;
      }
    }
  }

  /**
   * Handle localStorage quota exceeded error
   * Attempts to clean up old/temporary data
   */
  private handleQuotaExceeded(): void {
    console.warn('localStorage quota exceeded, attempting cleanup');
    // Clean up old quiz attempts (keep only last 3)
    const quizAttempts = this.get<any[]>('quiz_attempts', []) || [];
    if (quizAttempts && quizAttempts.length > 3) {
      const recent = quizAttempts.slice(-3);
      this.set('quiz_attempts', recent);
    }

    // Clean up old reading progress
    const progressKeys = this.keys().filter((k) => k.startsWith('progress_'));
    if (progressKeys.length > 5) {
      progressKeys.slice(0, -5).forEach((key) => this.remove(key));
    }
  }

  /**
   * Add prefix to storage key
   * @param key - Storage key
   */
  private prefixKey(key: string): string {
    return `${this.STORAGE_KEY_PREFIX}_${key}`;
  }
}

export const storageService = new StorageService();
