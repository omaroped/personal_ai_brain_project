# Browser Bookmarklet for Personal AI Brain

The browser bookmarklet enables quick, one-click clipping of web articles, research papers, and blog posts directly from your browser. It automatically grabs the page URL, title, any selected text passage, and the first 5000 characters of the page body, sending them to your local ingestion server.

## Installation

1. Open your browser's Bookmarks Manager (or show the Bookmarks Bar).
2. Create a new bookmark.
3. Set the name to **Clip to Brain** (or similar).
4. Paste the following code block directly into the **URL** (or **Location**) field of the bookmark:

```javascript
javascript:(function(){
  const url = window.location.href;
  const isYouTube = window.location.hostname.includes('youtube.com') || window.location.hostname.includes('youtu.be');

  if (isYouTube) {
    fetch('http://127.0.0.1:8001/ingest/youtube?url=' + encodeURIComponent(url), {
      method: 'POST'
    })
    .then(response => {
      if (response.ok) {
        alert('✅ YouTube transcript saved to brain!');
      } else {
        alert('❌ Failed to save transcript (server error)');
      }
    })
    .catch(err => {
      alert('❌ Failed to connect to local brain. Is the API server running?');
      console.error(err);
    });
  } else {
    const data = {
      url: url,
      title: document.title,
      selected: window.getSelection().toString(),
      body: document.body.innerText.substring(0, 5000)
    };
    fetch('http://127.0.0.1:8001/ingest/web', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    })
    .then(response => {
      if (response.ok) {
        alert('✅ Saved to brain!');
      } else {
        alert('❌ Failed to save (server error)');
      }
    })
    .catch(err => {
      alert('❌ Failed to connect to local brain. Is the API server running?');
      console.error(err);
    });
  }
})();
```

## How to Use

1. Ensure the ingestion API server is running on your local machine:
   ```bash
   source /home/omar/personal_ai_brain_project/venv/bin/activate
   python3 src/ingestion/web_endpoint.py
   ```
2. Navigate to any web page you want to remember.
3. (Optional) Highlight/select a key passage you want to mark as the primary selection.
4. Click the **Clip to Brain** bookmark in your Bookmarks Bar.
5. You should see a confirmation alert: `✅ Saved to brain!`.
6. Within 60 seconds, a summary and key facts will automatically be generated using your local Ollama model and saved under `data/vault/summaries/`.
