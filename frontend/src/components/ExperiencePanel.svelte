<script lang="ts">
  import { experiencePanelData, experiencePanelType } from '../stores';
  import CampaignForm from './CampaignForm.svelte';
  import CampaignDetail from './CampaignDetail.svelte';
  import CampaignList from './CampaignList.svelte';
  import SegmentDetail from './SegmentDetail.svelte';
  import SegmentList from './SegmentList.svelte';
  import CompendiumDetail from './CompendiumDetail.svelte';
  import CompendiumList from './CompendiumList.svelte';
</script>

<div class="h-full bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 flex flex-col">
  <div class="p-4 border-b border-gray-200 dark:border-gray-700">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Experience Panel</h3>
  </div>
  <div class="flex-1 overflow-y-auto p-4">
    {#if $experiencePanelData}
      {#if $experiencePanelType === 'campaign_list'}
        <CampaignList items={$experiencePanelData.items || []} />
      {:else if $experiencePanelType === 'segment_list'}
        <SegmentList items={$experiencePanelData.items || []} />
      {:else if $experiencePanelType === 'compendium_list'}
        <CompendiumList items={$experiencePanelData.items || []} />
      {:else if $experiencePanelType === 'campaign_form' || ($experiencePanelData && $experiencePanelData.name && !$experiencePanelType)}
        <CampaignForm data={$experiencePanelData} />
      {:else if $experiencePanelType === 'campaign'}
        <CampaignDetail data={$experiencePanelData} />
      {:else if $experiencePanelType === 'segment'}
        <SegmentDetail data={$experiencePanelData} />
      {:else if $experiencePanelType === 'compendium'}
        <CompendiumDetail data={$experiencePanelData} />
      {:else}
        <div class="text-gray-500 dark:text-gray-400">
          <pre>{JSON.stringify($experiencePanelData, null, 2)}</pre>
        </div>
      {/if}
    {:else}
      <div class="text-center text-gray-500 dark:text-gray-400 py-8">
        Experience panel will show here when you interact with the system.
      </div>
    {/if}
  </div>
</div>
