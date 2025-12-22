<script lang="ts">
  import { currentSession } from '../stores';

  let expandedReasoning: Set<string> = new Set();
</script>

<div class="h-full bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 flex flex-col">
  <div class="p-4 border-b border-gray-200 dark:border-gray-700">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Dialog</h3>
  </div>
  <div class="flex-1 overflow-y-auto p-4 space-y-4">
    {#if $currentSession}
      {#each $currentSession.messages as message}
        <div class="flex {message.role === 'user' ? 'justify-end' : 'justify-start'}">
          <div class="max-w-[80%] {message.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'} rounded-lg p-3">
            <div class="text-sm font-semibold mb-1">
              {message.role === 'user' ? 'You' : 'Assistant'}
            </div>
            <div class="whitespace-pre-wrap">{message.content}</div>
            
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
          </div>
        </div>
      {/each}
    {:else}
      <div class="text-center text-gray-500 dark:text-gray-400 py-8">
        No active dialog session. Start a conversation to begin.
      </div>
    {/if}
  </div>
</div>
