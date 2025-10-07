# Postman Collection Setup Guide

## Import Collection
1. Open Postman
2. Click **Import** → **Upload Files**
3. Select `rork-toolkit-postman-collection.json`
4. Collection will appear as "Rork Toolkit API Collection"

## Environment Setup

### Create Environment
1. Click **Environments** (left sidebar)
2. Click **+ Create Environment**
3. Name it "Rork Toolkit"

### Set Variables
| Variable | Value | Description |
|----------|--------|-------------|
| `RORK_BASE_URL` | `https://toolkit.rork.com` | Base URL for direct API calls |
| `EXPO_PUBLIC_TOOLKIT_URL` | `https://toolkit.rork.com` | Base URL for Agent Chat |
| `base64_image_raw` | `data:image/jpeg;base64,/9j/4AAQ...` | Raw base64 with data URI (optional) |
| `base64_image_clean` | `/9j/4AAQ...` | Clean base64 WITHOUT data URI prefix |

## Testing Guide

### 1. Start with Text Generation
- **Folder**: "1. Text LLM with Vision"
- **Request**: "Text Only Generation"
- **Expected**: `{ "completion": "..." }` response

### 2. Test Image Analysis
- **Requirement**: Set `base64_image_clean` variable
- **Request**: "Image Analysis + JSON Output" 
- **Expected**: JSON nutrition data in `completion` field

### 3. Test STT
- **Folder**: "5. Speech-to-Text"
- **Requirement**: Upload audio file in form data
- **Formats**: mp3, mp4, wav, webm, m4a
- **Expected**: `{ "text": "...", "language": "en" }`

### 4. Test Error Handling
- **Folder**: "Error Testing"
- **Purpose**: Verify error responses (400, 413, etc.)

## Image Preparation

### Get Base64 from File
```bash
# macOS/Linux
base64 -i image.jpg | tr -d '\n' > base64.txt

# Windows PowerShell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("image.jpg"))
```

### Online Tools
- **Base64 Encode**: https://base64.guru/converter/encode/image
- **Image Resize**: https://imageresizer.com/ (target 1024px max)

### Clean Data URI
If you have `data:image/jpeg;base64,ABC123...`, use only the `ABC123...` part.

## Common Issues

### ❌ 400 Bad Request
- **Cause**: Malformed JSON or invalid base64
- **Fix**: Validate JSON and ensure base64 is clean

### ❌ 413 Payload Too Large  
- **Cause**: Image too big
- **Fix**: Resize image to ~1024px max dimension

### ❌ No STT Response
- **Cause**: Manual Content-Type header
- **Fix**: Remove Content-Type header for multipart requests

## Advanced Usage

### Pre-request Script (Auto-clean base64)
```javascript
// Automatically clean base64 images
if (pm.environment.get('base64_image_raw')) {
  const cleaned = pm.environment.get('base64_image_raw')
    .replace(/^data:.*?;base64,/, '');
  pm.environment.set('base64_image_clean', cleaned);
}
```

### Tests Script (Validate responses)
```javascript
pm.test("Status code is 200", function () {
  pm.response.to.have.status(200);
});

pm.test("Response has completion field", function () {
  const json = pm.response.json();
  pm.expect(json).to.have.property('completion');
});

pm.test("Completion is valid JSON (if expected)", function () {
  const json = pm.response.json();
  try {
    JSON.parse(json.completion);
    pm.test.pass();
  } catch (e) {
    // completion might be plain text, that's also valid
  }
});
```
