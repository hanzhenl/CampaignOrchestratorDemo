<script lang="ts">
  import { searchResults, currentSession, experiencePanelData, experiencePanelType } from '../stores';
  
  let inputValue = '';
  let showSearchResults = false;
  let searchTimeout: number | null = null;

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
    // Get current session ID using reactive statement
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

<div class="relative w-full">
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
      class="flex-1 px-4 py-3 bg-transparent border-0 focus:outline-none text-gray-900 dark:text-white placeholder-gray-400"
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