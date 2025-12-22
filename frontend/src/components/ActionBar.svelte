<script lang="ts">
  import UserInput from './UserInput.svelte';
  import DialogHistory from './DialogHistory.svelte';
  import { currentSession } from '../stores';

  let showDialogHistory = false;
</script>

<div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 shadow-sm">
  <div class="flex items-center justify-between gap-4">
    <div class="flex-1">
      <UserInput />
    </div>
    <button
      on:click={() => showDialogHistory = !showDialogHistory}
      class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
    >
      Dialog History
    </button>
  </div>
  
  {#if showDialogHistory}
    <DialogHistory on:close={() => showDialogHistory = false} />
  {/if}
</div>
