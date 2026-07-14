import { defineConfig } from 'wxt';

// See https://wxt.dev/api/config.html
export default defineConfig({
  modules: ['@wxt-dev/module-react'],
  manifest: {
    name: 'Brief Parser Assistant',
    description: 'AI-powered brief parsing assistant',
    version: '1.0.0',
    permissions: ['sidePanel', 'storage', 'activeTab', 'scripting'],
    side_panel: {
      default_path: 'sidepanel.html',
    },
    action: {},
  },
});
