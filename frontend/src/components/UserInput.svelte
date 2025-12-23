<script lang="ts">
  import {
    searchResults,
    currentSession,
    experiencePanelData,
    experiencePanelType,
    selectedKnowledge,
  } from "../stores";
  import KnowledgeSelectionModal from "./KnowledgeSelectionModal.svelte";

  let inputValue = "";
  let showSearchResults = false;
  let searchTimeout: number | null = null;
  let showKnowledgeModal = false;

  // Determine if we're on the homepage
  $: isHomepage = !$currentSession && !$experiencePanelData;

  async function handleInput() {
    if (searchTimeout) clearTimeout(searchTimeout);

    if (inputValue.length < 3) {
      showSearchResults = false;
      return;
    }

    // Short queries trigger search
    if (inputValue.length < 10) {
      searchTimeout = setTimeout(async () => {
        const response = await fetch(
          `/api/v1/search?q=${encodeURIComponent(inputValue)}&type=all`
        );
        const results = await response.json();
        searchResults.set(results);
        showSearchResults = results.length > 0;
      }, 300);
    } else {
      showSearchResults = false;
    }
  }

  async function handleSubmit() {
    if (!inputValue.trim()) return;

    // When user explicitly submits (button click or Enter), always send to agent
    // Search-as-you-type is handled separately in handleInput()

    const promptText = inputValue.trim();
    inputValue = ""; // Clear input immediately for better UX

    // Long queries trigger AI agent
    // Get current session ID using reactive statement
    let sessionId: string | null = $currentSession?.id || null;

    if (!sessionId) {
      // Create new session
      try {
        const response = await fetch("/api/v1/dialog/sessions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title: promptText.substring(0, 50) }),
        });
        const newSession = await response.json();
        sessionId = newSession.id;
        currentSession.set(newSession);
        // Reset selected knowledge when starting a new session
        selectedKnowledge.set([]);
      } catch (error) {
        console.error("Error creating session:", error);
        throw error;
      }
    }

    // Step 1: Add user message immediately via API
    try {
      const userMessageResponse = await fetch(
        `/api/v1/dialog/sessions/${sessionId}/messages`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            role: "user",
            content: promptText,
          }),
        }
      );
      const userMessage = await userMessageResponse.json();

      // Update local state with user message
      const current = $currentSession;
      if (current) {
        currentSession.set({
          ...current,
          messages: [...current.messages, userMessage],
        });
      }
    } catch (error) {
      console.error("Error adding user message:", error);
      // Continue anyway - we'll sync from backend later
    }

    // Step 2: Add thinking message to local state
    const thinkingMessageId = `thinking-${Date.now()}`;
    const thinkingMessage = {
      id: thinkingMessageId,
      role: "assistant" as const,
      content: "Thinking...",
      timestamp: new Date().toISOString(),
      isThinking: true,
    };

    const current = $currentSession;
    if (current) {
      currentSession.set({
        ...current,
        messages: [...current.messages, thinkingMessage],
      });
    }

    // Step 3: Send to agent orchestrator asynchronously
    // #region agent log
    fetch("http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        location: "UserInput.svelte:orchestrate_start",
        message: "Starting orchestration",
        data: {
          promptText,
          sessionId,
        },
        timestamp: Date.now(),
        sessionId: "debug-session",
        runId: "run1",
        hypothesisId: "Q",
      }),
    }).catch(() => {});
    // #endregion

    // Prepare knowledge articles for context
    const knowledgeArticles = $selectedKnowledge.map((article) => ({
      id: article.id,
      title: article.title,
      content: article.content,
    }));

    fetch("/api/v1/agent/orchestrate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: promptText,
        sessionId: sessionId,
        knowledgeArticles: knowledgeArticles,
      }),
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`Orchestration failed: ${response.statusText}`);
        }
        const result = await response.json();

        // #region agent log
        fetch(
          "http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              location: "UserInput.svelte:orchestrate_response_received",
              message: "Received orchestration response",
              data: {
                experiencePanelType: result.experiencePanelType,
                hasCampaignConfig: !!result.campaignConfig,
                hasChart: !!result.campaignConfig?.chart,
                campaignConfigKeys: result.campaignConfig
                  ? Object.keys(result.campaignConfig)
                  : null,
                hasUiComponents: !!result.campaignConfig?.uiComponents,
                uiComponentsLength:
                  result.campaignConfig?.uiComponents?.length || 0,
              },
              timestamp: Date.now(),
              sessionId: "debug-session",
              runId: "run1",
              hypothesisId: "F",
            }),
          }
        ).catch(() => {});
        // #endregion

        // Update experience panel
        const configData = result.campaignConfig || result;

        // #region agent log
        fetch(
          "http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              location: "UserInput.svelte:before_set_store",
              message: "About to set experience panel data",
              data: {
                hasCampaignConfig: !!result.campaignConfig,
                hasUiComponents: !!result.campaignConfig?.uiComponents,
                uiComponentsCount:
                  result.campaignConfig?.uiComponents?.length || 0,
                primaryComponent: result.campaignConfig?.primaryComponent,
                configDataKeys: configData ? Object.keys(configData) : null,
                configDataHasUiComponents: !!configData?.uiComponents,
                configDataUiComponentsCount:
                  configData?.uiComponents?.length || 0,
              },
              timestamp: Date.now(),
              sessionId: "debug-session",
              runId: "run1",
              hypothesisId: "A",
            }),
          }
        ).catch(() => {});
        // #endregion

        experiencePanelData.set(configData);
        experiencePanelType.set(result.experiencePanelType || "default");

        // #region agent log
        fetch(
          "http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              location: "UserInput.svelte:after_set_store",
              message: "After setting experience panel data",
              data: {
                experiencePanelType: result.experiencePanelType || "default",
              },
              timestamp: Date.now(),
              sessionId: "debug-session",
              runId: "run1",
              hypothesisId: "A",
            }),
          }
        ).catch(() => {});
        // #endregion

        // #region agent log
        fetch(
          "http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              location: "UserInput.svelte:set_store",
              message: "Setting experience panel store",
              data: {
                experiencePanelType: result.experiencePanelType || "default",
                hasConfigData: !!configData,
                configDataKeys: configData ? Object.keys(configData) : null,
                hasUiComponents: !!configData?.uiComponents,
                uiComponentsLength: configData?.uiComponents?.length || 0,
                hasRecommendations: !!configData?.recommendations,
                hasChart: !!configData?.chart,
              },
              timestamp: Date.now(),
              sessionId: "debug-session",
              runId: "run1",
              hypothesisId: "M",
            }),
          }
        ).catch(() => {});
        // #endregion

        // Refresh session to get updated messages (this will replace thinking message)
        const sessionResponse = await fetch(
          `/api/v1/dialog/sessions/${sessionId}`
        );
        const updatedSession = await sessionResponse.json();
        currentSession.set(updatedSession);
      })
      .catch((error) => {
        console.error("Error submitting prompt:", error);

        // Replace thinking message with error message
        const current = $currentSession;
        if (current) {
          const updatedMessages = current.messages.map((msg) =>
            msg.id === thinkingMessageId
              ? {
                  ...msg,
                  content: `Error: ${error.message || "Failed to process request"}`,
                  isThinking: false,
                }
              : msg
          );
          currentSession.set({
            ...current,
            messages: updatedMessages,
          });
        }
      });
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  function selectSearchResult(result: any) {
    experiencePanelData.set(result);
    experiencePanelType.set(result.type);
    showSearchResults = false;
    inputValue = "";
  }

  function startNewSession() {
    // Clear all state to start a new session
    currentSession.set(null);
    experiencePanelData.set(null);
    experiencePanelType.set(null);
    selectedKnowledge.set([]);
    searchResults.set([]);
    inputValue = "";
    showSearchResults = false;
  }
