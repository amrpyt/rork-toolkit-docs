# Best Practices

## Payload Hygiene
- Strip data URI prefix from base64 images
- Compress/resize images on client (target ~1024px max dimension)
- Avoid sending duplicate images within the same request

## Do Not Log Sensitive Data
- Never log raw base64 images or audio payloads
- Redact user PII

## Performance
- Cache identical requests (short TTL)
- Deduplicate in-flight requests by key
- Use AbortController for timeouts and cancellation

## Reliability
- Implement retries with exponential backoff for idempotent requests
- Validate responses before use (e.g., JSON.parse on `completion`)

## STT Specific
- Let the platform set multipart boundaries (no manual Content-Type)
- On React Native, use `{ uri, name, type }` object for FormData

## Env & Config
- Keep `EXPO_PUBLIC_TOOLKIT_URL` consistent across environments
- Centralize headers and base URL in a single module
