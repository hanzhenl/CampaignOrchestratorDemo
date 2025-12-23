<script lang="ts">
  import { selectedKnowledge, type KnowledgeArticle } from '../stores';
  import { onMount } from 'svelte';

  export let isOpen = false;
  export let onClose: () => void = () => {};

  let knowledgeArticles: KnowledgeArticle[] = [];
  let loading = false;
  let searchQuery = '';

  onMount(async () => {
    await loadKnowledge();
  });

  async function loadKnowledge() {
    loading = true;
    try {
      const response = await fetch('/api/v1/knowledge');
      knowledgeArticles = await response.json();
    } catch (error) {
      console.error('Error loading knowledge articles:', error);
    } finally {
      loading = false;
    }
  }

  function toggleArticle(article: KnowledgeArticle) {
    const current = $selectedKnowledge;
    const isSelected = current.some(a => a.id === article.id);
    
    if (isSelected) {
      selectedKnowledge.set(current.filter(a => a.id !== article.id));
    } else {
      selectedKnowledge.set([...current, article]);
    }
  }

  function isArticleSelected(articleId: string): boolean {
    return $selectedKnowledge.some(a => a.id === articleId);
  }

  $: filteredArticles = knowledgeArticles.filter(article => {
    if (!searchQuery.trim()) return true;
    const query = searchQuery.toLowerCase();
    return (
      article.title.toLowerCase().includes(query) ||
      article.content.toLowerCase().includes(query)
    );
  });

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) {
      onClose();
    }
  }
</script>

{#if isOpen}
  <!-- Backdrop -->
  <div
    class="fixed inset-0 bg-black bg-opacity-50 z-40"
    on:click={handleBackdropClick}
    role="button"
    tabindex="-1"
  ></div>

  <!-- Modal -->
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4"
    role="dialog"
    aria-modal="true"
    aria-labelledby="modal-title"
  >
    <div
      class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col"
      on:click|stopPropagation
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h2
          id="modal-title"
          class="text-lg font-semibold text-gray-900 dark:text-white"
        >
          Select Knowledge Articles
        </h2>
        <button
          on:click={onClose}
          class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          aria-label="Close"
        >
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <!-- Search -->
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <input
          type="text"
          bind:value={searchQuery}
          placeholder="Search knowledge articles..."
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-4">
        {#if loading}
          <div class="text-center text-gray-500 dark:text-gray-400 py-8">
            Loading knowledge articles...
          </div>
        {:else if filteredArticles.length === 0}
          <div class="text-center text-gray-500 dark:text-gray-400 py-8">
            {searchQuery ? 'No articles found matching your search.' : 'No knowledge articles available.'}
          </div>
        {:else}
          <div class="space-y-2">
            {#each filteredArticles as article}
              <button
                on:click={() => toggleArticle(article)}
                class="w-full text-left p-4 border rounded-lg transition-colors {isArticleSelected(article.id)
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400'
                  : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'}"
              >
                <div class="flex items-start gap-3">
                  <div class="flex-shrink-0 mt-1">
                    {#if isArticleSelected(article.id)}
                      <svg
                        class="w-5 h-5 text-blue-600 dark:text-blue-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fill-rule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                          clip-rule="evenodd"
                        />
                      </svg>
                    {:else}
                      <div
                        class="w-5 h-5 border-2 border-gray-300 dark:border-gray-600 rounded"
                      ></div>
                    {/if}
                  </div>
                  <div class="flex-1 min-w-0">
                    <div
                      class="font-semibold text-gray-900 dark:text-white mb-1"
                    >
                      {article.title}
                    </div>
                    <div
                      class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2"
                    >
                      {article.content?.substring(0, 150)}
                      {article.content?.length > 150 ? '...' : ''}
                    </div>
                    {#if article.articleType}
                      <div class="mt-2">
                        <span
                          class="inline-block px-2 py-1 text-xs rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                        >
                          {article.articleType}
                        </span>
                      </div>
                    {/if}
                  </div>
                </div>
              </button>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between p-4 border-t border-gray-200 dark:border-gray-700">
        <div class="text-sm text-gray-600 dark:text-gray-400">
          {$selectedKnowledge.length} article{$selectedKnowledge.length === 1 ? '' : 's'} selected
        </div>
        <button
          on:click={onClose}
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          Done
        </button>
      </div>
    </div>
  </div>
{/if}

