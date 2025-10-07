# Implementation Examples

## Web (Text + Vision)
```ts
import { stripDataUriPrefix } from "./utils" // or inline helper

const res = await fetch("https://toolkit.rork.com/text/llm/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    messages: [
      {
        role: "user",
        content: [
          { type: "text", text: "Classify this meal and return JSON" },
          { type: "image", image: stripDataUriPrefix(base64Image) }
        ]
      }
    ]
  })
})

const data = await res.json()
let parsed: any = null
try { parsed = JSON.parse(data.completion) } catch {}
```

## React Native (STT)
```ts
const fd = new FormData()
fd.append("audio", { uri: recording.getURI(), name: "rec.m4a", type: "audio/m4a" })
const res = await fetch("https://toolkit.rork.com/stt/transcribe/", { method: "POST", body: fd })
const json = await res.json()
```

## Node/Express Proxy
```ts
import express from "express"
import fetch from "node-fetch"

const app = express()
app.use(express.json({ limit: "10mb" }))

app.post("/api/ai/analyze", async (req, res) => {
  try {
    const upstream = await fetch("https://toolkit.rork.com/text/llm/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body)
    })

    if (!upstream.ok) {
      const errText = await upstream.text()
      return res.status(upstream.status).send(errText)
    }

    const data = await upstream.json()
    res.json(data)
  } catch (e: any) {
    res.status(500).json({ error: e?.message || "Proxy error" })
  }
})
```

## Agent Chat (Sketch)
```ts
const url = new URL("/agent/chat", process.env.EXPO_PUBLIC_TOOLKIT_URL)
const res = await fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    messages: [ { id: "1", role: "user", parts: [{ type: "text", text: "Hello agent" }] } ]
  })
})
```
