# Advanced Features & Monitoring

## Lightweight Metrics
```ts
interface Metric { endpoint: string; ms: number; status: number; ts: number }
const metrics: Metric[] = []

export async function monitoredFetch(url: string, init: RequestInit) {
  const t0 = Date.now()
  try {
    const res = await fetch(url, init)
    metrics.push({ endpoint: url, ms: Date.now() - t0, status: res.status, ts: t0 })
    return res
  } catch (e) {
    metrics.push({ endpoint: url, ms: Date.now() - t0, status: 0, ts: t0 })
    throw e
  }
}
```

## Request Deduplication
```ts
const inflight = new Map<string, Promise<any>>()
export function dedup<T>(key: string, fn: () => Promise<T>) {
  if (inflight.has(key)) return inflight.get(key) as Promise<T>
  const p = fn().finally(() => inflight.delete(key))
  inflight.set(key, p)
  return p
}
```

## Cache (TTL)
```ts
const cache = new Map<string, { data: any; ts: number }>()
export async function cached<T>(key: string, ttl: number, fn: () => Promise<T>) {
  const c = cache.get(key)
  if (c && Date.now() - c.ts < ttl) return c.data as T
  const data = await fn()
  cache.set(key, { data, ts: Date.now() })
  return data
}
```

## Concurrency Control
```ts
class Semaphore { constructor(private n: number, private q: (() => void)[] = []) {}
  async acquire() { if (this.n > 0) return this.n--; await new Promise<void>(r => this.q.push(r)); this.n-- }
  release() { this.n++; const r = this.q.shift(); if (r) r() }
}
```
