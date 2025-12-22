<script lang="ts">
  import { experiencePanelData } from '../stores';
  import { onMount } from 'svelte';

  let formData: any = $experiencePanelData || {
    name: '',
    description: '',
    goals: [],
    segmentIds: [],
    startDate: '',
    endDate: '',
    channels: [],
    estimatedAudienceSize: 0,
    creatives: [],
    journeyDescription: '',
    controlGroup: null
  };

  let segments: any[] = [];
  let showCreatives = false;
  let showControlGroup = false;

  const goalOptions = [
    'Acquisition', 'Activation', 'Engagement', 'Retention', 
    'Reactivation', 'Upsell/Cross-sell', 'Brand Awareness', 
    'Promotional/Seasonal', 'Purchase', 'Start Session', 
    'Open Message', 'Custom Event'
  ];

  onMount(async () => {
    const response = await fetch('/api/v1/segments');
    segments = await response.json();
  });

  $: if ($experiencePanelData && ($experiencePanelData.name || $experiencePanelData.goals)) {
    formData = { 
      ...formData, 
      ...$experiencePanelData,
      goals: $experiencePanelData.goals || [],
      segmentIds: $experiencePanelData.segmentIds || []
    };
  }

  async function saveCampaign() {
    const response = await fetch('/api/v1/campaigns', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...formData,
        goals: formData.goals || [],
        segmentIds: formData.segmentIds || []
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

  function toggleGoal(goal: string) {
    if (!formData.goals) formData.goals = [];
    if (formData.goals.includes(goal)) {
      formData.goals = formData.goals.filter((g: string) => g !== goal);
    } else {
      formData.goals = [...formData.goals, goal];
    }
    formData = formData;
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

  function getSegmentName(segmentId: string): string {
    const segment = segments.find(s => s.id === segmentId);
    return segment ? segment.name : segmentId;
  }
</script>

<div class="space-y-6">
  <!-- Campaign Overview -->
  <div class="space-y-4">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Campaign Overview</h3>
    
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
      <div class="flex flex-wrap gap-2">
        {#each goalOptions as goal}
          <button
            on:click={() => toggleGoal(goal)}
            class="px-3 py-1 rounded-lg border transition-colors {formData.goals?.includes(goal) 
              ? 'bg-blue-600 text-white border-blue-600' 
              : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600'}"
          >
            {goal}
          </button>
        {/each}
      </div>
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
          <span class="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm flex items-center gap-2">
            {getSegmentName(segmentId)}
            <button
              on:click={() => toggleSegment(segmentId)}
              class="hover:text-blue-600 dark:hover:text-blue-400"
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

  <!-- Creatives Section -->
  <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
    <div class="flex items-center justify-between mb-2">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        Creatives
        {#if formData.creatives && formData.creatives.length > 0}
          <span class="ml-2 text-sm font-normal text-gray-500 dark:text-gray-400">
            {formData.creatives.length}
          </span>
        {/if}
      </h3>
      <button
        on:click={() => showCreatives = !showCreatives}
        class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
    {#if showCreatives}
      <div class="text-sm text-gray-600 dark:text-gray-400">
        Creative management interface would go here
      </div>
    {/if}
  </div>

  <!-- Campaign Journey Section -->
  <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Campaign Journey</h3>
    <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
      Describe your campaign to generate journey steps
    </p>
    <textarea
      bind:value={formData.journeyDescription}
      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
      rows="3"
      placeholder="Enter campaign description to generate journey steps..."
    ></textarea>
    <button class="mt-2 px-4 py-2 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors">
      Edit
    </button>
  </div>

  <!-- Control Group Section -->
  <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Control Group</h3>
      <button
        on:click={() => showControlGroup = !showControlGroup}
        class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
    </div>
    {#if showControlGroup}
      <div class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        Control group configuration would go here
      </div>
    {/if}
  </div>

  <!-- Action Buttons -->
  <div class="flex gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
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