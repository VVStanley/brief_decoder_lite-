export default defineContentScript({
  matches: ['<all_urls>'],
  main() {
    console.log('Brief Parser Assistant Content Script loaded.');

    chrome.runtime.onMessage.addListener(
      (
        message: { action: string },
        sender: chrome.runtime.MessageSender,
        sendResponse: (response?: { text: string }) => void
      ) => {
        if (message.action === 'GET_SELECTED_TEXT') {
          const selectedText = window.getSelection()?.toString() || '';
          sendResponse({ text: selectedText });
        }
        return false;
      }
    );
  },
});
