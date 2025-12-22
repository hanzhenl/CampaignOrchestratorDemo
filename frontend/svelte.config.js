import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  preprocess: vitePreprocess(),
  compilerOptions: {
    // Enable compatibility mode for Svelte 4 syntax
    compatibility: {
      componentApi: 4
    }
  }
};
