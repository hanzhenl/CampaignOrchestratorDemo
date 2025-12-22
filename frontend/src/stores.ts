import { writable } from 'svelte/store';

export interface DialogSession {
  id: string;
  title: string;
  messages: Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    reasoningSteps?: Array<any>;
    timestamp: string;
  }>;
  createdAt: string;
  updatedAt: string;
}

export interface SearchResult {
  id: string;
  type: 'campaign' | 'segment' | 'compendium';
  title: string;
  description: string;
  relevance: number;
}

export const currentSession = writable<DialogSession | null>(null);
export const searchResults = writable<SearchResult[]>([]);
export const experiencePanelData = writable<any>(null);
export const experiencePanelType = writable<string | null>(null);
