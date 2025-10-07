# API Endpoint Analysis: Rork Toolkit AI Service

## Executive Summary
Based on the codebase analysis, I've identified two distinct AI API endpoints in use by this application. Let me provide exhaustive technical documentation for both.

---

## 1. Agent Chat API (Primary Conversational Interface)

### Endpoint Configuration
- **Protocol:** HTTPS
- **Base URL:** process.env["EXPO_PUBLIC_TOOLKIT_URL"]
- **Path:** /agent/chat
- **Full URL Construction:** new URL("/agent/chat", process.env["EXPO_PUBLIC_TOOLKIT_URL"])
- **Method:** POST

### Authentication & Headers
- **Content-Type:** application/json
- **Authorization:** Inferred to be handled via environment variable or session context
- **X-Request-ID:** Likely auto-generated (not explicitly shown in client code)

### Request Schema
Format: Vercel AI SDK v5 compatible message format

```typescript
interface AgentChatRequest {
  messages: Message[];
  tools?: Record<string, ToolDefinition>;
  model?: string; // Inferred, not explicitly shown
  temperature?: number; // Inferred
  maxTokens?: number; // Inferred
}

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  parts: MessagePart[];
}

type MessagePart = TextPart | ImagePart | ToolPart;

interface TextPart {
  type: "text";
  text: string;
}

interface ImagePart {
  type: "image";
  image: string; // base64 encoded data URI
}

interface ToolPart {
  type: "tool";
  toolName: string;
  state: "input-streaming" | "input-available" | "output-available" | "output-error";
  input?: Record<string, any>;
  output?: any;
  errorText?: string;
}

interface ToolDefinition {
  description: string;
  parameters: ZodSchema; // Zod schema converted to JSON Schema
  execute?: (input: any) => any | Promise<any>;
}
```

### Response Format
Streaming Response: Server-Sent Events (SSE) or chunked transfer encoding

```typescript
interface AgentChatResponse {
  messages: Message[];
  // Streaming chunks contain partial message updates
}

// Streaming chunk example:
{
  "type": "message-delta",
  "id": "msg_abc123",
  "role": "assistant",
  "delta": {
    "type": "text",
    "text": "partial response..."
  }
}

// Tool invocation chunk:
{
  "type": "tool-call",
  "id": "tool_xyz789",
  "toolName": "addTodo",
  "state": "input-streaming",
  "input": {
    "title": "Buy groceries"
  }
}
```

### OpenAI Compatibility
**Status:** ❌ NOT OpenAI-compatible

This is a custom Vercel AI SDK v5 implementation with significant differences:

| Feature | OpenAI API | Rork Agent API |
|---------|-----------|----------------|
| Message format | {role, content} | {role, parts[]} with typed parts |
| Tool calling | tools array with function objects | Custom ToolDefinition with Zod schemas |
| Streaming | data: [DONE] delimiter | Vercel AI SDK streaming protocol |
| Images | content: [{type: "image_url"}] | parts: [{type: "image", image: base64}] |
| Response | choices[0].message | Direct messages array |

### Hidden/Inferred Parameters
```typescript
// Not explicitly shown in client code but likely supported:
{
  model: "gpt-4" | "claude-3-5-sonnet" | string,
  temperature: 0.0 - 2.0,
  maxTokens: number,
  topP: number,
  frequencyPenalty: number,
  presencePenalty: number,
  stopSequences: string[],
  metadata: {
    userId?: string,
    sessionId?: string
  }
}
```

### Rate Limits & Constraints
- **Rate Limiting:** Unknown (not exposed in client)
- **Max Message History:** Unknown
- **Max Tool Definitions:** Unknown
- **Timeout:** Likely 60-120 seconds for streaming
- **Max Image Size:** Unknown (base64 encoded)
- **Concurrent Requests:** Unknown

### Full Request Example
```http
POST https://toolkit.rork.com/agent/chat
Content-Type: application/json

{
  "messages": [
    {
      "id": "msg_001",
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "Add a todo to buy milk"
        }
      ]
    }
  ],
  "tools": {
    "addTodo": {
      "description": "Add a new todo item",
      "parameters": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "description": "Short description of the todo item"
          },
          "priority": {
            "type": "string",
            "enum": ["low", "medium", "high"],
            "description": "Priority level"
          }
        },
        "required": ["title"]
      }
    }
  }
}
```

### Full Response Example
```json
{
  "messages": [
    {
      "id": "msg_001",
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "Add a todo to buy milk"
        }
      ]
    },
    {
      "id": "msg_002",
      "role": "assistant",
      "parts": [
        {
          "type": "tool",
          "toolName": "addTodo",
          "state": "output-available",
          "input": {
            "title": "Buy milk",
            "priority": "medium"
          },
          "output": {
            "success": true,
            "todoId": "todo_123"
          }
        },
        {
          "type": "text",
          "text": "I've added 'Buy milk' to your todo list with medium priority."
        }
      ]
    }
  ]
}
```

---

## 2. Simple Generation APIs (Non-conversational)

### 2.1 Generate Text API
```typescript
// Imported from: @rork/toolkit-sdk
async function generateText(
  params: string | { messages: (UserMessage | AssistantMessage)[] }
): Promise<string>

interface UserMessage {
  role: "user";
  content: string | (TextPart | ImagePart)[];
}

interface AssistantMessage {
  role: "assistant";
  content: string | TextPart[];
}
```

