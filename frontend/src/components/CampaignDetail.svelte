<script lang="ts">
  import { onMount } from 'svelte';

  export let data: any;
  let campaign: any = null;
  let metrics: any = null;

  onMount(async () => {
    if (data.id && data.type !== 'campaign') {
      // Only fetch if we have an ID and it's not already a full campaign object
      try {
        const response = await fetch(`/api/v1/campaigns/${data.id}`);
        campaign = await response.json();
        
        const metricsResponse = await fetch(`/api/v1/campaigns/${data.id}/metrics`);
        metrics = await metricsResponse.json();
      } catch (e) {
        // If fetch fails, use the data as-is
        campaign = data;
      }
    } else {
      campaign = data;
      // Try to fetch metrics if we have an ID
      if (data.id) {
        try {
          const metricsResponse = await fetch(`/api/v1/campaigns/${data.id}/metrics`);
          metrics = await metricsResponse.json();
        } catch (e) {
          // Ignore metrics fetch errors
        }
      }
    }
  });
</script>

{#if campaign}
  <div class="space-y-4">
    <div>
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{campaign.name}</h2>
      <p class="text-gray-600 dark:text-gray-400">{campaign.description}</p>
    </div>

    <div class="grid grid-cols-2 gap-4">
      <div>
        <div class="text-sm text-gray-500 dark:text-gray-400">Goals</div>
        <div class="text-lg font-semibold text-gray-900 dark:text-white">
          {campaign.goals?.join(', ') || 'N/A'}
        </div>
      </div>
      <div>
        <div class="text-sm text-gray-500 dark:text-gray-400">Status</div>
        <div class="text-lg font-semibold text-gray-900 dark:text-white">{campaign.status}</div>
      </div>
      <div>
        <div class="text-sm text-gray-500 dark:text-gray-400">Audience Size</div>
        <div class="text-lg font-semibold text-gray-900 dark:text-white">
          {campaign.estimatedAudienceSize?.toLocaleString()}
        </div>
      </div>
      <div>
        <div class="text-sm text-gray-500 dark:text-gray-400">Channels</div>
        <div class="text-lg font-semibold text-gray-900 dark:text-white">
          {campaign.channels?.join(', ')}
        </div>
      </div>
    </div>

    {#if metrics}
      <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
        <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Metrics</h3>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <div class="text-sm text-gray-500 dark:text-gray-400">Delivered</div>
            <div class="text-xl font-bold text-gray-900 dark:text-white">{metrics.delivered?.toLocaleString()}</div>
          </div>
          <div>
            <div class="text-sm text-gray-500 dark:text-gray-400">Open Rate</div>
            <div class="text-xl font-bold text-gray-900 dark:text-white">{metrics.openRate?.toFixed(1)}%</div>
          </div>
          <div>
            <div class="text-sm text-gray-500 dark:text-gray-400">Click Rate</div>
            <div class="text-xl font-bold text-gray-900 dark:text-white">{metrics.clickRate?.toFixed(1)}%</div>
          </div>
          <div>
            <div class="text-sm text-gray-500 dark:text-gray-400">Conversion Rate</div>
            <div class="text-xl font-bold text-gray-900 dark:text-white">{metrics.conversionRate?.toFixed(1)}%</div>
          </div>
        </div>
      </div>
    {/if}
  </div>
{/if}
