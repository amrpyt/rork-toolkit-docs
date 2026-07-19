# Text وStructured Object

# `POST /llm/text`

## الغرض

Single-shot text or vision generation بدون conversation state أو Tool Calling.

```text
POST https://toolkit.rork.com/llm/text
Content-Type: application/json
```

## Request

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Reply exactly: OK"
    }
  ]
}
```

## Response

```json
{
  "completion": "OK"
}
```

لا ترجع الاستجابة OpenAI fields مثل:

```text
choices
usage
model
finish_reason
id
object
```

## Roles المقبولة

الاختبارات أثبتت قبول:

```text
system
user
assistant
```

مثال:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Reply only with SYSTEM_OK"
    },
    {
      "role": "user",
      "content": "Test"
    }
  ]
}
```

## Multimodal content

`user.content` يمكن أن يكون String أو array من parts:

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Read the image"
        },
        {
          "type": "image",
          "image": "BASE64_OR_DATA_URI"
        }
      ]
    }
  ]
}
```

الاختبارات نجحت مع:

- Base64 خام.
- Data URI مثل `data:image/png;base64,...`.

لذلك لا تعتمد على الادعاء القديم بأن Data URI يجب إزالتها دائمًا. الأفضل توحيد format داخل الـAdapter واختبار صور حقيقية ضمن contract tests.

## Fields لا يجب الاعتماد عليها

تم إرسال قيم مثل:

```json
{
  "model": "definitely-not-real",
  "temperature": -10,
  "max_tokens": -1,
  "stream": true,
  "providerOptions": {}
}
```

وظل الطلب ينجح. هذا يعني أن الحقول قد تكون ignored أو stripped. الـSDK الحالي أصلًا لا يرسلها.

لا تعتبر قبول الحقل دليلًا على تطبيقه.

## الأخطاء المقاسة

### JSON غير صالح

```http
400 Bad Request
```

```json
{"error":"Request body must be valid JSON"}
```

### `messages` مفقودة

```http
400 Bad Request
```

```json
{
  "error": "Invalid request body",
  "issues": [
    {
      "expected": "array",
      "path": ["messages"]
    }
  ]
}
```

### `messages: []`

```http
500 Internal Server Error
```

```json
{"error":"Internal server error"}
```

هذه server bug معروفة بالاختبار؛ امنع empty arrays عندك محليًا.

---

# `POST /llm/object`

## الغرض

استخراج JSON object من رسائل وفق JSON Schema. الاستخدام الرسمي عبر `generateObject` مع Zod schema.

```text
POST https://toolkit.rork.com/llm/object
Content-Type: application/json
```

## Request

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Return Alice, age 30"
    }
  ],
  "schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "age": {"type": "number"}
    },
    "required": ["name", "age"],
    "additionalProperties": false
  }
}
```

## Response

```json
{
  "object": {
    "name": "Alice",
    "age": 30
  }
}
```

## Roles المقبولة

الـSDK type definitions تسمح بـ:

```text
user
assistant
```

الاختبار أثبت أن `system` يُرفض في `/llm/object`:

```http
400 Bad Request
```

لإضافة تعليمات عامة، ضعها في أول `user` message بدل `system`.

## تحذير حاسم: Schema ليست ضمانًا من السيرفر

الاختبارات التالية رجعت `200`:

- Schema مفقودة.
- Schema بقيمة أو type غير صالح.
- Schema لا تفرض الشكل المطلوب بوضوح.

وفي بعض الحالات رجع السيرفر Object generic أو Object لا يمثل intent المتوقع.

لذلك يجب تطبيق validation محليًا:

```ts
import { z } from "zod";

const ResultSchema = z.object({
  name: z.string(),
  age: z.number().int().nonnegative()
});

const response = await fetch(
  "https://toolkit.rork.com/llm/object",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      messages,
      schema: z.toJSONSchema(ResultSchema)
    })
  }
);

if (!response.ok) {
  throw new Error(`Rork error: ${response.status}`);
}

const data = await response.json();
const parsed = ResultSchema.safeParse(data.object);

if (!parsed.success) {
  throw new Error("Rork returned an object that failed validation");
}

return parsed.data;
```

## الأخطاء المقاسة

### `messages` مفقودة

```http
400
```

### `messages: []`

```http
500
```

### `system` role

```http
400
```

## قرار الاستخدام

- استخدم `/llm/object` للاستخراج القصير غير الحواري.
- ضع Schema صارمة.
- امنع empty messages.
- طبّق local validation إلزاميًا.
- لا تستعمله بدل Tool Calling عندما تحتاج تنفيذ Actions حقيقية.
