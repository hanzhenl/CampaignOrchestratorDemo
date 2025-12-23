<script lang="ts">
  import { experiencePanelData, experiencePanelType } from "../stores";
  import CampaignForm from "./CampaignForm.svelte";
  import CampaignDetail from "./CampaignDetail.svelte";
  import CampaignList from "./CampaignList.svelte";
  import SegmentDetail from "./SegmentDetail.svelte";
  import SegmentList from "./SegmentList.svelte";
  import KnowledgeDetail from "./KnowledgeDetail.svelte";
  import KnowledgeList from "./KnowledgeList.svelte";
  import Chart from "./Chart.svelte";
  import RecommendationCards from "./RecommendationCards.svelte";

  // Helper to get component type and data
  function getComponentInfo() {
    const data = $experiencePanelData;
    const type = $experiencePanelType;

    // #region agent log
    fetch("http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        location: "ExperiencePanel.svelte:getComponentInfo:entry",
        message: "getComponentInfo called",
        data: {
          hasData: !!data,
          dataType: data ? typeof data : "null",
          hasUiComponents: !!data?.uiComponents,
          uiComponentsIsArray: Array.isArray(data?.uiComponents),
          uiComponentsLength: data?.uiComponents?.length || 0,
          primaryComponent: data?.primaryComponent,
          experiencePanelType: type,
        },
        timestamp: Date.now(),
        sessionId: "debug-session",
        runId: "run1",
        hypothesisId: "D",
      }),
    }).catch(() => {});
    // #endregion

    if (!data) {
      // #region agent log
      fetch(
        "http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            location: "ExperiencePanel.svelte:getComponentInfo:no_data",
            message: "No data, returning null",
            data: {},
            timestamp: Date.now(),
            sessionId: "debug-session",
            runId: "run1",
            hypothesisId: "D",
          }),
        }
      ).catch(() => {});
      // #endregion
      return null;
    }

    // Check for new uiComponents array format (preferred)
    if (
      data.uiComponents &&
      Array.isArray(data.uiComponents) &&
      data.uiComponents.length > 0
    ) {
      const primaryComponent =
        data.primaryComponent || data.uiComponents[0].type;

      // #region agent log
      fetch(
        "http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            location:
              "ExperiencePanel.svelte:getComponentInfo:uiComponents_found",
            message: "Found uiComponents array",
            data: {
              primaryComponent,
              uiComponentsTypes: data.uiComponents.map((c: any) => c.type),
              uiComponentsWithData: data.uiComponents.map((c: any) => ({
                type: c.type,
                hasData: c.data !== undefined,
              })),
            },
            timestamp: Date.now(),
            sessionId: "debug-session",
            runId: "run1",
            hypothesisId: "B",
          }),
        }
      ).catch(() => {});
      // #endregion

      const component =
        data.uiComponents.find((c: any) => c.type === primaryComponent) ||
        data.uiComponents[0];

      // #region agent log
      fetch(
        "http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            location: "ExperiencePanel.svelte:getComponentInfo:component_found",
            message: "Component found",
            data: {
              componentType: component?.type,
              componentHasData: component?.data !== undefined,
              componentDataType: component?.data
                ? typeof component.data
                : "undefined",
              componentDataIsString: typeof component?.data === "string",
              componentDataStringValue:
                typeof component?.data === "string"
                  ? component.data.substring(0, 100)
                  : null,
              componentDataKeys:
                component?.data && typeof component.data === "object"
                  ? Object.keys(component.data)
                  : null,
              componentDataFull: component?.data
                ? JSON.stringify(component.data).substring(0, 200)
                : null,
            },
            timestamp: Date.now(),
            sessionId: "debug-session",
            runId: "run1",
            hypothesisId: "B",
          }),
        }
      ).catch(() => {});
      // #endregion

      if (component && component.data !== undefined) {
        // Handle case where component.data might be a string (should be object)
        let componentData = component.data;
        if (typeof component.data === "string") {
          try {
            componentData = JSON.parse(component.data);
          } catch (e) {
            // If parsing fails, use empty object
            console.warn(
              `Component ${component.type} has string data that couldn't be parsed:`,
              component.data
            );
            componentData = {};
          }
        }

        // #region agent log
        fetch(
          "http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              location:
                "ExperiencePanel.svelte:getComponentInfo:returning_component",
              message: "Returning component with data",
              data: {
                componentType: component.type,
                originalDataType: typeof component.data,
                parsedDataType: typeof componentData,
                hasItems: !!componentData?.items,
                itemsCount: componentData?.items?.length || 0,
              },
              timestamp: Date.now(),
              sessionId: "debug-session",
              runId: "run1",
              hypothesisId: "B",
            }),
          }
        ).catch(() => {});
        // #endregion
        return {
          componentType: component.type,
          componentData: componentData,
          allComponents: data.uiComponents,
        };
      } else if (component) {
        // Component exists but data is undefined - use empty object
        console.warn(
          `Component ${component.type} has no data, using empty object`
        );
        // #region agent log
        fetch(
          "http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              location:
                "ExperiencePanel.svelte:getComponentInfo:component_no_data",
              message: "Component has no data, using empty object",
              data: { componentType: component.type },
              timestamp: Date.now(),
              sessionId: "debug-session",
              runId: "run1",
              hypothesisId: "B",
            }),
          }
        ).catch(() => {});
        // #endregion
        return {
          componentType: component.type,
          componentData: {},
          allComponents: data.uiComponents,
        };
      }
    }

    // Fallback to legacy format
    // Check for individual component data
    if (data.recommendations) {
      return {
        componentType: "recommendations",
        componentData: data.recommendations,
      };
    }

    if (data.chart) {
      return {
        componentType: "chart",
        componentData: data.chart,
      };
    }

    // Use experiencePanelType
    if (type) {
      // #region agent log
      fetch(
        "http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            location: "ExperiencePanel.svelte:getComponentInfo:using_type",
            message: "Using experiencePanelType fallback",
            data: { type },
            timestamp: Date.now(),
            sessionId: "debug-session",
            runId: "run1",
            hypothesisId: "D",
          }),
        }
      ).catch(() => {});
      // #endregion
      return {
        componentType: type,
        componentData: data,
      };
    }

    // #region agent log
    fetch("http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        location: "ExperiencePanel.svelte:getComponentInfo:returning_null",
        message: "Returning null - no component found",
        data: {
          hasData: !!data,
          hasUiComponents: !!data?.uiComponents,
          hasRecommendations: !!data?.recommendations,
          hasChart: !!data?.chart,
          hasType: !!type,
        },
        timestamp: Date.now(),
        sessionId: "debug-session",
        runId: "run1",
        hypothesisId: "D",
      }),
    }).catch(() => {});
    // #endregion
    return null;
  }

  // Declare componentInfo variable
  let componentInfo: any = null;

  // Reactive statement that re-runs when store changes
  $: {
    // #region agent log
    fetch("http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        location: "ExperiencePanel.svelte:reactive_statement",
        message: "Reactive statement triggered",
        data: {
          hasData: !!$experiencePanelData,
          hasType: !!$experiencePanelType,
        },
        timestamp: Date.now(),
        sessionId: "debug-session",
        runId: "run1",
        hypothesisId: "D",
      }),
    }).catch(() => {});
    // #endregion
    componentInfo = getComponentInfo();

    // #region agent log
    fetch("http://127.0.0.1:7242/ingest/dbf0cb9b-da32-4af5-b7e9-55bd2da93dad", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        location: "ExperiencePanel.svelte:reactive_after_call",
        message: "After getComponentInfo call",
        data: {
          hasComponentInfo: !!componentInfo,
          componentType: componentInfo?.componentType || null,
          hasComponentData: !!componentInfo?.componentData,
        },
        timestamp: Date.now(),
        sessionId: "debug-session",
        runId: "run1",
        hypothesisId: "D",
      }),
    }).catch(() => {});
    // #endregion
  }
