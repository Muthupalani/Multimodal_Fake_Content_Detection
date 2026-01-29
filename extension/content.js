let autoScanEnabled = false;
const BACKEND_URL = 'http://localhost:8000/analyze';  // Change via storage
// Social selectors (Instagram/X 2026 compatible)
function extractPostData() {
  const posts = [];
  // Instagram post selectors
  const igPosts = document.querySelectorAll('article a[href*="/p/"], div[role="button"]');
  igPosts.forEach(post => {
    const img = post.querySelector('img');
    const captionEl = post.closest('article')?.querySelector('h1, span[dir="auto"]');
    const htEl = captionEl?.nextElementSibling?.textContent?.match(/#\w+/g) || [];
    if (img?.src && captionEl?.textContent) {
      posts.push({
        image_url: img.src,
        caption: captionEl.textContent.trim().slice(0, 512),
        hashtags: htEl
      });
    }
  });
  // X selectors (adapt similar)
  const xPosts = document.querySelectorAll('[data-testid="tweet"] img');
  // ... similar extraction
  return posts;
}
async function analyzeAndAct(postData) {
  try {
    const res = await fetch(BACKEND_URL, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(postData)
    });
    const { actions, final_score } = await res.json();
    // Modify DOM
    if (actions.blur_image) postData.image.style.filter = 'blur(10px)';
    if (actions.hide_caption) postData.captionEl.style.display = 'none';
    if (actions.hide_hashtags) postData.htEl.forEach(el => el.style.textDecoration = 'line-through');
    if (actions.blur_post) {
      const postContainer = postData.post.closest('article, [data-testid="tweet"]');
      postContainer.style.filter = 'blur(5px)';
    }
  } catch (e) { console.error('Analysis failed:', e); }
}
// MutationObserver for dynamic content
const observer = new MutationObserver(debounce(extractPostData, 1000).then(posts => {
  if (autoScanEnabled && posts.length) posts.forEach(analyzeAndAct);
}));
observer.observe(document.body, { childList: true, subtree: true });
// Utils
function debounce(fn, delay) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
}
// Listen for enable message from popup
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.enabled !== undefined) autoScanEnabled = msg.enabled;
});
