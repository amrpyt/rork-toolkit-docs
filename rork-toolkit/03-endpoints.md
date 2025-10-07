# Core Endpoints

## 1) Text LLM with Vision (Primary)
- Method: POST
- URL: `https://toolkit.rork.com/text/llm/`
- Content-Type: `application/json`

### Request
```ts
interface TextPart { type: "text"; text: string }
interface ImagePart { type: "image"; image: string } // Base64 WITHOUT data URI prefix

type ContentPart = TextPart | ImagePart

interface Message { role: "system" | "user" | "assistant"; content: string | ContentPart[] }

interface TextLLMRequest {
  messages: Message[]
  // Optional (inferred):
  model?: string
  temperature?: number
  max_tokens?: number
  top_p?: number
}
```

### Response
```ts
interface TextLLMResponse {
  completion: string
  usage?: { prompt_tokens?: number; completion_tokens?: number; total_tokens?: number }
  model?: string
  finish_reason?: string
}
```

### Example
```http
POST /text/llm/ HTTP/1.1
Host: toolkit.rork.com
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": [
        { "type": "text", "text": "Analyze this meal image and return JSON" },
        { "type": "image", "image": "/9j/4AAQSkZJRgABAQAA..." }
      ]
    }
  ]
}
```

---

## 2) Agent Chat (Conversational, SDK-oriented)
- Method: POST
- Base URL: `${process.env.EXPO_PUBLIC_TOOLKIT_URL}`
- Path: `/agent/chat`
- Format: Vercel AI SDK v5 compatible (messages with typed parts, tool calls)

### Minimal Request Sketch
```ts
interface ToolDefinition { description: string; parameters: any }

const res = await fetch(`${process.env.EXPO_PUBLIC_TOOLKIT_URL}/agent/chat`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    messages: [
      { id: "m1", role: "user", parts: [{ type: "text", text: "Hello" }] }
    ],
    tools: {
      addTodo: {
        description: "Add a todo",
        parameters: { type: "object", properties: { title: { type: "string" } }, required: ["title"] }
      }
    }
  })
})
```

> Note: Responses may stream; integration is easiest via the Vercel AI SDK.

---

## 3) Image Generation
- Method: POST
- URL: `https://toolkit.rork.com/images/generate/`
- Model: DALL-E 3

### Request
```json
{
  "prompt": "A photorealistic image of a healthy salad bowl",
  "size": "1024x1024"
}
```

### Response
```json
{
  "image": { "base64Data": "...", "mimeType": "image/png" },
  "size": "1024x1024"
}
```

---

## 4) Image Editing
- Method: POST
- URL: `https://toolkit.rork.com/images/edit/`
- Model: Google Gemini 2.5 Flash Image Preview

### Request
```json
{
  "prompt": "Lightly enhance colors and contrast",
  "images": [ { "type": "image", "image": "<base64>" } ]
}
```

### Response
```json
{
  "image": { "base64Data": "...", "mimeType": "image/png" }
}
```

---

## 5) Speech-to-Text (STT)
- Method: POST
- URL: `https://toolkit.rork.com/stt/transcribe/`
- Content-Type: multipart/form-data (auto)
- Formats: mp3, mp4, mpeg, mpga, m4a, wav, webm

### Request (FormData)
```ts
const fd = new FormData()
fd.append("audio", audioFile) // File/Blob on web; { uri, name, type } on RN
// Optional language:
// fd.append("language", "en")

fetch("https://toolkit.rork.com/stt/transcribe/", { method: "POST", body: fd })
```

### Response
```json
{ "text": "...", "language": "en" }
```
