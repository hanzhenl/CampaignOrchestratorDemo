<script lang="ts">
  export let data: any;

  function formatDate(dateString: string): string {
    if (!dateString) return "N/A";
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch {
      return dateString;
    }
  }

  function formatPercentage(value: number): string {
    if (value === undefined || value === null) return "N/A";
    return `${(value * 100).toFixed(1)}%`;
  }

  function formatNumber(value: number): string {
    if (value === undefined || value === null) return "N/A";
    return value.toLocaleString();
  }
</script>

<div class="space-y-4">
  <div>
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
      {data.title || data.name}
    </h2>
    <p class="text-gray-600 dark:text-gray-400">{data.description}</p>
  </div>

  <div class="grid grid-cols-2 gap-4">
    <div>
      <div class="text-sm text-gray-500 dark:text-gray-400">Type</div>
      <div class="text-lg font-semibold text-gray-900 dark:text-white">
        Segment
      </div>
    </div>
    <div>
      <div class="text-sm text-gray-500 dark:text-gray-400">ID</div>
      <div class="text-lg font-semibold text-gray-900 dark:text-white">
        {data.id}
      </div>
    </div>
    {#if data.size !== undefined}
      <div>
        <div class="text-sm text-gray-500 dark:text-gray-400">Size</div>
        <div class="text-lg font-semibold text-gray-900 dark:text-white">
          {formatNumber(data.size)}
        </div>
      </div>
    {/if}
    {#if data.pastConversionRate !== undefined}
      <div>
        <div class="text-sm text-gray-500 dark:text-gray-400">
          Past Conversion Rate
        </div>
        <div class="text-lg font-semibold text-gray-900 dark:text-white">
          {formatPercentage(data.pastConversionRate)}
        </div>
      </div>
    {/if}
  </div>

  {#if data.demographics && Object.keys(data.demographics).length > 0}
    <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        Demographics
      </h3>
      <div class="grid grid-cols-2 gap-4">
        {#if data.demographics.age}
          <div>
            <div class="text-sm text-gray-500 dark:text-gray-400">Age</div>
            <div class="text-base text-gray-900 dark:text-white">
              {data.demographics.age}
            </div>
          </div>
        {/if}
        {#if data.demographics.location}
          <div>
            <div class="text-sm text-gray-500 dark:text-gray-400">Location</div>
            <div class="text-base text-gray-900 dark:text-white">
              {data.demographics.location}
            </div>
          </div>
        {/if}
      </div>
    </div>
  {/if}

  {#if data.behaviors && Object.keys(data.behaviors).length > 0}
    <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        Behaviors
      </h3>
      <div class="grid grid-cols-2 gap-4">
        {#if data.behaviors.engagement}
          <div>
            <div class="text-sm text-gray-500 dark:text-gray-400">
              Engagement
            </div>
            <div class="text-base text-gray-900 dark:text-white capitalize">
              {data.behaviors.engagement.replace("_", " ")}
            </div>
          </div>
        {/if}
        {#if data.behaviors.purchaseFrequency}
          <div>
            <div class="text-sm text-gray-500 dark:text-gray-400">
              Purchase Frequency
            </div>
            <div class="text-base text-gray-900 dark:text-white capitalize">
              {data.behaviors.purchaseFrequency.replace("_", " ")}
            </div>
          </div>
        {/if}
      </div>
    </div>
  {/if}

  {#if data.createdAt}
    <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
      <div class="text-sm text-gray-500 dark:text-gray-400">Created At</div>
      <div class="text-base text-gray-900 dark:text-white">
        {formatDate(data.createdAt)}
      </div>
    </div>
  {/if}
</div>
