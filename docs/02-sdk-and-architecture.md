# الـSDK الرسمي والمعمارية

## الحزمة المنشورة

```text
@rork-ai/toolkit-sdk
```

الإصدار الذي تم فحصه أثناء البحث:

```text
0.2.54
```

## Base URL

الكود المنشور يحدد:

```ts
export const BASE_URL =
  process.env.EXPO_PUBLIC_TOOLKIT_URL ??
  "https://toolkit.rork.com";
```

يمكن تغيير الـBase URL عبر:

```text
EXPO_PUBLIC_TOOLKIT_URL
```

## أهم الاعتمادات

```text
ai
@ai-sdk/react
zod/v4
expo/fetch
```

## Functions المكشوفة

```ts
generateText(...)
generateObject(...)
useRorkAgent(...)
createRorkTool(...)
useConnections(...)
```

## Mapping من الـSDK إلى الـEndpoints

| SDK function | Endpoint |
|---|---|
| `generateText` | `POST /llm/text` |
| `generateObject` | `POST /llm/object` |
| `useRorkAgent` | `POST /agent/chat` |
| `useConnections` | `/connections/*` |

## كيف يعمل `generateText`؟

السلوك المنشور قريب من:

```ts
const result = await fetch(
  new URL("/llm/text", BASE_URL),
  {
    method: "POST",
    body: JSON.stringify({ messages })
  }
);

const data = await result.json();
return data.completion;
```

الـSDK لا يمرّر `model` أو `temperature` أو `maxTokens` في النسخة المفحوصة.

## كيف يعمل `generateObject`؟

```ts
const result = await fetch(
  new URL("/llm/object", BASE_URL),
  {
    method: "POST",
    body: JSON.stringify({
      messages,
      schema: z.toJSONSchema(params.schema)
    })
  }
);

const data = await result.json();
return params.schema.parse(data.object);
```

النقطة الحاسمة هنا أن الـSDK يطبق Zod parsing بعد رجوع الاستجابة. لذلك validation في العميل جزء أساسي من الـcontract، وليس تحسينًا اختياريًا.

## كيف يعمل `useRorkAgent`؟

الـSDK يستخدم مباشرة:

```ts
useChat
DefaultChatTransport
lastAssistantMessageIsCompleteWithToolCalls
```

ويحدد:

```ts
api: "https://toolkit.rork.com/agent/chat"
```

ثم يحوّل كل Tool من:

```ts
{
  description,
  zodSchema,
  execute
}
```

إلى payload خارجي:

```json
{
  "description": "...",
  "jsonSchema": {}
}
```

عند وصول Tool Call:

1. يبحث عن الأداة بالاسم.
2. ينفذ `tool.execute(input)` محليًا داخل التطبيق.
3. يستدعي `addToolResult` لإرجاع النتيجة.
4. يرسل الـSDK الرسالة التالية تلقائيًا لأن `lastAssistantMessageIsCompleteWithToolCalls` مفعّل.

## Analytics relay

الحزمة تستخدم PostHog relay على:

```text
https://toolkit.rork.com/relay-GnBZ/
```

وتسجل أحداثًا مثل:

```text
RORK/GENERATE_TEXT
RORK/GENERATE_OBJECT
RORK/USE_AGENT/SEND_MESSAGE
RORK/USE_AGENT/TOOL_CALL
```

هذا يؤكد أن `toolkit.rork.com` طبقة خدمات أوسع من مجرد LLM endpoint.
