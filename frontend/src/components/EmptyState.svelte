<script lang="ts">
  import { searchResults, currentSession, experiencePanelData, experiencePanelType } from '../stores';
  
  let inputValue = '';
  let showSearchResults = false;
  let searchTimeout: number | null = null;

  async function loadCampaigns() {
    const response = await fetch('/api/v1/campaigns');
    const campaigns = await response.json();
    experiencePanelData.set({ type: 'campaign_list', items: campaigns });
    experiencePanelType.set('campaign_list');
  }

  async function loadSegments() {
    const response = await fetch('/api/v1/segments');
    const segments = await response.json();
    experiencePanelData.set({ type: 'segment_list', items: segments });
    experiencePanelType.set('segment_list');
  }

  async function loadKnowledge() {
    const response = await fetch('/api/v1/knowledge');
    const knowledge = await response.json();
    experiencePanelData.set({ type: 'knowledge_list', items: knowledge });
    experiencePanelType.set('knowledge_list');
  }

  async function handleInput() {
    if (searchTimeout) clearTimeout(searchTimeout);
    
    if (inputValue.length < 3) {
      showSearchResults = false;
      return;
    }

    // Short queries trigger search
    if (inputValue.length < 50) {
      searchTimeout = setTimeout(async () => {
        const response = await fetch(`/api/v1/search?q=${encodeURIComponent(inputValue)}&type=all`);
        const results = await response.json();
        searchResults.set(results);
        showSearchResults = results.length > 0;
      }, 300);
    } else {
      showSearchResults = false;
    }
  }

  async function handleSubmit() {
    if (!inputValue.trim()) return;

    // If it's a short query, treat as search
    if (inputValue.length < 50) {
      await handleInput();
      return;
    }

    // Long queries trigger AI agent
    let sessionId: string | null = $currentSession?.id || null;

    if (!sessionId) {
      // Create new session
      const response = await fetch('/api/v1/dialog/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: inputValue.substring(0, 50) })
      });
      const newSession = await response.json();
      sessionId = newSession.id;
      currentSession.set(newSession);
    }

    // Send to agent orchestrator
    const response = await fetch('/api/v1/agent/orchestrate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: inputValue,
        sessionId: sessionId
      })
    });

    const result = await response.json();
    
    // Update experience panel
    experiencePanelData.set(result.campaignConfig || result);
    experiencePanelType.set(result.experiencePanelType || 'default');

    // Refresh session to get updated messages
    const sessionResponse = await fetch(`/api/v1/dialog/sessions/${sessionId}`);
    const updatedSession = await sessionResponse.json();
    currentSession.set(updatedSession);

    inputValue = '';
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  function selectSearchResult(result: any) {
    experiencePanelData.set(result);
    experiencePanelType.set(result.type);
    showSearchResults = false;
    inputValue = '';
  }
</script>

<div class="w-full h-full flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900">
  <!-- Logo and Title -->
  <div class="flex items-center gap-3 mb-8">
    <!-- Diamond Logo with Gradient -->
    <div class="w-12 h-12 relative">
      <svg viewBox="0 0 48 48" class="w-full h-full">
        <defs>
          <linearGradient id="logoGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#9333ea;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:1" />
          </linearGradient>
        </defs>
        <path d="M24 4 L44 24 L24 44 L4 24 Z" fill="url(#logoGradient)"/>
      </svg>
    </div>
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
      Campaign Launchpad
    </h1>
  </div>

  <!-- Input Field with Icons -->
  <div class="relative w-full max-w-2xl mb-8">
    <div class="relative flex items-center bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 rounded-lg shadow-sm">
      <!-- Left Icons -->
      <div class="flex items-center gap-2 px-4">
        <button class="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200" title="Add">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
        </button>
        <button class="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200" title="Attach">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
          </svg>
        </button>
        <button class="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200" title="History">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
      
      <!-- Input Field -->
      <input
        type="text"
        bind:value={inputValue}
        on:input={handleInput}
        on:keydown={handleKeydown}
        placeholder="What are we launching today?"
        class="flex-1 px-4 py-4 bg-transparent border-0 focus:outline-none text-gray-900 dark:text-white placeholder-gray-400"
      />
      
      <!-- Send Icon -->
      <button
        on:click={handleSubmit}
        class="p-2 mr-2 text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
        title="Send"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
        </svg>
      </button>
    </div>

    <!-- Search Results Dropdown -->
    {#if showSearchResults}
      <div class="absolute z-10 w-full mt-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-64 overflow-y-auto">
        {#each $searchResults as result}
          <button
            on:click={() => selectSearchResult(result)}
            class="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <div class="font-semibold text-gray-900 dark:text-white">{result.title}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400">{result.type} • {result.description}</div>
          </button>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Entry Buttons -->
  <div class="flex gap-4">
    <button
      on:click={loadCampaigns}
      class="flex items-center gap-2 px-6 py-3 border-2 border-blue-600 dark:border-blue-500 rounded-lg bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors font-medium"
    >
      <!-- Megaphone Icon -->
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
      </svg>
      Campaign
    </button>
    
    <button
      on:click={loadSegments}
      class="flex items-center gap-2 px-6 py-3 border-2 border-blue-600 dark:border-blue-500 rounded-lg bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors font-medium"
    >
      <!-- Two People Icon -->
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
      Audience
    </button>
    
    <button
      on:click={loadKnowledge}
      class="flex items-center gap-2 px-6 py-3 border-2 border-blue-600 dark:border-blue-500 rounded-lg bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors font-medium"
    >
      <!-- Graduation Cap Icon -->
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14v6" />
      </svg>
      Knowledge
    </button>
  </div>
</div>