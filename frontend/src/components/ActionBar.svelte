<script lang="ts">
  import UserInput from './UserInput.svelte';
  import DialogHistory from './DialogHistory.svelte';
  import { currentSession, experiencePanelData } from '../stores';

  let showDialogHistory = false;
</script>

<div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 shadow-sm">
  <div class="flex items-center justify-between gap-4">
    {#if $currentSession || $experiencePanelData}
      <div class="flex-1">
        <UserInput />
      </div>
    {/if}
    <button
      on:click={() => (showDialogHistory = !showDialogHistory)}
      class="flex items-center gap-2 px-6 py-3 border-2 border-blue-600 dark:border-blue-500 rounded-lg bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors font-medium"
    >
      <!-- Clock/History Icon -->
      <svg
        class="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      Dialog History
    </button>
  </div>
  
  {#if showDialogHistory}
    <DialogHistory on:close={() => (showDialogHistory = false)} />
  {/if}
</div>
