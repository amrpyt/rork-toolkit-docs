# ربط Rork مع Chatwoot Captain

## الحكم

Rork لا يُركب مباشرة كـOpenAI Base URL داخل Chatwoot Captain، لأن:

- لا يوجد `/v1/chat/completions` على Rork.
- Text response هي `{completion}` وليست `choices`.
- Agent streaming هو Vercel AI SDK UI Message Stream v1 وليس OpenAI SSE.
- Tool calls تُرسل كـ`tool-input-*` events، لا `choices[].delta.tool_calls`.
- لا يوجد Embeddings endpoint مكتشف.

الحل الصحيح هو **Internal Adapter/Gateway**.

## المعمارية الموصى بها

```text
Chatwoot Captain
      |
      | OpenAI-compatible requests
      v
Rork Captain Adapter
  - Authentication
  - Tenant isolation
  - OpenAI <-> Rork mapping
  - Stream translation
  - Tool-call state
  - Validation
  - Timeouts/retries
  - Logs/metrics
  - Fallback provider
      |
      v
Rork /agent/chat
```

## Endpoint يقدمه الـAdapter لـChatwoot

الحد الأدنى:

```text
POST /v1/chat/completions
GET  /v1/models
GET  /health
```

اختياري حسب إعداد Captain:

```text
POST /v1/embeddings
```

لا توجه `/v1/embeddings` إلى Rork؛ استخدم مزود Embeddings منفصلًا.

## المسار الذي يستعمله الـAdapter في Rork

```text
POST https://toolkit.rork.com/agent/chat
```

استخدم `/llm/text` فقط لمسارات Text بسيطة لا تحتاج Tools أو streaming حقيقي.

---

# Mapping الرسائل

## OpenAI user message

Input من Chatwoot:

```json
{
  "role": "user",
  "content": "Where is order ORD-42?"
}
```

Rork UIMessage:

```json
{
  "id": "cw-msg-123",
  "role": "user",
  "parts": [
    {
      "type": "text",
      "text": "Where is order ORD-42?"
    }
  ]
}
```

## OpenAI assistant text

```json
{
  "role": "assistant",
  "content": "I will check the order."
}
```

Rork:

```json
{
  "id": "assistant-123",
  "role": "assistant",
  "parts": [
    {
      "type": "text",
      "text": "I will check the order."
    }
  ]
}
```

## System prompt

Rork Agent يقبل system role ضمن model messages في الاختبارات، لكن UI message transport يجب اختباره مع نسخة الـSDK المستخدمة. أبسط تصميم للـAdapter:

- احتفظ بتعليمات Captain في system message عندما تقبلها النسخة.
- أو دمجها في أول user context block بعلامة داخلية واضحة.
- لا تسمح للعميل النهائي بتعديل system prompt.

---

# Mapping تعريف الأدوات

## OpenAI tool

```json
{
  "type": "function",
  "function": {
    "name": "lookup_order",
    "description": "Look up an order by ID",
    "parameters": {
      "type": "object",
      "properties": {
        "orderId": {"type": "string"}
      },
      "required": ["orderId"],
      "additionalProperties": false
    }
  }
}
```

## Rork tool

```json
{
  "lookup_order": {
    "description": "Look up an order by ID",
    "jsonSchema": {
      "type": "object",
      "properties": {
        "orderId": {"type": "string"}
      },
      "required": ["orderId"],
      "additionalProperties": false
    }
  }
}
```

Mapping:

```ts
function openAIToolsToRork(tools: OpenAITool[]) {
  return Object.fromEntries(
    tools
      .filter(tool => tool.type === "function")
      .map(tool => [
        tool.function.name,
        {
          description: tool.function.description ?? "",
          jsonSchema: tool.function.parameters
        }
      ])
  );
}
```

قبل الإرسال:

- validate أسماء الأدوات.
- ارفض duplicate names.
- ضع حدًا لحجم schema.
- ارفض recursive أو شديدة التعقيد إذا لم تكن مدعومة.
- لا تقبل tool definitions من مستخدم غير موثوق.

---

# Mapping Tool Call

Rork event:

```json
{
  "type": "tool-input-available",
  "toolCallId": "call_123",
  "toolName": "lookup_order",
  "input": {
    "orderId": "ORD-42"
  }
}
```

OpenAI-compatible non-stream response part:

```json
{
  "id": "chatcmpl-rork-123",
  "object": "chat.completion",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_123",
            "type": "function",
            "function": {
              "name": "lookup_order",
              "arguments": "{\"orderId\":\"ORD-42\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}
```

OpenAI stream chunk:

