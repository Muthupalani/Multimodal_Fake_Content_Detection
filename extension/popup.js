document.getElementById('scanBtn').addEventListener('click', () => {
    // Send a message to the content script to run the scan manually
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {action: "scan_page"});
    });
});