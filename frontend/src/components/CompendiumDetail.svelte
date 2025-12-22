<script lang="ts">
  export let data: any;
</script>

<div class="space-y-4">
  <div>
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{data.title}</h2>
  </div>
  
  <div class="prose dark:prose-invert max-w-none">
    <p class="text-gray-700 dark:text-gray-300">{data.content || data.description}</p>
  </div>
</div>
