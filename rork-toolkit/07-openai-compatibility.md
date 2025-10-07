# OpenAI Compatibility & Adapter Notes

## Status
- Not OpenAI-compatible out-of-the-box
- Differences: response shape (`completion` vs `choices`), message parts, tool-calls, streaming format

## Differences Snapshot
| Feature | OpenAI | Rork Text LLM |
|---|---|---|
| Request | `{ messages: {role, content}[] }` | `{ messages: {role, content}[] } with image parts (base64 no prefix)` |
| Response | `{ choices[0].message.content }` | `{ completion: string }` |
| Tools | Functions / JSON schema | Agent Chat uses SDK-style tools |
| Streaming | SSE with `[DONE]` | Not observed for `/text/llm/` |

## Minimal Adapter (Concept)
```ts
// OpenAI-like -> Rork request
export function toRork(messages: { role: string; content: any }[]) {
  // Map image_url to { type: "image", image: base64WithoutPrefix }
  const mapContent = (c: any) => Array.isArray(c)
    ? c.map(p => p.type === "image_url" ? { type: "image", image: stripPrefix(p.image_url?.url) } : { type: "text", text: p.text })
    : c
  return { messages: messages.map(m => ({ role: m.role as any, content: mapContent(m.content) })) }
}

// Rork -> OpenAI-like
export function fromRork(resp: { completion: string }) {
  return { choices: [{ message: { role: "assistant", content: resp.completion } }] }
}
```

> For Agent Chat, use the Vercel AI SDK v5 directly instead of trying to emulate OpenAI.
