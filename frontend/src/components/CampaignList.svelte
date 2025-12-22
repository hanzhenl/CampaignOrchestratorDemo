<script lang="ts">
  import { experiencePanelData, experiencePanelType } from '../stores';

  export let items: any[] = [];

  async function viewCampaign(campaign: any) {
    if (campaign.id) {
      const response = await fetch(`/api/v1/campaigns/${campaign.id}`);
      const fullCampaign = await response.json();
      experiencePanelData.set(fullCampaign);
      experiencePanelType.set('campaign');
    } else {
      experiencePanelData.set(campaign);
      experiencePanelType.set('campaign');
    }
  }
</script>

<div class="space-y-4">
  <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Campaigns</h2>
  <div class="space-y-2">
    {#each items as campaign}
      <button
        on:click={() => viewCampaign(campaign)}
        class="w-full text-left p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        <div class="font-semibold text-gray-900 dark:text-white">{campaign.name}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">{campaign.description}</div>
        <div class="text-xs text-gray-500 dark:text-gray-500 mt-1">
          {campaign.status} • {campaign.channels?.join(', ')} • {campaign.estimatedAudienceSize?.toLocaleString()} users
        </div>
      </button>
    {/each}
  </div>
</div>
