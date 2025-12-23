<script lang="ts">
  import { marked } from 'marked';
  import { onMount, afterUpdate } from 'svelte';
  import { experiencePanelData, experiencePanelType } from '../stores';

  export let content: string;

  let container: HTMLDivElement;

  // Configure marked options once
  marked.setOptions({
    breaks: true, // Convert line breaks to <br>
    gfm: true, // GitHub Flavored Markdown
  });

  // Parse markdown to HTML reactively
  $: htmlContent = content ? (marked.parse(content) as string) : '';

  // Handle grounding link clicks
  async function handleGroundingClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    const link = target.closest('a[href^="grounding://"]') as HTMLAnchorElement;
    
    if (!link) return;
    
    event.preventDefault();
    event.stopPropagation();
    
    const href = link.getAttribute('href');
    if (!href) return;
    
    // Parse grounding://campaign/camp-001 or grounding://segment/seg-001
    const match = href.match(/^grounding:\/\/(campaign|segment)\/(.+)$/);
    if (!match) return;
    
    const [, type, id] = match;
    
    try {
      if (type === 'campaign') {
        const response = await fetch(`/api/v1/campaigns/${id}`);
        if (!response.ok) throw new Error('Campaign not found');
        const campaign = await response.json();
        
        // Update experience panel with campaign data using uiComponents format
        experiencePanelData.set({
          uiComponents: [{
            type: 'campaign',
            data: campaign
          }],
          primaryComponent: 'campaign'
        });
        experiencePanelType.set('campaign');
      } else if (type === 'segment') {
        // For segments, we need to fetch from the list
        const response = await fetch('/api/v1/segments');
        if (!response.ok) throw new Error('Segments not found');
        const segments = await response.json();
        const segment = segments.find((s: any) => s.id === id);
        
        if (!segment) throw new Error('Segment not found');
        
        // Update experience panel with segment data using uiComponents format
        experiencePanelData.set({
          uiComponents: [{
            type: 'segment',
            data: segment
          }],
          primaryComponent: 'segment'
        });
        experiencePanelType.set('segment');
      }
    } catch (error) {
      console.error('Error fetching grounding reference:', error);
      // Could show a toast/notification here in the future
    }
  }

  // Attach click listeners after content updates
  afterUpdate(() => {
    if (container) {
      const links = container.querySelectorAll('a[href^="grounding://"]');
      links.forEach(link => {
        // Remove existing listener if any (to avoid duplicates)
        const existingLink = link as HTMLElement & { _groundingHandler?: (e: MouseEvent) => void };
        if (existingLink._groundingHandler) {
          link.removeEventListener('click', existingLink._groundingHandler);
        }
        
        // Add new listener and store reference
        existingLink._groundingHandler = handleGroundingClick;
        link.addEventListener('click', handleGroundingClick);
        
        // Add cursor pointer style
        (link as HTMLElement).style.cursor = 'pointer';
      });
    }
  });
</script>

<div bind:this={container} class="markdown-content prose prose-sm dark:prose-invert max-w-none">
  {@html htmlContent}
</div>

<style>
  :global(.markdown-content) {
    /* Links */
    :global(a) {
      @apply text-blue-600 dark:text-blue-400 underline hover:text-blue-800 dark:hover:text-blue-300;
    }

    /* Inline code */
    :global(code:not(pre code)) {
      @apply bg-gray-200 dark:bg-gray-600 text-gray-900 dark:text-gray-100 px-1.5 py-0.5 rounded text-sm font-mono;
    }

    /* Code blocks */
    :global(pre) {
      @apply bg-gray-200 dark:bg-gray-600 text-gray-900 dark:text-gray-100 p-3 rounded overflow-x-auto my-2;
    }

    :global(pre code) {
      @apply bg-transparent p-0;
    }

    /* Lists */
    :global(ul, ol) {
      @apply my-2 ml-4;
    }

    :global(ul) {
      @apply list-disc;
    }

    :global(ol) {
      @apply list-decimal;
    }

    :global(li) {
      @apply my-1;
    }

    /* Bold and italic */
    :global(strong) {
      @apply font-semibold;
    }

    :global(em) {
      @apply italic;
    }

    /* Paragraphs */
    :global(p) {
      @apply my-2;
    }

    :global(p:first-child) {
      @apply mt-0;
    }

    :global(p:last-child) {
      @apply mb-0;
    }

    /* Headers (if any appear) */
    :global(h1, h2, h3, h4, h5, h6) {
      @apply font-semibold mt-4 mb-2;
    }

    :global(h1) {
      @apply text-lg;
    }

    :global(h2) {
      @apply text-base;
    }

    :global(h3) {
      @apply text-sm;
    }

    /* Blockquotes */
    :global(blockquote) {
      @apply border-l-4 border-gray-300 dark:border-gray-600 pl-4 my-2 italic;
    }

    /* Horizontal rules */
    :global(hr) {
      @apply border-gray-300 dark:border-gray-600 my-4;
    }
  }
</style>

