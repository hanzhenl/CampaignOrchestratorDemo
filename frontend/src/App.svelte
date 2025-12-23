<script lang="ts">
  import ActionBar from "./components/ActionBar.svelte";
  import AgentCanvas from "./components/AgentCanvas.svelte";
  import { currentSession, experiencePanelData } from "./stores";

  // Determine if we're on the homepage
  $: isHomepage = !$currentSession && !$experiencePanelData;
</script>

<div class="h-screen flex flex-col dark bg-gray-900">
  <AgentCanvas />
  {#if !isHomepage}
    <ActionBar />
  {/if}
</div>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
      Ubuntu, Cantarell, sans-serif;
  }
</style>
