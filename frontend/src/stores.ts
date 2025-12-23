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
    isThinking?: boolean;
  }>;
  createdAt: string;
  updatedAt: string;
}

export interface SearchResult {
  id: string;
  type: 'campaign' | 'segment' | 'knowledge';
  title: string;
  description: string;
  relevance: number;
}

export const currentSession = writable<DialogSession | null>(null);
export const searchResults = writable<SearchResult[]>([]);
// Create base writable stores
const _experiencePanelData = writable<any>(null);
const _experiencePanelType = writable<string | null>(null);

// Create wrapped stores with logging
export const experiencePanelData = {
  subscribe: _experiencePanelData.subscribe,
  set: (value: any) => {
    // #region agent log
    const stack = new Error().stack;
    const caller = stack?.split('\n')[2]?.trim() || 'unknown';
    fetch('http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'stores.ts:experiencePanelData.set',message:'Store being set',data:{caller,hasValue:!!value,valueType:value?typeof value:'null',hasUiComponents:!!value?.uiComponents,uiComponentsCount:value?.uiComponents?.length||0,primaryComponent:value?.primaryComponent,valueKeys:value&&typeof value==='object'?Object.keys(value):null},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    _experiencePanelData.set(value);
  },
  update: _experiencePanelData.update
};

export const experiencePanelType = {
  subscribe: _experiencePanelType.subscribe,
  set: (value: string | null) => {
    // #region agent log
    const stack = new Error().stack;
    const caller = stack?.split('\n')[2]?.trim() || 'unknown';
    fetch('http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'stores.ts:experiencePanelType.set',message:'Store type being set',data:{caller,value},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    _experiencePanelType.set(value);
  },
  update: _experiencePanelType.update
};

// Knowledge article selection store
export interface KnowledgeArticle {
  id: string;
  title: string;
  content: string;
  articleType?: string;
  metadata?: any;
  createdAt?: string;
  updatedAt?: string;
}

export const selectedKnowledge = writable<KnowledgeArticle[]>([]);