</script>

<div class="relative w-full">
  <!-- Knowledge Badges -->
  {#if $selectedKnowledge.length > 0}
    <div class="flex flex-wrap gap-2 mb-2">
      {#each $selectedKnowledge as article}
        <span
          class="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm"
        >
          <span>{article.title}</span>
          <button
            on:click={() => {
              selectedKnowledge.set(
                $selectedKnowledge.filter((a) => a.id !== article.id)
              );
            }}
            class="hover:text-blue-600 dark:hover:text-blue-400"
            aria-label="Remove {article.title}"
          >
            ×
          </button>
        </span>
      {/each}
    </div>
  {/if}

  <div
    class="relative flex items-center bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 rounded-lg shadow-sm"
  >
    <!-- Left Icons -->
    <div class="flex items-center gap-2 px-4">
      <button
        on:click={() => (showKnowledgeModal = true)}
        class="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        title="Add Knowledge"
      >
        <svg
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 4v16m8-8H4"
          />
        </svg>
      </button>
      <button
        class="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        title="Attach"
      >
        <svg
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
          />
        </svg>
      </button>
      <button
        on:click={startNewSession}
        class="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        title="Start New Session"
      >
        <svg
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
      </button>
    </div>

    <!-- Input Field -->
    <input
      type="text"
      bind:value={inputValue}
      on:input={handleInput}
      on:keydown={handleKeydown}
      placeholder="What are we launching today?"
      class="flex-1 px-4 py-3 bg-transparent border-0 focus:outline-none text-gray-900 dark:text-white placeholder-gray-400"
    />

    <!-- Send Icon -->
    <button
      on:click={handleSubmit}
      class="p-2 mr-2 text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
      title="Send"
    >
      <svg
        class="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
        />
      </svg>
    </button>
  </div>

  {#if showSearchResults}
    <div
      class="absolute z-50 w-full {isHomepage
        ? 'top-full mt-2'
        : 'bottom-full mb-2'} bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-64 overflow-y-auto"
    >
      {#each $searchResults as result}
        <button
          on:click={() => selectSearchResult(result)}
          class="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          <div class="font-semibold text-gray-900 dark:text-white">
            {result.title}
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-400">
            {result.type} • {result.description}
          </div>
        </button>
      {/each}
    </div>
  {/if}

  <!-- Knowledge Selection Modal -->
  <KnowledgeSelectionModal
    isOpen={showKnowledgeModal}
    onClose={() => (showKnowledgeModal = false)}
  />
</div>
