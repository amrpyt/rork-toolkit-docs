# Error Handling & Retries

## Status Codes to Expect
- 400 Bad Request (malformed JSON, invalid base64)
- 401 Unauthorized (session expired)
- 403 Forbidden (quota/rules)
- 413 Payload Too Large (images)
- 429 Too Many Requests (rate limit)
- 500/503 Server/Unavailable

## Exponential Backoff
```ts
export async function retryWithBackoff<T>(fn: () => Promise<T>, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try { return await fn() } catch (err) {
      if (i === maxRetries - 1) throw err
      await new Promise(r => setTimeout(r, Math.pow(2, i) * 1000))
    }
  }
}
```

## Timeout & Abort
```ts
export async function fetchWithTimeout(resource: RequestInfo, options: RequestInit = {}, ms = 30000) {
  const controller = new AbortController()
  const id = setTimeout(() => controller.abort(), ms)
  try {
    const res = await fetch(resource, { ...options, signal: controller.signal })
    return res
  } finally { clearTimeout(id) }
}
```

## Safe JSON Parse
```ts
export async function safeJson<T>(res: Response): Promise<T> {
  const text = await res.text()
  try { return JSON.parse(text) as T } catch {
    throw new Error(`Invalid JSON: ${text?.slice(0, 300)}`)
  }
}
```

## Guarded Call Utility
```ts
export async function guardedJson<T>(url: string, init: RequestInit) {
  const res = await fetchWithTimeout(url, init)
  if (!res.ok) {
    let msg = `HTTP ${res.status}`
    try { const e = await res.json(); msg = e?.message || e?.error || msg } catch {}
    throw new Error(msg)
  }
  return safeJson<T>(res)
}
```

## Handling `completion` Field (May Contain JSON)
```ts
export function tryParseCompletion<T = unknown>(completion: string): T | null {
  try { return JSON.parse(completion) as T } catch { return null }
}
```
