<script lang="ts">
  import { experiencePanelData } from '../stores';
  import { onMount } from 'svelte';

  let formData: any = $experiencePanelData || {
    name: '',
    description: '',
    goal: '',
    segmentIds: [],
    startDate: '',
    endDate: '',
    channels: [],
    estimatedAudienceSize: 0,
    creatives: [],
    userFlowConfig: {},
    controlGroup: null
  };

  let segments: any[] = [];
  let expandedCreatives: { [key: string]: boolean } = {
    'WhatsApp': true,
    'Google Ads': false,
    'Meta Ads': false
  };

  const goalOptions = [
    'Acquisition', 'Activation', 'Engagement', 'Retention', 
    'Reactivation', 'Upsell/Cross-sell', 'Brand Awareness', 
    'Promotional/Seasonal', 'Purchase Conversion', 'Start Session', 
    'Open Message', 'Custom Event'
  ];

  const channelOptions = ['WhatsApp', 'Google Ads', 'Meta Ads', 'Email', 'SMS', 'Push'];

  onMount(async () => {
    const response = await fetch('/api/v1/segments');
    segments = await response.json();
  });

  $: if ($experiencePanelData && ($experiencePanelData.name || $experiencePanelData.goals || $experiencePanelData.goal)) {
    // Handle both goals array (legacy) and goal string (new)
    const goal = $experiencePanelData.goal || ($experiencePanelData.goals && $experiencePanelData.goals.length > 0 ? $experiencePanelData.goals[0] : '');
    
    formData = { 
      ...formData, 
      ...$experiencePanelData,
      goal: goal,
      segmentIds: $experiencePanelData.segmentIds || [],
      channels: $experiencePanelData.channels || [],
      creatives: $experiencePanelData.creatives || [],
      userFlowConfig: $experiencePanelData.userFlowConfig || {}
    };
  }

  async function saveCampaign() {
    const response = await fetch('/api/v1/campaigns', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...formData,
        goals: formData.goal ? [formData.goal] : [],
        segmentIds: formData.segmentIds || [],
        channels: formData.channels || []
      })
    });
    
    if (response.ok) {
      alert('Campaign saved successfully!');
      const campaign = await response.json();
      experiencePanelData.set(campaign);
    } else {
      alert('Error saving campaign');
    }
  }

  function resetForm() {
    formData = {
      name: '',
      description: '',
      goal: '',
      segmentIds: [],
      startDate: '',
      endDate: '',
      channels: [],
      estimatedAudienceSize: 0,
      creatives: [],
      userFlowConfig: {},
      controlGroup: null
    };
  }

  async function saveDraft() {
    await saveCampaign();
  }

  function scheduleCampaign() {
    // For now, just save as scheduled
    saveCampaign();
  }

  function toggleSegment(segmentId: string) {
    if (!formData.segmentIds) formData.segmentIds = [];
    if (formData.segmentIds.includes(segmentId)) {
      formData.segmentIds = formData.segmentIds.filter((id: string) => id !== segmentId);
    } else {
      formData.segmentIds = [...formData.segmentIds, segmentId];
    }
    formData = formData;
  }

  function toggleChannel(channel: string) {
    if (!formData.channels) formData.channels = [];
    if (formData.channels.includes(channel)) {
      formData.channels = formData.channels.filter((c: string) => c !== channel);
    } else {
      formData.channels = [...formData.channels, channel];
    }
    formData = formData;
  }

  function getSegmentName(segmentId: string): string {
    const segment = segments.find(s => s.id === segmentId);
    return segment ? segment.name : segmentId;
  }

  function getCreativesByChannel(channel: string) {
    if (!formData.creatives || !Array.isArray(formData.creatives)) {
      return { channel, photos: [], copy: '' };
    }
    const creative = formData.creatives.find((c: any) => c.channel === channel);
    if (creative) {
      return creative;
    }
    return { channel, photos: [], copy: '' };
  }

  function updateCreative(channel: string, field: string, value: any) {
    if (!formData.creatives) formData.creatives = [];
    const index = formData.creatives.findIndex((c: any) => c.channel === channel);
    if (index >= 0) {
      formData.creatives[index] = { ...formData.creatives[index], [field]: value };
    } else {
      formData.creatives.push({ channel, [field]: value, photos: field === 'photos' ? value : [], copy: field === 'copy' ? value : '' });
    }
    formData = formData;
  }

  function toggleCreativesSection(channel: string) {
    expandedCreatives[channel] = !expandedCreatives[channel];
    expandedCreatives = expandedCreatives;
  }

  function getChannelIcon(channel: string): string {
    // Simple icon representation - can be enhanced later
    return '📱';
  }
