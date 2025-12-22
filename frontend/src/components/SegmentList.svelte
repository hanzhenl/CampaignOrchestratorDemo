<script lang="ts">
  import { experiencePanelData, experiencePanelType } from '../stores';

  export let items: any[] = [];

  function viewSegment(segment: any) {
    experiencePanelData.set({ ...segment, type: 'segment' });
    experiencePanelType.set('segment');
  }
</script>

<div class="space-y-4">
  <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Segments</h2>
  <div class="space-y-2">
    {#each items as segment}
      <button
        on:click={() => viewSegment(segment)}
        class="w-full text-left p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        <div class="font-semibold text-gray-900 dark:text-white">{segment.name}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">
          Size: {segment.size?.toLocaleString()} • Conversion Rate: {(segment.pastConversionRate * 100).toFixed(1)}%
        </div>
      </button>
    {/each}
  </div>
</div>
