console.log("🛡️ Fake Content Detector Script Loaded");

// 1. Listen for Manual Scan Trigger
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "scan_page") {
        scanPage();
    }
});

// Optional: Auto-scan when page loads
window.addEventListener('load', scanPage);

async function scanPage() {
    console.log("🔍 Scanning page for content...");

    // Generic selector: Grabs all images on the page
    // In a real app, you would target specific post containers (e.g., 'article' tags)
    const images = document.querySelectorAll('img');

    images.forEach((img, index) => {
        // Skip small icons or invisible images
        if (img.width < 100 || img.height < 100) return;

        // Extract Data
        const imageUrl = img.src;
        
        // Try to find the nearest caption (text in the parent container)
        // This is a rough approximation for demo purposes
        const container = img.parentElement; 
        const captionText = container ? container.innerText : "";
        
        // Extract Hashtags (simple regex)
        const hashtags = captionText.match(/#[a-z0-9_]+/gi) || [];

        console.log(`Analyzing Image ${index}:`, imageUrl);

        // Prepare Payload
        const payload = {
            image_url: imageUrl,
            caption: captionText,
            hashtags: hashtags
        };

        // 2. Send to Backend API
        fetch('http://127.0.0.1:5000/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            console.log("✅ Analysis Result:", data);
            
            // 3. Apply Decision
            if (data.final_decision === "BLUR") {
                applyBlur(img, data);
            }
        })
        .catch(error => console.error("API Error:", error));
    });
}

function applyBlur(imgElement, data) {
    // 1. Apply Blur Class
    imgElement.classList.add('fake-content-blur');

    // 2. Create Warning Overlay
    const warning = document.createElement('div');
    warning.className = 'fake-content-warning';
    
    // Customize message based on what failed
    let reasons = [];
    if (data.image_analysis.result !== 'fact') reasons.push("Fake Image");
    if (data.caption_analysis.result !== 'fact') reasons.push("Fake Caption");
    if (data.hashtag_analysis.result !== 'related') reasons.push("Bad Hashtags");

    warning.innerHTML = `
        ⚠️ <strong>CONTENT WARNING</strong> ⚠️<br>
        ${reasons.join(" + ")}<br>
        <small>Click to Reveal</small>
    `;

    // 3. Add overlay to the parent
    if (imgElement.parentElement) {
        imgElement.parentElement.style.position = "relative"; // Ensure absolute positioning works
        imgElement.parentElement.appendChild(warning);
    }

    // 4. Click to Reveal Logic
    warning.addEventListener('click', () => {
        imgElement.classList.remove('fake-content-blur');
        warning.remove();
    });
}