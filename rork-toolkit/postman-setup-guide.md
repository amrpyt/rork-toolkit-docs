# Postman setup

Import [`rork-toolkit-postman-collection.json`](./rork-toolkit-postman-collection.json).

The collection uses:

```text
baseUrl = https://toolkit.rork.com
```

No visible API key was required during the July 2026 measurements. This is not a guarantee of future access or a recommendation to expose the endpoints directly in production.

## Recommended order

1. Current — Text
2. Current — Structured Object
3. Current — Agent Text Stream
4. Current — Agent Tool Call
5. Image Generation
6. Image Editing
7. Speech-to-Text
8. Legacy — Text LLM

## Notes

- Postman may display `/agent/chat` as a raw streaming response. Inspect `data:` frames manually.
- Replace Base64 placeholders before testing images.
- Select a real local audio file for the `audio` form-data field.
- Validate `/llm/object` responses locally; HTTP 200 does not prove schema compliance.
- Avoid repeated image/audio requests unless needed because they are larger and slower.
