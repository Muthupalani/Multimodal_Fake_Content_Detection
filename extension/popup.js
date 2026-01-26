document.getElementById('toggle').onclick = () => {
  chrome.storage.sync.get(['enabled'], (data) => {
    const enabled = !data.enabled;
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, {enabled});
    });
    chrome.storage.sync.set({enabled});
  });
};
document.getElementById('save').onclick = () => {
  const url = document.getElementById('backend').value;
  chrome.storage.sync.set({backendUrl: url});
};
