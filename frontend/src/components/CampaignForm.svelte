<script lang="ts">
  import { experiencePanelData } from '../stores';

  let formData: any = $experiencePanelData || {
    name: '',
    description: '',
    goal: 'purchase',
    channels: [],
    estimatedAudienceSize: 0,
    schedule: { type: 'immediate' },
    userFlowConfig: { flowType: 'sequential', steps: [] },
    variants: []
  };

  $: if ($experiencePanelData && $experiencePanelData.name) {
    formData = { ...formData, ...$experiencePanelData };
  }

  async function saveCampaign() {
    const response = await fetch('/api/v1/campaigns', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });
    
    if (response.ok) {
      alert('Campaign saved successfully!');
      const campaign = await response.json();
      experiencePanelData.set(campaign);
    } else {
      alert('Error saving campaign');
    }
  }

  function toggleChannel(channel: string) {
    if (formData.channels.includes(channel)) {
      formData.channels = formData.channels.filter((c: string) => c !== channel);
    } else {
      formData.channels = [...formData.channels, channel];
    }
    formData = formData;
  }
</script>

<div class="space-y-6">
  <div>
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
      Campaign Name
    </label>
    <input
      type="text"
      bind:value={formData.name}
      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
      maxlength="100"
    />
  </div>

  <div>
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
      Description
    </label>
    <textarea
      bind:value={formData.description}
      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
      rows="3"
      maxlength="500"
    ></textarea>
  </div>

  <div>
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
      Campaign Goal
    </label>
    <select
      bind:value={formData.goal}
      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
    >
      <option value="purchase">Purchase</option>
      <option value="start_session">Start Session</option>
      <option value="open_message">Open Message</option>
      <option value="custom_event">Custom Event</option>
    </select>
  </div>

  <div>
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
      Channels
    </label>
    <div class="flex gap-4">
      <label class="flex items-center">
        <input
          type="checkbox"
          checked={formData.channels.includes('email')}
          on:change={() => toggleChannel('email')}
          class="mr-2"
        />
        Email
      </label>
      <label class="flex items-center">
        <input
          type="checkbox"
          checked={formData.channels.includes('sms')}
          on:change={() => toggleChannel('sms')}
          class="mr-2"
        />
        SMS
      </label>
      <label class="flex items-center">
        <input
          type="checkbox"
          checked={formData.channels.includes('push')}
          on:change={() => toggleChannel('push')}
          class="mr-2"
        />
        Push
      </label>
    </div>
  </div>

  <div>
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
      Estimated Audience Size
    </label>
    <input
      type="number"
      bind:value={formData.estimatedAudienceSize}
      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
    />
  </div>

  <div>
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
      Schedule
    </label>
    <select
      bind:value={formData.schedule.type}
      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
    >
      <option value="immediate">Immediate</option>
      <option value="scheduled">Scheduled</option>
    </select>
  </div>

  {#if formData.userFlowConfig}
    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        User Flow Type
      </label>
      <div class="text-sm text-gray-600 dark:text-gray-400">
        {formData.userFlowConfig.flowType || 'sequential'}
      </div>
    </div>
  {/if}

  <div class="flex gap-2">
    <button
      on:click={saveCampaign}
      class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
    >
      Save Campaign
    </button>
    <button
      on:click={() => experiencePanelData.set(null)}
      class="px-6 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-white rounded-lg transition-colors"
    >
      Cancel
    </button>
  </div>
</div>
