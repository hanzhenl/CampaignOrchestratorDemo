<script lang="ts">
  import { experiencePanelData, experiencePanelType } from '../stores';

  export let items: any[] = [];

  function viewArticle(article: any) {
    experiencePanelData.set({ ...article, type: 'compendium' });
    experiencePanelType.set('compendium');
  }
</script>

<div class="space-y-4">
  <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Compendium</h2>
  <div class="space-y-2">
    {#each items as article}
      <button
        on:click={() => viewArticle(article)}
        class="w-full text-left p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        <div class="font-semibold text-gray-900 dark:text-white">{article.title}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">{article.content?.substring(0, 100)}...</div>
      </button>
    {/each}
  </div>
</div>
