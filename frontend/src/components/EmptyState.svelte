<script lang="ts">
  import { experiencePanelData, experiencePanelType } from '../stores';

  async function loadCampaigns() {
    const response = await fetch('/api/v1/campaigns');
    const campaigns = await response.json();
    experiencePanelData.set({ type: 'campaign_list', items: campaigns });
    experiencePanelType.set('campaign_list');
  }

  async function loadSegments() {
    const response = await fetch('/api/v1/segments');
    const segments = await response.json();
    experiencePanelData.set({ type: 'segment_list', items: segments });
    experiencePanelType.set('segment_list');
  }

  async function loadCompendium() {
    const response = await fetch('/api/v1/compendium');
    const compendium = await response.json();
    experiencePanelData.set({ type: 'compendium_list', items: compendium });
    experiencePanelType.set('compendium_list');
  }
</script>

<div class="w-full h-full flex items-center justify-center">
  <div class="text-center space-y-6">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
      AI-native Campaign Orchestrator
    </h1>
    <p class="text-gray-600 dark:text-gray-400 max-w-md">
      Start by creating a campaign, exploring existing campaigns, or searching for segments and compendium articles.
    </p>
    <div class="flex gap-4 justify-center">
      <button
        on:click={loadCampaigns}
        class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
      >
        View Campaigns
      </button>
      <button
        on:click={loadSegments}
        class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
      >
        View Segments
      </button>
      <button
        on:click={loadCompendium}
        class="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
      >
        View Compendium
      </button>
    </div>
  </div>
</div>
