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

<div class="relative">
  <div class="flex gap-2">
    <input
      type="text"
      bind:value={inputValue}
      on:input={handleInput}
      on:keydown={handleKeydown}
      placeholder="Search or describe your campaign..."
      class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
    />
    <button
      on:click={handleSubmit}
      class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
    >
      Send
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