```json
{
  "choices": [
    {
      "index": 0,
      "delta": {
        "tool_calls": [
          {
            "index": 0,
            "id": "call_123",
            "type": "function",
            "function": {
              "name": "lookup_order",
              "arguments": "{\"orderId\":\"ORD-42\"}"
            }
          }
        ]
      },
      "finish_reason": null
    }
  ]
}
```

لا ترسل OpenAI tool call قبل اكتمال `tool-input-available` إلا إذا نفذت parser مضبوطًا لتجميع `tool-input-delta`.

---

# طريقتان لتنفيذ Tools

## A. Chatwoot ينفذ Tool

```text
Rork tool event
      |
Adapter maps to OpenAI tool_call
      |
Chatwoot executes Captain custom tool
      |
Chatwoot sends role=tool result
      |
Adapter maps result back to Rork
```

هذه الطريقة مفضلة عندما تريد الاستفادة من:

- Captain custom tools.
- Permissions وإدارة الأدوات داخل Chatwoot.
- Audit trail الخاص بـChatwoot.

## B. الـAdapter ينفذ Tool

```text
Rork tool event
      |
Adapter validates and executes tool
      |
Adapter appends Rork output-available
      |
Rork returns final text
      |
Adapter sends only final answer to Chatwoot
```

هذه الطريقة مفيدة عندما تكون الأدوات داخلية عندك أو عندما لا يدعم مسار Captain المستخدم tool round-trip بالشكل المطلوب.

## التوصية

ابدأ بـA إن كانت نسخة Chatwoot الحالية عندك تدعم tool calls مع custom endpoint بشكل كامل. استخدم B للأدوات الخاصة بالـERP/OpenWA أو عندما تحتاج تحكمًا أدق في التنفيذ.

---

# Mapping Tool Result إلى Rork

Chatwoot/OpenAI message:

```json
{
  "role": "tool",
  "tool_call_id": "call_123",
  "content": "{\"status\":\"shipped\",\"trackingNumber\":\"TRK-9001\"}"
}
```

الـAdapter يحتاج state محفوظًا من الطلب السابق:

```json
{
  "toolCallId": "call_123",
  "toolName": "lookup_order",
  "input": {
    "orderId": "ORD-42"
  }
}
```

ثم يبني Rork assistant tool part:

```json
{
  "id": "assistant-tool-result-123",
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
        "status": "shipped",
        "trackingNumber": "TRK-9001"
      }
    }
  ]
}
```

ثم يعيد إرسال history إلى `/agent/chat` للحصول على final answer.

---

# Streaming text mapping

Rork:

```json
{
  "type": "text-delta",
  "id": "gen-1",
  "delta": "Hello"
}
```

OpenAI SSE:

```text
data: {"id":"chatcmpl-rork-1","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}
```

Rork finish:

```json
{
  "type": "finish",
  "finishReason": "stop"
}
```

OpenAI finish:

```text
data: {"id":"chatcmpl-rork-1","object":"chat.completion.chunk","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

## State store المطلوب

Key مقترح:

```text
chatwoot:{account_id}:{conversation_id}
```

البيانات:

```json
{
  "rorkMessages": [],
  "pendingToolCalls": {},
  "lastRequestId": "...",
  "updatedAt": "..."
}
```

استخدم Redis أو storage مشترك؛ لا تعتمد على memory داخل process واحد.

## Timeout policy

| المرحلة | اقتراح مبدئي |
|---|---|
| Rork TTFB | 5s |
| Text completion | 30s |
| Tool execution | 10–20s حسب الأداة |
| Image operations | 30–60s |
| Total Captain turn | حد مناسب لتجربة Chatwoot |

## Embeddings وKnowledge Base

لم يُكتشف Rork embeddings endpoint. افصل المسار:

```text
Captain chat completion -> Rork Adapter
Knowledge embeddings -> OpenAI/other embedding provider
```

لا تحاول تزييف `/v1/embeddings` باستخدام Text Generation.

## Headers داخلية مفيدة

```text
X-Chatwoot-Account-Id
X-Chatwoot-Conversation-Id
X-Chatwoot-Inbox-Id
X-Request-Id
```

تحقق منها داخل شبكة موثوقة فقط، ولا تقبلها كهوية من الإنترنت دون توقيع أو auth.

## Acceptance criteria للـAdapter

- Text streaming يعمل دون تكرار أو فقد chunks.
- Tool names وarguments تُحفظ بدقة.
- Tool result يرجع إلى نفس `toolCallId`.
- لا يتم تنفيذ unknown tools.
- كل conversation معزولة عن الأخرى.
- retries لا تكرر side effects.
- عند فشل Rork ينتقل النظام إلى fallback أو human handoff.
- Logs لا تحتوي محتوى حساسًا كاملًا افتراضيًا.
