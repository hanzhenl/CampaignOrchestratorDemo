<script lang="ts">
  import { onMount } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { currentSession, experiencePanelData, experiencePanelType } from '../stores';

  const dispatch = createEventDispatcher();
  let sessions: any[] = [];
  let loading = true;

  onMount(async () => {
    const response = await fetch('/api/v1/dialog/sessions');
    sessions = await response.json();
    loading = false;
  });

  async function loadSession(sessionId: string) {
    const response = await fetch(`/api/v1/dialog/sessions/${sessionId}`);
    const session = await response.json();
    currentSession.set(session);
    dispatch('close');
  }

  async function createNewSession() {
    // Clear all state to return to empty state
    currentSession.set(null);
    experiencePanelData.set(null);
    experiencePanelType.set(null);
    dispatch('close');
  }
</script>

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col">
    <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Dialog History</h2>
      <button
        on:click={() => dispatch('close')}
        class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
      >
        ✕
      </button>
    </div>
    <div class="flex-1 overflow-y-auto p-4">
      <button
        on:click={createNewSession}
        class="w-full mb-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
      >
        New Request
      </button>
      {#if loading}
        <div class="text-center text-gray-500">Loading...</div>
      {:else if sessions.length === 0}
        <div class="text-center text-gray-500">No dialog sessions yet</div>
      {:else}
        {#each sessions as session}
          <button
            on:click={() => loadSession(session.id)}
            class="w-full text-left p-4 mb-2 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <div class="font-semibold text-gray-900 dark:text-white">{session.title}</div>
            <div class="text-sm text-gray-500 dark:text-gray-400">
              {new Date(session.updatedAt).toLocaleString()}
            </div>
          </button>
        {/each}
      {/if}
    </div>
  </div>
</div>
