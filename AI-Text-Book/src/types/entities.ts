export interface Module {
  id: string;
  name: string;
  description: string;
  icon: string;
  order: number;
  topics: Topic[];
}

export interface Topic {
  id: string;
  module_id: string;
  title: string;
  slug: string;
  order: number;
}

export interface Content {
  id: string;
  module_id: string;
  topic_id?: string;
  title: string;
  slug: string;
  body: string;
  reading_time: number;
  word_count: number;
  created_at: number;
  updated_at: number;
}

export interface Section {
  id: string;
  content_id: string;
  title: string;
  order: number;
}

export interface CookiePreferences {
  essential: boolean;
  analytics: boolean;
  preferences: boolean;
  timestamp: number;
}

export interface StorageSchema {
  version: number;
  auth?: any;
  progress?: any;
  quizzes?: any;
  language?: any;
  cookies?: any;
}
