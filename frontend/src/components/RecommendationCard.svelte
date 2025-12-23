<script lang="ts">
  import { experiencePanelData, experiencePanelType } from '../stores';

  export let item: any;
  export let type: 'campaign' | 'segment' = 'campaign';

  function handleViewDetails() {
    // Preserve uiComponents structure when viewing details
    // Set the item with proper component structure
    const currentData = $experiencePanelData;
    if (currentData && currentData.uiComponents && Array.isArray(currentData.uiComponents)) {
      // Find the component for this item type
      const componentType = type === 'campaign' ? 'campaign' : 'segment';
      const existingComponent = currentData.uiComponents.find((c: any) => c.type === componentType);
      
      if (existingComponent) {
        // Update the existing component's data with the selected item
        const updatedComponents = currentData.uiComponents.map((c: any) => 
          c.type === componentType ? { ...c, data: { ...item, type } } : c
        );
        experiencePanelData.set({
          ...currentData,
          uiComponents: updatedComponents,
          primaryComponent: componentType
        });
        experiencePanelType.set(componentType);
      } else {
        // Add new component for this item
        const updatedComponents = [...currentData.uiComponents, {
          type: componentType,
          data: { ...item, type }
        }];
        experiencePanelData.set({
          ...currentData,
          uiComponents: updatedComponents,
          primaryComponent: componentType
        });
        experiencePanelType.set(componentType);
      }
    } else {
      // Fallback: create new uiComponents structure
      experiencePanelData.set({
        uiComponents: [{
          type: type === 'campaign' ? 'campaign' : 'segment',
          data: { ...item, type }
        }],
        primaryComponent: type === 'campaign' ? 'campaign' : 'segment'
      });
      experiencePanelType.set(type);
    }
  }

  function handleUseThis() {
    // For now, just view details. In future, this could trigger a "use this" action
    handleViewDetails();
  }
</script>

<div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow bg-white dark:bg-gray-800">
  <div class="flex justify-between items-start mb-2">
    <div class="flex-1">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
        {item.name || item.id || 'Unnamed'}
      </h3>
      {#if item.description}
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
          {item.description}
        </p>
      {/if}
    </div>
    {#if item.isSuggested}
      <span class="ml-2 px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
        Suggested
      </span>
    {/if}
  </div>

  {#if type === 'campaign'}
    <div class="space-y-2 mb-4">
      {#if item.goals && item.goals.length > 0}
        <div class="flex flex-wrap gap-1">
          {#each item.goals as goal}
            <span class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded">
              {goal}
            </span>
          {/each}
        </div>
      {/if}
      <div class="grid grid-cols-2 gap-2 text-sm">
        {#if item.estimatedAudienceSize !== undefined}
          <div>
            <span class="text-gray-500 dark:text-gray-400">Audience:</span>
            <span class="ml-1 font-medium text-gray-900 dark:text-white">
              {item.estimatedAudienceSize?.toLocaleString() || 'N/A'}
            </span>
          </div>
        {/if}
        {#if item.progress !== undefined}
          <div>
            <span class="text-gray-500 dark:text-gray-400">Progress:</span>
            <span class="ml-1 font-medium text-gray-900 dark:text-white">
              {item.progress?.toFixed(0)}%
            </span>
          </div>
        {/if}
        {#if item.status}
          <div>
            <span class="text-gray-500 dark:text-gray-400">Status:</span>
            <span class="ml-1 font-medium text-gray-900 dark:text-white">
              {item.status}
            </span>
          </div>
        {/if}
        {#if item.channels && item.channels.length > 0}
          <div>
            <span class="text-gray-500 dark:text-gray-400">Channels:</span>
            <span class="ml-1 font-medium text-gray-900 dark:text-white">
              {item.channels.join(', ')}
            </span>
          </div>
        {/if}
      </div>
    </div>
  {:else if type === 'segment'}
    <div class="space-y-2 mb-4">
      {#if item.size !== undefined}
        <div class="text-sm">
          <span class="text-gray-500 dark:text-gray-400">Size:</span>
          <span class="ml-1 font-medium text-gray-900 dark:text-white">
            {item.size?.toLocaleString() || 'N/A'}
          </span>
        </div>
      {/if}
      {#if item.pastConversionRate !== undefined}
        <div class="text-sm">
          <span class="text-gray-500 dark:text-gray-400">Conversion Rate:</span>
          <span class="ml-1 font-medium text-gray-900 dark:text-white">
            {(item.pastConversionRate * 100).toFixed(1)}%
          </span>
        </div>
      {/if}
      {#if item.criteria}
        <div class="text-sm">
          <span class="text-gray-500 dark:text-gray-400">Criteria:</span>
          <span class="ml-1 text-gray-700 dark:text-gray-300">
            {item.criteria}
          </span>
        </div>
      {/if}
    </div>
  {/if}

  <div class="flex gap-2 pt-2 border-t border-gray-200 dark:border-gray-700">
    <button
      on:click={handleViewDetails}
      class="flex-1 px-3 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors"
    >
      View Details
    </button>
    <button
      on:click={handleUseThis}
      class="flex-1 px-3 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
    >
      Use This
    </button>
  </div>
</div>

