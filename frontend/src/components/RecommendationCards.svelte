<script lang="ts">
  import RecommendationCard from './RecommendationCard.svelte';

  export let items: any[] = [];
  export let type: 'campaign' | 'segment' | 'mixed' = 'mixed';
  export let title: string | null = null;
  export let description: string | null = null;
</script>

<div class="space-y-4">
  {#if title}
    <div>
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{title}</h2>
      {#if description}
        <p class="text-gray-600 dark:text-gray-400 mt-1">{description}</p>
      {/if}
    </div>
  {/if}

  {#if items && items.length > 0}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      {#each items as item (item.id || item.name || item)}
        {#if type === 'mixed'}
          {@const itemType = item.segmentIds ? 'campaign' : item.size !== undefined ? 'segment' : 'campaign'}
          <RecommendationCard item={item} type={itemType} />
        {:else}
          <RecommendationCard item={item} type={type} />
        {/if}
      {/each}
    </div>
  {:else}
    <div class="text-center text-gray-500 dark:text-gray-400 py-8">
      <p>No recommendations available</p>
    </div>
  {/if}
</div>