</script>

<div class="space-y-6">
  <!-- Campaign Overview -->
  <div class="space-y-4">
    <div class="flex items-center gap-2">
      <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6-3 6H7.5m-4.5 0h4.5" />
      </svg>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Campaign Overview</h3>
    </div>
    
    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        Name
      </label>
      <input
        type="text"
        bind:value={formData.name}
        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
        maxlength="100"
        placeholder="Enter campaign name"
      />
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        Goal
      </label>
      <select
        bind:value={formData.goal}
        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
      >
        <option value="">Select a goal...</option>
        {#each goalOptions as goal}
          <option value={goal}>{goal}</option>
        {/each}
      </select>
    </div>

    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Start
        </label>
        <input
          type="date"
          bind:value={formData.startDate}
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          End
        </label>
        <input
          type="date"
          bind:value={formData.endDate}
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
        />
      </div>
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        Audience Segment
      </label>
      <div class="flex flex-wrap gap-2 mb-2">
        {#each (formData.segmentIds || []) as segmentId}
          <span class="px-3 py-1 bg-blue-600 text-white rounded-full text-sm flex items-center gap-2">
            {getSegmentName(segmentId)}
            <button
              on:click={() => toggleSegment(segmentId)}
              class="hover:text-blue-200"
            >
              ×
            </button>
          </span>
        {/each}
      </div>
      <select
        on:change={(e) => {
          const selectedId = e.target.value;
          if (selectedId && !formData.segmentIds?.includes(selectedId)) {
            toggleSegment(selectedId);
            e.target.value = '';
          }
        }}
        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
      >
        <option value="">Select a segment...</option>
        {#each segments as segment}
          <option value={segment.id}>{segment.name}</option>
        {/each}
      </select>
    </div>
  </div>

  <!-- Campaign Journey Section -->
  <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
    <div class="flex items-center gap-2 mb-4">
      <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
      </svg>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Campaign Journey</h3>
    </div>
    
    <div class="mb-3">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        Channels
      </label>
      <div class="flex flex-wrap gap-2 mb-2">
        {#each (formData.channels || []) as channel}
          <span class="px-3 py-1 bg-blue-600 text-white rounded-full text-sm flex items-center gap-2">
            {channel}
            <button
              on:click={() => toggleChannel(channel)}
              class="hover:text-blue-200"
            >
              ×
            </button>
          </span>
        {/each}
      </div>
      <select
        on:change={(e) => {
          const selectedChannel = e.target.value;
          if (selectedChannel && !formData.channels?.includes(selectedChannel)) {
            toggleChannel(selectedChannel);
            e.target.value = '';
          }
        }}
        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
      >
        <option value="">Select a channel...</option>
        {#each channelOptions as channel}
          <option value={channel}>{channel}</option>
        {/each}
      </select>
    </div>

    <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-3 min-h-[100px] flex items-center justify-center">
      <p class="text-sm text-gray-500 dark:text-gray-400">
        Journey preview will appear here
      </p>
    </div>

    <div class="flex justify-center">
      <button class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm">
        Edit
      </button>
    </div>
  </div>

  <!-- Creatives Section -->
  <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
    <div class="flex items-center gap-2 mb-4">
      <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Creatives</h3>
    </div>

    <!-- WhatsApp Section -->
    <div class="mb-4">
      <div class="flex items-center justify-between mb-2">
        <h4 class="text-md font-medium text-gray-800 dark:text-gray-200">WhatsApp</h4>
        <button
          on:click={() => toggleCreativesSection('WhatsApp')}
          class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={expandedCreatives['WhatsApp'] ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"} />
          </svg>
        </button>
      </div>
      {#if expandedCreatives['WhatsApp']}
        {@const whatsappCreative = getCreativesByChannel('WhatsApp')}
        <div class="space-y-3 pl-4 border-l-2 border-gray-200 dark:border-gray-700">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Photo
            </label>
            <div class="flex gap-2">
              {#each (whatsappCreative.photos || []) as photo}
                <img src={photo} alt="WhatsApp creative" class="w-20 h-20 object-cover rounded border border-gray-300 dark:border-gray-600" />
              {:else}
                <div class="w-20 h-20 bg-gray-200 dark:bg-gray-700 rounded border border-gray-300 dark:border-gray-600 flex items-center justify-center">
                  <span class="text-xs text-gray-400">Image</span>
                </div>
                <div class="w-20 h-20 bg-gray-200 dark:bg-gray-700 rounded border border-gray-300 dark:border-gray-600 flex items-center justify-center">
                  <span class="text-xs text-gray-400">Image</span>
                </div>
              {/each}
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Copy
            </label>
            <input
              type="text"
              value={whatsappCreative.copy || ''}
              on:input={(e) => updateCreative('WhatsApp', 'copy', e.target.value)}
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
              placeholder="Enter copy text"
            />
          </div>
          <button class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm">
            Edit
          </button>
        </div>
      {/if}
    </div>

    <!-- Google Ads Section -->
    <div class="mb-4">
      <div class="flex items-center justify-between mb-2">
        <h4 class="text-md font-medium text-gray-800 dark:text-gray-200">Google Ads</h4>
        <button
          on:click={() => toggleCreativesSection('Google Ads')}
          class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={expandedCreatives['Google Ads'] ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"} />
          </svg>
        </button>
      </div>
      {#if expandedCreatives['Google Ads']}
        {@const googleCreative = getCreativesByChannel('Google Ads')}
        <div class="space-y-3 pl-4 border-l-2 border-gray-200 dark:border-gray-700">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Photo
            </label>
            <div class="flex gap-2">
              {#each (googleCreative.photos || []) as photo}
                <img src={photo} alt="Google Ads creative" class="w-20 h-20 object-cover rounded border border-gray-300 dark:border-gray-600" />
              {:else}
                <div class="w-20 h-20 bg-gray-200 dark:bg-gray-700 rounded border border-gray-300 dark:border-gray-600 flex items-center justify-center">
                  <span class="text-xs text-gray-400">Image</span>
                </div>
              {/each}
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Copy
            </label>
            <input
              type="text"
              value={googleCreative.copy || ''}
              on:input={(e) => updateCreative('Google Ads', 'copy', e.target.value)}
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
              placeholder="Enter copy text"
            />
          </div>
          <button class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm">
            Edit
          </button>
        </div>
      {/if}
    </div>

    <!-- Meta Ads Section -->
    <div class="mb-4">
      <div class="flex items-center justify-between mb-2">
        <h4 class="text-md font-medium text-gray-800 dark:text-gray-200">Meta Ads</h4>
        <button
          on:click={() => toggleCreativesSection('Meta Ads')}
          class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={expandedCreatives['Meta Ads'] ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"} />
          </svg>
        </button>
      </div>
      {#if expandedCreatives['Meta Ads']}
        {@const metaCreative = getCreativesByChannel('Meta Ads')}
        <div class="space-y-3 pl-4 border-l-2 border-gray-200 dark:border-gray-700">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Photo
            </label>
            <div class="flex gap-2">
              {#each (metaCreative.photos || []) as photo}
                <img src={photo} alt="Meta Ads creative" class="w-20 h-20 object-cover rounded border border-gray-300 dark:border-gray-600" />
              {:else}
                <div class="w-20 h-20 bg-gray-200 dark:bg-gray-700 rounded border border-gray-300 dark:border-gray-600 flex items-center justify-center">
                  <span class="text-xs text-gray-400">Image</span>
                </div>
              {/each}
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Copy
            </label>
            <input
              type="text"
              value={metaCreative.copy || ''}
              on:input={(e) => updateCreative('Meta Ads', 'copy', e.target.value)}
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
              placeholder="Enter copy text"
            />
          </div>
          <button class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm">
            Edit
          </button>
        </div>
      {/if}
    </div>
  </div>

  <!-- Control Group Section -->
  <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
    <div class="flex items-center gap-2 mb-2">
      <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
      </svg>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Control Group</h3>
    </div>
    <p class="text-sm text-gray-600 dark:text-gray-400">
      Describe your campaign to generate journey steps
    </p>
  </div>

  <!-- Footer Buttons -->
  <div class="flex gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
    <button
      on:click={resetForm}
      class="px-6 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-white rounded-lg transition-colors"
    >
      Reset
    </button>
    <button
      on:click={saveDraft}
      class="px-6 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-white rounded-lg transition-colors"
    >
      Save as draft
    </button>
    <button
      on:click={scheduleCampaign}
      class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors ml-auto"
    >
      Schedule
    </button>
  </div>
</div>
