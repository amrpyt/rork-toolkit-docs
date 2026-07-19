# cURL examples

## Text

```bash
curl -sS https://toolkit.rork.com/llm/text \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [
      {"role":"system","content":"Reply concisely"},
      {"role":"user","content":"Explain stock transfer in one sentence"}
    ]
  }'
```

## Vision with Data URI

```bash
IMAGE_B64="$(base64 -w 0 screenshot.png)"

curl -sS https://toolkit.rork.com/llm/text \
  -H 'Content-Type: application/json' \
  -d "{
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": [
          {\"type\":\"text\",\"text\":\"Read the order ID\"},
          {\"type\":\"image\",\"image\":\"data:image/png;base64,$IMAGE_B64\"}
        ]
      }
    ]
  }"
```

## Structured object

```bash
curl -sS https://toolkit.rork.com/llm/object \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [
      {"role":"user","content":"Extract order ORD-42 with status shipped"}
    ],
    "schema": {
      "type":"object",
      "properties": {
        "orderId":{"type":"string"},
        "status":{"type":"string"}
      },
      "required":["orderId","status"],
      "additionalProperties":false
    }
  }'
```

## Agent without tools

```bash
curl -N https://toolkit.rork.com/agent/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [
      {
        "id":"user-1",
        "role":"user",
        "parts":[
          {"type":"text","text":"Reply exactly AGENT_OK"}
        ]
      }
    ],
    "tools": {}
  }'
```

## Agent with tool

```bash
curl -N https://toolkit.rork.com/agent/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [
      {
        "id":"user-1",
        "role":"user",
        "parts":[
          {"type":"text","text":"Check order ORD-42 using lookup_order"}
        ]
      }
    ],
    "tools": {
      "lookup_order": {
        "description":"Look up an order by ID",
        "jsonSchema": {
          "type":"object",
          "properties": {
            "orderId":{"type":"string"}
          },
          "required":["orderId"],
          "additionalProperties":false
        }
      }
    }
  }'
```

## Image generation

```bash
curl -sS https://toolkit.rork.com/images/generate/ \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt":"A clean product illustration on a white background"
  }'
```

## Image editing

```bash
IMAGE_B64="$(base64 -w 0 input.png)"

curl -sS https://toolkit.rork.com/images/edit/ \
  -H 'Content-Type: application/json' \
  -d "{
    \"prompt\":\"Change the background to a modern office\",
    \"images\":[
      {\"type\":\"image\",\"image\":\"$IMAGE_B64\"}
    ]
  }"
```

## Speech-to-text

```bash
curl -sS https://toolkit.rork.com/stt/transcribe/ \
  -F 'audio=@sample.wav'
```

## Legacy text

```bash
curl -sS https://toolkit.rork.com/text/llm/ \
  -H 'Content-Type: application/json' \
  -d '{
    "messages":[
      {"role":"user","content":"Reply exactly LEGACY_OK"}
    ]
  }'
```

ابدأ أي Integration جديد على `/llm/text` أو `/agent/chat`، وليس المسار Legacy.
