<script lang="ts">
  import DialogPanel from './DialogPanel.svelte';
  import ExperiencePanel from './ExperiencePanel.svelte';
  import EmptyState from './EmptyState.svelte';
  import { currentSession, experiencePanelData } from '../stores';

  let dialogMinimized = false;
  let experienceMinimized = false;
</script>

<div class="flex-1 flex gap-4 p-4 overflow-hidden">
  {#if !$currentSession && !$experiencePanelData}
    <EmptyState />
  {:else}
    {#if !dialogMinimized}
      <div class="flex-1 {experienceMinimized ? 'w-full' : 'w-1/2'}">
        <DialogPanel />
      </div>
    {/if}
    {#if !experienceMinimized}
      <div class="flex-1 {dialogMinimized ? 'w-full' : 'w-1/2'}">
        <ExperiencePanel />
      </div>
    {/if}
  {/if}
</div>