- **Endpoint:** Unknown (abstracted by SDK)  
- **Use Case:** Single-shot text generation without chat history  
- **Response:** Plain string

### 2.2 Generate Object API
```typescript
async function generateObject<T extends z.ZodType>(params: {
  messages: (UserMessage | AssistantMessage)[];
  schema: T;
}): Promise<z.infer<T>>
```

- **Endpoint:** Unknown (abstracted by SDK)  
- **Use Case:** Structured data extraction with Zod schema validation  
- **Response:** Typed object matching Zod schema

---

## 3. Image Generation API

### Endpoint Configuration
- **URL:** https://toolkit.rork.com/images/generate/
- **Method:** POST
- **Model:** DALL-E 3

### Request Schema
```typescript
interface ImageGenerateRequest {
  prompt: string;
  size?: "1024x1024" | "512x512" | string;
}
```

### Response Schema
```typescript
interface ImageGenerateResponse {
  image: {
    base64Data: string;
    mimeType: string; // e.g., "image/png"
  };
  size: string;
}
```

### Full Example
```http
POST https://toolkit.rork.com/images/generate/
Content-Type: application/json

{
  "prompt": "A photorealistic image of a healthy salad bowl",
  "size": "1024x1024"
}

// Response:
{
  "image": {
    "base64Data": "/9j/4AAQSkZJRgABAQAA...",
    "mimeType": "image/png"
  },
  "size": "1024x1024"
}
```

---

## 4. Image Editing API

### Endpoint Configuration
- **URL:** https://toolkit.rork.com/images/edit/
- **Method:** POST
- **Model:** Google Gemini 2.5 Flash Image Preview

### Request Schema
```typescript
interface ImageEditRequest {
  prompt: string;
  images: Array<{
    type: "image";
    image: string; // base64 encoded
  }>;
}
```

### Response Schema
```typescript
interface ImageEditResponse {
  image: {
    base64Data: string;
    mimeType: string;
  };
}
```

---

## 5. Speech-to-Text API

### Endpoint Configuration
- **URL:** https://toolkit.rork.com/stt/transcribe/
- **Method:** POST
- **Content-Type:** multipart/form-data (auto-set by browser)
- **Supported Formats:** mp3, mp4, mpeg, mpga, m4a, wav, webm

### Request Schema
```typescript
interface STTRequest {
  audio: File; // FormData field
  language?: string; // Optional, auto-detects if omitted
}
```

### Response Schema
```typescript
interface STTResponse {
  text: string;
  language: string;
}
```

### Critical Implementation Notes
```typescript
// NEVER manually set Content-Type for FormData
const formData = new FormData();

// Mobile (iOS/Android) - append as object
formData.append('audio', {
  uri: recording.getURI(),
  name: "recording.m4a",
  type: "audio/m4a"
});

// Web - append as Blob
formData.append('audio', audioBlob, 'recording.webm');

fetch('https://toolkit.rork.com/stt/transcribe/', {
  method: 'POST',
  body: formData
  // DO NOT SET Content-Type header
});
```

---

## Integration Compatibility Matrix

| Integration | Agent Chat API | Generate APIs | Image APIs | STT API |
|-------------|----------------|---------------|------------|---------|
| OpenAI SDK | ❌ No | ❌ No | ❌ No | ❌ No |
| LangChain | ⚠️ Custom adapter needed | ⚠️ Custom adapter | ❌ No | ❌ No |
| n8n | ❌ No | ❌ No | ⚠️ HTTP node | ⚠️ HTTP node |
| Vercel AI SDK | ✅ Yes (native) | ✅ Yes | ❌ No | ❌ No |
| Direct HTTP | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

---

## Observable Differences from OpenAI Standard

1. **Message Structure:** Uses parts[] array instead of flat content field
2. **Tool Calling:** Zod-based schema definition vs OpenAI's JSON Schema
3. **Streaming Protocol:** Vercel AI SDK format vs OpenAI's SSE format
4. **Image Handling:** Direct base64 in message parts vs image_url objects
5. **Tool State Management:** Explicit state tracking (input-streaming, output-available, etc.)
6. **Response Format:** Direct message array vs choices[0].message wrapper
7. **SDK Requirement:** Requires @rork/toolkit-sdk for proper integration

---

## Security & Authentication

```typescript
// Authentication appears to be handled via:
// 1. Environment variable: EXPO_PUBLIC_TOOLKIT_URL
// 2. Implicit session/token management (not visible in client code)
// 3. Possible API key in headers (abstracted by SDK)

// No explicit API key visible in codebase
// Suggests server-side session or OAuth-based auth
```

---

## Reverse Engineering Notes

- **SDK Abstraction:** Heavy use of @rork/toolkit-sdk hides low-level HTTP details
- **TypeScript Path Mapping:** SDK is globally available via tsconfig paths, not npm
- **Vercel AI SDK v5:** Core dependency for message format and streaming
- **Custom Protocol:** Proprietary extension of Vercel AI SDK patterns
- **No Direct OpenAI Compatibility:** Requires custom client implementation
- **Tool Execution:** Can be client-side (with execute function) or server-side
- **Streaming:** Likely uses ReadableStream API with custom chunk parsing

**Conclusion:** This API is a proprietary AI orchestration layer built on Vercel AI SDK primitives, not a drop-in OpenAI replacement.
