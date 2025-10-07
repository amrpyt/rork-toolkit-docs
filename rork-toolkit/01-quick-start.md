# Quick Start

Use this guide to make your first successful call.

## Base Setup
```ts
const RORK_BASE_URL = "https://toolkit.rork.com";
const headers = { "Content-Type": "application/json" };
```

## Clean Base64 Helper
Strip the `data:*;base64,` prefix before sending images to the Text LLM endpoint.
```ts
export function stripDataUriPrefix(dataUrlOrBase64: string) {
  return dataUrlOrBase64.replace(/^data:.*?;base64,/, "");
}
```

## First Call: Text + Vision
```ts
const res = await fetch(`${RORK_BASE_URL}/text/llm/`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    messages: [
      {
        role: "user",
        content: [
          { type: "text", text: "Analyze this meal image and return nutrition as JSON" },
          { type: "image", image: stripDataUriPrefix(base64Image) }
        ]
      }
    ]
  })
});
const data = await res.json();
// data.completion is a string (may contain JSON)
let parsed: any = null;
try { parsed = JSON.parse(data.completion); } catch {}
```

## Optional Parameters (Experimental)
```ts
{
  temperature?: number;  // 0.0..2.0
  top_p?: number;        // 0..1
  max_tokens?: number;   // response length limit
  model?: string;        // server default if omitted
}
```

## Agent Chat Base URL
If you later use Agent Chat, configure:
```env
EXPO_PUBLIC_TOOLKIT_URL=https://toolkit.rork.com
```
