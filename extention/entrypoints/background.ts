export default defineBackground(() => {
  console.log('Hello background!', { id: browser.runtime.id });

  // Open the sidepanel when clicking the extension action icon
  chrome.sidePanel
    .setPanelBehavior({ openPanelOnActionClick: true })
    .catch((error: unknown) => console.error('Failed to set sidepanel behavior:', error));
});