</script>

<div
  class="h-full bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 flex flex-col"
>
  <div class="p-4 border-b border-gray-200 dark:border-gray-700">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
      Experience Panel
    </h3>
  </div>
  <div class="flex-1 overflow-y-auto p-4">
    {#if $experiencePanelData && componentInfo}
      {#if componentInfo.componentType === "recommendations"}
        <RecommendationCards
          items={componentInfo.componentData.items || []}
          type={componentInfo.componentData.type || "mixed"}
          title={componentInfo.componentData.title}
          description={componentInfo.componentData.description}
        />
      {:else if componentInfo.componentType === "chart"}
        <Chart data={componentInfo.componentData} />
      {:else if componentInfo.componentType === "campaign_list"}
        <CampaignList
          items={componentInfo.componentData.items ||
            componentInfo.componentData ||
            []}
        />
      {:else if componentInfo.componentType === "segment_list"}
        <SegmentList
          items={componentInfo.componentData.items ||
            componentInfo.componentData ||
            []}
        />
      {:else if componentInfo.componentType === "knowledge_list"}
        <KnowledgeList
          items={componentInfo.componentData.items ||
            componentInfo.componentData ||
            []}
        />
      {:else if componentInfo.componentType === "campaign_form"}
        <!-- CampaignForm uses store directly, no prop needed -->
        <CampaignForm />
      {:else if componentInfo.componentType === "campaign"}
        <CampaignDetail data={componentInfo.componentData} />
      {:else if componentInfo.componentType === "segment"}
        <SegmentDetail data={componentInfo.componentData} />
      {:else if componentInfo.componentType === "knowledge"}
        <KnowledgeDetail data={componentInfo.componentData} />
      {:else if componentInfo.componentType === "research_analysis"}
        <!-- Display research analysis - could show rationale, analysis summary, etc. -->
        <div class="space-y-4">
          {#if componentInfo.componentData?.rationale}
            <div class="prose dark:prose-invert max-w-none">
              <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                {componentInfo.componentData.rationale}
              </p>
            </div>
          {/if}
          {#if componentInfo.componentData?.analysis}
            <div class="space-y-2">
              <h4 class="font-semibold text-gray-900 dark:text-white">
                Analysis
              </h4>
              <div class="text-sm text-gray-600 dark:text-gray-400">
                <pre class="whitespace-pre-wrap">{JSON.stringify(
                    componentInfo.componentData.analysis,
                    null,
                    2
                  )}</pre>
              </div>
            </div>
          {/if}
          {#if !componentInfo.componentData?.rationale && !componentInfo.componentData?.analysis}
            <div class="text-center text-gray-500 dark:text-gray-400 py-8">
              Research analysis completed
            </div>
          {/if}
        </div>
      {:else}
        <!-- Unknown component type, show empty state -->
        <div class="text-center text-gray-500 dark:text-gray-400 py-8">
          Unknown component type: {componentInfo.componentType}
        </div>
      {/if}
    {:else if $experiencePanelData}
      <!-- Legacy fallback when componentInfo is null -->
      {#if $experiencePanelType === "campaign_list"}
        <CampaignList items={$experiencePanelData.items || []} />
      {:else if $experiencePanelType === "segment_list"}
        <SegmentList items={$experiencePanelData.items || []} />
      {:else if $experiencePanelType === "knowledge_list"}
        <KnowledgeList items={$experiencePanelData.items || []} />
      {:else if $experiencePanelType === "campaign_form" || ($experiencePanelData && $experiencePanelData.name && !$experiencePanelType)}
        <!-- CampaignForm uses store directly, no prop needed -->
        <CampaignForm />
      {:else if $experiencePanelType === "campaign"}
        <CampaignDetail data={$experiencePanelData} />
      {:else if $experiencePanelType === "segment"}
        <SegmentDetail data={$experiencePanelData} />
      {:else if $experiencePanelType === "knowledge"}
        <KnowledgeDetail data={$experiencePanelData} />
      {:else if $experiencePanelType === "chart" && $experiencePanelData?.chart}
        {@const chartData = $experiencePanelData.chart}
        <Chart data={chartData} />
      {:else if $experiencePanelType === "recommendations" && $experiencePanelData?.recommendations}
        {@const recData = $experiencePanelData.recommendations}
        <RecommendationCards
          items={recData.items || []}
          type={recData.type || "mixed"}
          title={recData.title}
          description={recData.description}
        />
      {:else}
        <!-- Unknown format, show empty state -->
        <div class="text-center text-gray-500 dark:text-gray-400 py-8">
          No component to display
        </div>
      {/if}
    {:else}
      <div
        class="flex flex-col items-center justify-center text-gray-500 dark:text-gray-400 py-12 px-4"
      >
        <!-- Empty State Graphic -->
        <div class="w-64 h-48 mb-6 text-gray-300 dark:text-gray-600">
          <svg
            viewBox="0 0 200 150"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            class="w-full h-full"
          >
            <!-- Panel Frame -->
            <rect
              x="10"
              y="10"
              width="180"
              height="130"
              rx="8"
              stroke="currentColor"
              stroke-width="2"
              fill="none"
              stroke-dasharray="4 4"
              opacity="0.3"
            />

            <!-- Content Placeholders -->
            <!-- Card 1 (Campaign) -->
            <rect
              x="25"
              y="30"
              width="70"
              height="45"
              rx="4"
              fill="currentColor"
              opacity="0.1"
            />
            <rect
              x="30"
              y="35"
              width="40"
              height="3"
              rx="1.5"
              fill="currentColor"
              opacity="0.2"
            />
            <rect
              x="30"
              y="42"
              width="50"
              height="2"
              rx="1"
              fill="currentColor"
              opacity="0.15"
            />
            <rect
              x="30"
              y="47"
              width="35"
              height="2"
              rx="1"
              fill="currentColor"
              opacity="0.15"
            />

            <!-- Card 2 (Segment/Knowledge) -->
            <rect
              x="105"
              y="30"
              width="70"
              height="45"
              rx="4"
              fill="currentColor"
              opacity="0.1"
            />
            <rect
              x="110"
              y="35"
              width="35"
              height="3"
              rx="1.5"
              fill="currentColor"
              opacity="0.2"
            />
            <rect
              x="110"
              y="42"
              width="45"
              height="2"
              rx="1"
              fill="currentColor"
              opacity="0.15"
            />
            <rect
              x="110"
              y="47"
              width="30"
              height="2"
              rx="1"
              fill="currentColor"
              opacity="0.15"
            />

            <!-- Chart Placeholder -->
            <rect
              x="25"
              y="85"
              width="150"
              height="45"
              rx="4"
              fill="currentColor"
              opacity="0.1"
            />
            <line
              x1="35"
              y1="120"
              x2="165"
              y2="120"
              stroke="currentColor"
              stroke-width="1.5"
              opacity="0.2"
            />
            <line
              x1="35"
              y1="120"
              x2="35"
              y2="95"
              stroke="currentColor"
              stroke-width="1.5"
              opacity="0.2"
            />
            <!-- Chart bars -->
            <rect
              x="45"
              y="110"
              width="12"
              height="10"
              rx="2"
              fill="currentColor"
              opacity="0.2"
            />
            <rect
              x="65"
              y="105"
              width="12"
              height="15"
              rx="2"
              fill="currentColor"
              opacity="0.2"
            />
            <rect
              x="85"
              y="100"
              width="12"
              height="20"
              rx="2"
              fill="currentColor"
              opacity="0.2"
            />
            <rect
              x="105"
              y="108"
              width="12"
              height="12"
              rx="2"
              fill="currentColor"
              opacity="0.2"
            />
            <rect
              x="125"
              y="102"
              width="12"
              height="18"
              rx="2"
              fill="currentColor"
              opacity="0.2"
            />
            <rect
              x="145"
              y="115"
              width="12"
              height="5"
              rx="2"
              fill="currentColor"
              opacity="0.2"
            />

            <!-- Sparkle/Interactive Icons -->
            <circle cx="170" cy="25" r="3" fill="currentColor" opacity="0.2">
              <animate
                attributeName="opacity"
                values="0.2;0.4;0.2"
                dur="2s"
                repeatCount="indefinite"
              />
            </circle>
            <circle cx="185" cy="40" r="2.5" fill="currentColor" opacity="0.15">
              <animate
                attributeName="opacity"
                values="0.15;0.35;0.15"
                dur="2.5s"
                repeatCount="indefinite"
              />
            </circle>
            <circle cx="175" cy="50" r="2" fill="currentColor" opacity="0.1">
              <animate
                attributeName="opacity"
                values="0.1;0.3;0.1"
                dur="3s"
                repeatCount="indefinite"
              />
            </circle>
          </svg>
        </div>

        <!-- Message -->
        <p class="text-sm">Share your need to see your data come to life</p>
      </div>
    {/if}
  </div>
</div>
