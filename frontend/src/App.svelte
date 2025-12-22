<script lang="ts">
  import ActionBar from './components/ActionBar.svelte';
  import AgentCanvas from './components/AgentCanvas.svelte';
  import { currentSession, searchResults, experiencePanelData } from './stores';

  let darkMode = true;
</script>

<div class="h-screen flex flex-col dark bg-gray-900">
  <ActionBar />
  <AgentCanvas />
</div>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  }
</style>
