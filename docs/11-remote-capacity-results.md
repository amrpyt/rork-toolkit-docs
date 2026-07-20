# Remote Capacity and Tool Tests

**Test date:** 20 July 2026  
**Target:** `POST https://toolkit.rork.com/agent/chat`  
**Runner platform:** GitHub-hosted Ubuntu runners  
**Production server IP used:** No

## Runs

- [Stage 1 — baseline and concurrency to 32](https://github.com/amrpyt/API-interface/actions/runs/29712574240)
- [Stage 2 — concurrency to 96 and tool edge cases](https://github.com/amrpyt/API-interface/actions/runs/29712666297)

## Egress IPs

Six separate GitHub-hosted jobs used six distinct public egress IPs:

| Run | Python job | Egress IP |
|---|---:|---|
| Stage 1 | 3.9 | `172.203.7.51` |
| Stage 1 | 3.10 | `4.155.252.117` |
| Stage 1 | 3.11 | `20.168.94.82` |
| Stage 2 | 3.9 | `172.172.157.1` |
| Stage 2 | 3.10 | `20.64.206.181` |
| Stage 2 | 3.11 | `68.154.54.34` |

## Aggregate result

Across both stages, the runners sent **482 measured agent requests**.

| Metric | Result |
|---|---:|
| HTTP `200` for measured requests | 482 |
| HTTP `429` | 0 |
| HTTP `5xx` | 0 |
| Authentication required | No |
| API key required | No |
| UI Message Stream header | `v1` |

## Capacity results

### Burst ramp

| Concurrency | Requests | Success | `429` | `5xx` | Median | p95 | Max | Throughput |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 100% | 0 | 0 | 764 ms | 764 ms | 764 ms | 1.29 req/s |
| 2 | 2 | 100% | 0 | 0 | 706 ms | 577 ms | 835 ms | 2.39 req/s |
| 4 | 4 | 100% | 0 | 0 | 669 ms | 725 ms | 754 ms | 5.30 req/s |
| 8 | 8 | 100% | 0 | 0 | 782 ms | 1,028 ms | 1,056 ms | 7.51 req/s |
| 16 | 16 | 100% | 0 | 0 | 885 ms | 1,165 ms | 1,204 ms | 13.02 req/s |
| 32 | 32 | 100% | 0 | 0 | 1,015 ms | 1,375 ms | 2,617 ms | 12.04 req/s |
| 64 | 64 | 100% | 0 | 0 | 1,340 ms | 1,834 ms | 6,246 ms | 10.12 req/s |
| 96 | 96 | 100% | 0 | 0 | 1,647 ms | 3,361 ms | 6,760 ms | 14.00 req/s |

### Sustained concurrent wave

| Concurrency | Requests | Success | `429` | `5xx` | Median | p95 | Max | Throughput |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 16 | 120 | 100% | 0 | 0 | 673 ms | 1,175 ms | 2,279 ms | 19.29 req/s |

## Tool tests

| Test | Result |
|---|---|
| Basic tool request | Passed |
| Tool result sent back to `/agent/chat` | Passed |
| Final response after tool result | Passed |
| Select correct tool from two tools | Passed |
| Tool execution error using `output-error` | Passed |
| 64,429-character tool result | Passed |
| Two parallel tool calls in one model response | Passed |

### Parallel tool frame result

The agent returned two separate `tool-input-available` frames in one response:

```text
tool_alpha {"key":"K1"}
tool_beta  {"key":"K1"}
```

### Tool error result

An assistant tool part with:

```json
{
  "state": "output-error",
  "errorText": "CONTROLLED_TOOL_FAILURE"
}
```

was accepted. The endpoint returned HTTP `200` and generated a final text response describing the failed operation.

### Large tool result

A tool output containing **64,429 characters** was accepted. The endpoint returned HTTP `200` and generated the requested final answer.

## Exact verified boundary

The measured endpoint successfully handled:

- Six different public GitHub runner IPs.
- 482 agent requests across two runs.
- A burst of 96 simultaneous requests with 96/96 success.
- A 120-request wave at concurrency 16 with 120/120 success.
- Parallel tool calls.
- Tool errors.
- A 64 KB tool result.
- Full tool-result round trips through the same `/agent/chat` endpoint.

No `429`, authentication challenge, or server error appeared within these measured boundaries.
