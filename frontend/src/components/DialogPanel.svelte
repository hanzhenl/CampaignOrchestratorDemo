<script lang="ts">
  import { currentSession } from '../stores';
  import { afterUpdate } from 'svelte';
  import MarkdownRenderer from './MarkdownRenderer.svelte';

  let expandedReasoning: Set<string> = new Set();
  let scrollContainer: HTMLDivElement;
  let previousMessageCount = 0;

  // Helper function to format ISO timestamp to time-only format (e.g., "9:23 PM")
  function formatTimeOnly(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    } catch (e) {
      return '';
    }
  }

  // Auto-scroll to bottom when new messages are added or updated
  afterUpdate(() => {
    if (scrollContainer && $currentSession) {
      const currentMessageCount = $currentSession.messages.length;
      const hasThinkingMessage = $currentSession.messages.some(msg => msg.isThinking);
      
      // Scroll if message count changed or if there's a thinking message (content updates)
      if (currentMessageCount !== previousMessageCount || hasThinkingMessage) {
        // Use requestAnimationFrame to ensure DOM has updated
        requestAnimationFrame(() => {
          if (scrollContainer) {
            scrollContainer.scrollTop = scrollContainer.scrollHeight;
          }
        });
        previousMessageCount = currentMessageCount;
      }
    } else if (!$currentSession) {
      previousMessageCount = 0;
    }
  });
</script>

<div class="h-full bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 flex flex-col">
  <div class="p-4 border-b border-gray-200 dark:border-gray-700">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Dialog</h3>
  </div>
  <div bind:this={scrollContainer} class="flex-1 overflow-y-auto p-4 space-y-4">
    {#if $currentSession}
      {#each $currentSession.messages as message}
        <div class="flex {message.role === 'user' ? 'justify-end' : 'justify-start'}">
          <div class="group max-w-[80%] {message.role === 'user' ? 'bg-blue-600 text-white' : message.isThinking ? 'bg-gray-50 dark:bg-gray-800 text-gray-500 dark:text-gray-400' : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'} rounded-lg p-3 {message.isThinking ? 'italic' : ''}">
            <div class="flex items-center gap-2 text-sm font-semibold mb-1">
              {#if message.role === 'user'}
                <!-- User icon -->
                <svg
                  class="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              {:else}
                <!-- Assistant icon (sparkles/bot) -->
                <svg
                  class="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
                  />
                </svg>
              {/if}
              <span>{message.role === 'user' ? 'You' : 'Assistant'}</span>
            </div>
            {#if message.isThinking}
              <div class="flex items-center gap-2">
                <div class="whitespace-pre-wrap">{message.content}</div>
                <div class="flex gap-1">
                  <div class="w-1 h-1 bg-gray-400 dark:bg-gray-500 rounded-full animate-pulse" style="animation-delay: 0s"></div>
                  <div class="w-1 h-1 bg-gray-400 dark:bg-gray-500 rounded-full animate-pulse" style="animation-delay: 0.2s"></div>
                  <div class="w-1 h-1 bg-gray-400 dark:bg-gray-500 rounded-full animate-pulse" style="animation-delay: 0.4s"></div>
                </div>
              </div>
            {:else}
              {#if message.role === 'assistant'}
                <MarkdownRenderer content={message.content} />
              {:else}
                <div class="whitespace-pre-wrap">{message.content}</div>
              {/if}
            {/if}
            
            {#if message.reasoningSteps && message.reasoningSteps.length > 0}
              <button
                on:click={() => {
                  if (expandedReasoning.has(message.id)) {
                    expandedReasoning.delete(message.id);
                  } else {
                    expandedReasoning.add(message.id);
                  }
                  expandedReasoning = expandedReasoning;
                }}
                class="mt-2 text-xs underline"
              >
                {expandedReasoning.has(message.id) ? 'Hide' : 'Show'} Reasoning
              </button>
              {#if expandedReasoning.has(message.id)}
                <div class="mt-2 pt-2 border-t border-gray-300 dark:border-gray-600">
                  {#each message.reasoningSteps as step}
                    <div class="text-xs mb-1">
                      <span class="font-semibold">{step.step}:</span> {step.result}
                    </div>
                  {/each}
                </div>
              {/if}
            {/if}
            
            <!-- Footer with timestamp and action icons -->
            <div class="flex items-center justify-between mt-2 pt-2 border-t {message.role === 'user' ? 'border-blue-500/30' : 'border-gray-300 dark:border-gray-600'}">
              <!-- Timestamp on left -->
              <div class="text-xs {message.role === 'user' ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'}">
                {formatTimeOnly(message.timestamp)}
              </div>
              
              <!-- Action icons on right (visible on hover) -->
              <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <!-- Debug icon (gear) -->
                <button
                  class="p-1 {message.role === 'user' ? 'text-blue-100 hover:text-white' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'} transition-colors"
                  aria-label="Debug"
                  title="Debug"
                >
                  <svg
                    class="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                  </svg>
                </button>
                
                <!-- Bookmark icon -->
                <button
                  class="p-1 {message.role === 'user' ? 'text-blue-100 hover:text-white' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'} transition-colors"
                  aria-label="Bookmark"
                  title="Bookmark"
                >
                  <svg
                    class="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
                    />
                  </svg>
                </button>
                
                <!-- Quote icon (chat bubble) -->
                <button
                  class="p-1 {message.role === 'user' ? 'text-blue-100 hover:text-white' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'} transition-colors"
                  aria-label="Quote"
                  title="Quote"
                >
                  <svg
                    class="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      {/each}
    {:else}
      <div class="text-center text-gray-500 dark:text-gray-400 py-8">
        <ul class="list-none space-y-2 text-left inline-block">
          <li>• Generate a new campaign on...</li>
          <li>• Compare audience segments to...</li>
          <li>• Recommend a knowledge article for...</li>
        </ul>
      </div>
    {/if}
  </div>
</div>
