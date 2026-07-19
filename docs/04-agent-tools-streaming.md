# Agent، Streaming، وTool Calling

# `POST /agent/chat`

## الغرض

Conversational agent مع:

- Conversation history.
- Streaming.
- Tool calls.
- Tool result round-trip.
- Vision عبر UI message file parts.

```text
POST https://toolkit.rork.com/agent/chat
Content-Type: application/json
```

## البروتوكول

الاستجابة المقاسة:

```http
HTTP/2 200
Content-Type: application/octet-stream
Content-Encoding: none
Cache-Control: no-cache
X-Accel-Buffering: no
X-Vercel-Ai-UI-Message-Stream: v1
```

الـbody عبارة عن SSE-style frames:

```text
data: {"type":"start"}

data: {"type":"start-step"}

data: {"type":"text-start","id":"gen-..."}

data: {"type":"text-delta","id":"gen-...","delta":"Hello"}

data: {"type":"text-end","id":"gen-..."}

data: {"type":"finish-step"}

data: {"type":"finish","finishReason":"stop"}

data: [DONE]
```

هذا هو Vercel AI SDK UI Message Stream v1، وليس OpenAI SSE.

## Request المفضلة

```json
{
  "messages": [
    {
      "id": "user-1",
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "Hello"
        }
      ]
    }
  ],
  "tools": {}
}
```

الـSDK الرسمي ينشئ هذه الرسائل عبر `useChat` و`DefaultChatTransport`.

## تعريف Tool

الصيغة الخارجية المطلوبة من Rork:

```json
{
  "tools": {
    "lookup_order": {
      "description": "Look up an order and return its current status",
      "jsonSchema": {
        "type": "object",
        "properties": {
          "orderId": {
            "type": "string",
            "description": "The order identifier"
          }
        },
        "required": ["orderId"],
        "additionalProperties": false
      }
    }
  }
}
```

## لماذا `jsonSchema` وليس `inputSchema`؟

Vercel AI SDK داخليًا يستخدم `inputSchema`، لكن Rork يعرّف Contract خارجيًا خاصًا به باسم `jsonSchema`.

اختبار `inputSchema` مباشرة أعاد validation error يطلب:

```text
tools.<toolName>.jsonSchema
```

الـSDK الرسمي يحول Zod إلى JSON Schema:

```ts
const toolsEntries = Object.entries(options.tools).map(
  ([name, tool]) => [
    name,
    {
      description: tool.description,
      jsonSchema: z.toJSONSchema(tool.zodSchema)
    }
  ]
);
```

## Tool call stream

عندما يقرر الـAgent استدعاء Tool، التسلسل المقاس يكون قريبًا من:

```text
data: {"type":"start"}

data: {"type":"start-step"}

data: {"type":"reasoning-start","id":"gen-..."}

data: {"type":"reasoning-delta","id":"gen-...","delta":"[REDACTED]"}

data: {
  "type":"tool-input-start",
  "toolCallId":"call_123",
  "toolName":"lookup_order"
}

data: {
  "type":"tool-input-delta",
  "toolCallId":"call_123",
  "inputTextDelta":"{\"orderId\":\"ORD-42\"}"
}

data: {
  "type":"tool-input-available",
  "toolCallId":"call_123",
  "toolName":"lookup_order",
  "input":{"orderId":"ORD-42"}
}

data: {"type":"reasoning-end","id":"gen-..."}

data: {"type":"finish-step"}

data: {"type":"finish","finishReason":"tool-calls"}

data: [DONE]
```

نفّذ الأداة فقط بعد `tool-input-available`. لا تعتمد على `tool-input-delta` كـJSON كامل.

## تنفيذ Tool محليًا

```ts
const result = await lookupOrder({
  orderId: "ORD-42"
});
```

مثال output:

```json
{
  "orderId": "ORD-42",
  "status": "shipped",
  "trackingNumber": "TRK-9001"
}
```

## إرجاع Tool Result

أضف Assistant tool part إلى history ثم أرسل request جديدًا:

```json
{
  "id": "assistant-tool-1",
  "role": "assistant",
  "parts": [
    {
      "type": "tool-lookup_order",
      "toolCallId": "call_123",
      "state": "output-available",
      "input": {
        "orderId": "ORD-42"
      },
      "output": {
        "orderId": "ORD-42",
        "status": "shipped",
        "trackingNumber": "TRK-9001"
      }
    }
  ]
}
```

الـSDK الرسمي يوفر:

```ts
addToolResult({
  toolCallId,
  tool: toolName,
  output
});
```

ومع `lastAssistantMessageIsCompleteWithToolCalls` يرسل الرسالة التالية تلقائيًا للحصول على الرد النهائي.

## Tool error

يمكن تمثيل الفشل:

```json
{
  "type": "tool-lookup_order",
  "toolCallId": "call_123",
  "state": "output-error",
  "input": {
    "orderId": "ORD-42"
  },
  "errorText": "Order service timed out"
}
```

يجب على الـAdapter:

- عدم تنفيذ Tool غير موجود في allowlist.
- التحقق من input باستخدام JSON Schema أو Zod.
- وضع timeout مستقل لكل Tool.
- منع التكرار عبر idempotency key.
- عدم إرسال stack traces أو أسرار إلى الموديل.

## Vision داخل Agent

الصيغة التي نجحت كانت UI file part:

```json
{
  "id": "user-image-1",
  "role": "user",
  "parts": [
    {
      "type": "text",
      "text": "Read the order ID"
    },
    {
      "type": "file",
      "mediaType": "image/png",
      "url": "data:image/png;base64,..."
    }
  ]
}
```

الصيغة القديمة `{type:"image", image:"..."}` لم تُقبل كـUIMessage في الاختبار المباشر للـAgent.

## Conversation state

الـEndpoint Stateless من ناحية السيرفر بالنسبة للـhistory المرسلة: تذكّر قيمة سابقة فقط عندما تم إرسال الرسائل السابقة معه. لذلك الـAdapter مسؤول عن تخزين:

- Chatwoot conversation ID.
- Rork UI messages.
- Tool call IDs.
- Tool outputs.
- آخر request status.

## Parser مبسط

```ts
export async function readRorkStream(
  response: Response,
  onEvent: (event: unknown) => Promise<void> | void
): Promise<void> {
  if (!response.ok || !response.body) {
    throw new Error(`Rork error: ${response.status}`);
  }

  const reader = response.body
    .pipeThrough(new TextDecoderStream())
    .getReader();

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += value;
    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";

    for (const frame of frames) {
      const line = frame
        .split("\n")
        .find(item => item.startsWith("data:"));

      if (!line) continue;

      const payload = line.slice(5).trim();
      if (payload === "[DONE]") return;

      await onEvent(JSON.parse(payload));
    }
  }
}
```

Production parser يجب أن يضع limits لحجم frame، يتعامل مع malformed events، ويلغي الـrequest عند timeout أو client disconnect.
