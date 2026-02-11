import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://zqyijbfkdomulinqnewb.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpxeWlqYmZrZG9tdWxpbnFuZXdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk1NzAwMjMsImV4cCI6MjA4NTE0NjAyM30.wkEKuTbkwFbce7Tgf-ZmtjUW_yG4ZPFPTp4SwH33chU';

// Initialize Supabase client with proper configuration
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true, // Disable for client-side only auth
    storage: typeof window !== 'undefined' ? window.localStorage : undefined,
  },
});
