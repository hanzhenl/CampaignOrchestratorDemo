<script lang="ts">
  export let data: any;
</script>

<div class="space-y-4">
  <div>
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{data.title || data.name}</h2>
    <p class="text-gray-600 dark:text-gray-400">{data.description}</p>
  </div>
  
  <div class="grid grid-cols-2 gap-4">
    <div>
      <div class="text-sm text-gray-500 dark:text-gray-400">Type</div>
      <div class="text-lg font-semibold text-gray-900 dark:text-white">Segment</div>
    </div>
    <div>
      <div class="text-sm text-gray-500 dark:text-gray-400">ID</div>
      <div class="text-lg font-semibold text-gray-900 dark:text-white">{data.id}</div>
    </div>
  </div>
</div>
