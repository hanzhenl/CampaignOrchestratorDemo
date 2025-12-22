<script lang="ts">
  import { experiencePanelData, experiencePanelType } from '../stores';
  import { onMount } from 'svelte';

  export let items: any[] = [];
  let segments: any[] = [];

  onMount(async () => {
    const response = await fetch('/api/v1/segments');
    segments = await response.json();
  });

  function getStatusClass(status: string): string {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'completed':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'draft':
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
  }

  function getSegmentName(segmentId: string): string {
    const segment = segments.find(s => s.id === segmentId);
    return segment ? segment.name : segmentId;
  }

  function viewCampaign(campaign: any) {
    experiencePanelData.set(campaign);
    experiencePanelType.set('campaign');
  }

  function createNewCampaign() {
    experiencePanelData.set({ name: '', goals: [], segmentIds: [] });
    experiencePanelType.set('campaign_form');
  }

  function formatDate(dateString: string): string {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }
</script>

<div class="space-y-4">
  <div class="flex justify-between items-center">
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Campaigns</h2>
    <button
      on:click={createNewCampaign}
      class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
    >
      New Campaign
    </button>
  </div>

  <div class="overflow-x-auto">
    <table class="w-full border-collapse">
      <thead>
        <tr class="border-b border-gray-200 dark:border-gray-700">
          <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Campaign</th>
          <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Status</th>
          <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Goal</th>
          <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Segment</th>
          <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Progress</th>
          <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">End Date</th>
          <th class="text-left py-3 px-4"></th>
        </tr>
      </thead>
      <tbody>
        {#each items as campaign}
          <tr 
            on:click={() => viewCampaign(campaign)}
            class="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors"
          >
            <td class="py-3 px-4">
              <div class="font-medium text-gray-900 dark:text-white">{campaign.name}</div>
            </td>
            <td class="py-3 px-4">
              <span class="px-2 py-1 rounded-full text-xs font-medium {getStatusClass(campaign.status)}">
                {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
              </span>
            </td>
            <td class="py-3 px-4 text-gray-700 dark:text-gray-300">
              {campaign.goals?.join(', ') || 'N/A'}
            </td>
            <td class="py-3 px-4">
              <div class="flex flex-wrap gap-1">
                {#each (campaign.segmentIds || []).slice(0, 2) as segmentId}
                  <span class="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-full text-xs">
                    {getSegmentName(segmentId)}
                  </span>
                {/each}
                {#if (campaign.segmentIds || []).length > 2}
                  <span class="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-full text-xs">
                    +{(campaign.segmentIds || []).length - 2}
                  </span>
                {/if}
              </div>
            </td>
            <td class="py-3 px-4">
              <div class="flex items-center gap-2">
                <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2 min-w-[60px]">
                  <div 
                    class="bg-blue-600 h-2 rounded-full transition-all"
                    style="width: {campaign.progress || 0}%"
                  ></div>
                </div>
                <span class="text-sm text-gray-700 dark:text-gray-300">{campaign.progress || 0}%</span>
              </div>
            </td>
            <td class="py-3 px-4 text-gray-700 dark:text-gray-300">
              {formatDate(campaign.endDate)}
            </td>
            <td class="py-3 px-4">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
