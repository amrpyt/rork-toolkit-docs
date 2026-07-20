import concurrent.futures
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.request
import uuid
from typing import Optional

BASE_URL = "https://toolkit.rork.com"
AGENT_URL = f"{BASE_URL}/agent/chat"
TIMEOUT_SECONDS = 45


def log(event: str, **data):
    payload = {
        "event": event,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "timestamp": time.time(),
        **data,
    }
    print("RORK_TEST " + json.dumps(payload, ensure_ascii=False, sort_keys=True), flush=True)


def http_json(url: str, payload: Optional[dict] = None, timeout: int = TIMEOUT_SECONDS):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"User-Agent": "rork-toolkit-docs-controlled-test/1.0"}
    method = "GET"
    if body is not None:
        method = "POST"
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            return {
                "status": response.status,
                "headers": {key.lower(): value for key, value in response.headers.items()},
                "body": raw,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        return {
            "status": exc.code,
            "headers": ({key.lower(): value for key, value in exc.headers.items()} if exc.headers else {}),
            "body": exc.read(),
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "error": f"HTTPError: {exc}",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "status": 0,
            "headers": {},
            "body": b"",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "error": f"{type(exc).__name__}: {exc}",
        }


def parse_stream(raw: bytes):
    frames = []
    text = raw.decode("utf-8", errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            frames.append({"type": "[DONE]"})
            continue
        try:
            frames.append(json.loads(data))
        except json.JSONDecodeError:
            frames.append({"type": "unparsed", "raw": data})
    return frames


def extract_text(frames):
    chunks = []
    for frame in frames:
        if frame.get("type") == "text-delta":
            chunks.append(str(frame.get("delta", "")))
    return "".join(chunks)


def make_user_message(text: str):
    return {
        "id": "u-" + uuid.uuid4().hex[:12],
        "role": "user",
        "parts": [{"type": "text", "text": text}],
    }


def agent_request(messages, tools=None):
    payload = {"messages": messages}
    if tools is not None:
        payload["tools"] = tools
    result = http_json(AGENT_URL, payload)
    result["frames"] = parse_stream(result["body"])
    result["text"] = extract_text(result["frames"])
    return result


def public_egress_ip():
    result = http_json("https://api.ipify.org?format=json", None, timeout=15)
    if result["status"] != 200:
        return {"status": result["status"], "error": result["error"], "ip": None}
    try:
        return {"status": 200, "error": None, "ip": json.loads(result["body"])["ip"]}
    except Exception as exc:  # noqa: BLE001
        return {"status": result["status"], "error": str(exc), "ip": None}


def request_exact(marker: str):
    result = agent_request([make_user_message(f"Reply exactly {marker}")])
    return {
        "status": result["status"],
        "latency_ms": result["latency_ms"],
        "text": result["text"],
        "has_marker": marker in result["text"],
        "error": result["error"],
        "stream_header": result["headers"].get("x-vercel-ai-ui-message-stream"),
        "frame_types": [frame.get("type") for frame in result["frames"]],
    }


def run_wave(concurrency: int, count: int):
    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(request_exact, f"LOAD_OK_{concurrency}_{index}") for index in range(count)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    elapsed = time.perf_counter() - started

    statuses = {}
    for item in results:
        statuses[str(item["status"])] = statuses.get(str(item["status"]), 0) + 1
    latencies = [item["latency_ms"] for item in results]
    success = sum(item["status"] == 200 and item["has_marker"] for item in results)
    throttled = sum(item["status"] == 429 for item in results)
    server_errors = sum(500 <= item["status"] <= 599 for item in results)
    summary = {
        "concurrency": concurrency,
        "count": count,
        "elapsed_s": round(elapsed, 2),
        "throughput_rps": round(count / elapsed, 2) if elapsed else None,
        "success": success,
        "success_rate": round(success / count, 4),
        "throttled": throttled,
        "server_errors": server_errors,
        "statuses": statuses,
        "latency_min_ms": min(latencies),
        "latency_median_ms": round(statistics.median(latencies), 2),
        "latency_p95_ms": round(sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)], 2),
        "latency_max_ms": max(latencies),
    }
    log("load_wave", **summary)
    return summary


def test_00_runner_identity():
    identity = public_egress_ip()
    log(
        "runner_identity",
        egress_ip=identity["ip"],
        ip_lookup_status=identity["status"],
        ip_lookup_error=identity["error"],
        github_run_id=os.getenv("GITHUB_RUN_ID"),
        github_job=os.getenv("GITHUB_JOB"),
        github_repository=os.getenv("GITHUB_REPOSITORY"),
    )
    assert identity["status"] == 200
    assert identity["ip"]


def test_01_agent_smoke():
    marker = "RORK_REMOTE_SMOKE_OK"
    result = request_exact(marker)
    log("agent_smoke", **result)
    assert result["status"] == 200
    assert result["stream_header"] == "v1"
    assert result["has_marker"]


def test_02_tool_call_and_result_roundtrip():
    tool_name = "echo_value"
    requested_value = "TOOL_INPUT_42"
    final_marker = "TOOL_ROUNDTRIP_OK"
    user_message = make_user_message(
        f"Call {tool_name} with value {requested_value}. After receiving the tool result, reply exactly {final_marker}."
    )
    tools = {
        tool_name: {
            "description": "Return the provided value unchanged.",
            "jsonSchema": {
                "type": "object",
                "properties": {"value": {"type": "string"}},
                "required": ["value"],
                "additionalProperties": False,
            },
        }
    }

    first = agent_request([user_message], tools)
    available = next(
        (frame for frame in first["frames"] if frame.get("type") == "tool-input-available"),
        None,
    )
    log(
        "tool_request",
        status=first["status"],
        latency_ms=first["latency_ms"],
        frame_types=[frame.get("type") for frame in first["frames"]],
        tool_frame=available,
    )
    assert first["status"] == 200
    assert available is not None
    assert available.get("toolName") == tool_name
    assert available.get("input", {}).get("value") == requested_value

    assistant_tool_message = {
        "id": "a-" + uuid.uuid4().hex[:12],
        "role": "assistant",
        "parts": [
            {
                "type": f"tool-{tool_name}",
                "toolCallId": available["toolCallId"],
                "state": "output-available",
                "input": available["input"],
                "output": {"echoed": requested_value, "instruction": final_marker},
            }
        ],
    }
    second = agent_request([user_message, assistant_tool_message], tools)
    log(
        "tool_roundtrip",
        status=second["status"],
        latency_ms=second["latency_ms"],
        text=second["text"],
        frame_types=[frame.get("type") for frame in second["frames"]],
    )
    assert second["status"] == 200
    assert final_marker in second["text"]


def test_03_controlled_capacity_profile():
    version = (sys.version_info.major, sys.version_info.minor)
    if version == (3, 9):
        levels = [(1, 2), (2, 4)]
    elif version == (3, 10):
        levels = [
            (1, 1),
            (2, 2),
            (4, 4),
            (8, 8),
            (16, 16),
            (32, 32),
            (64, 64),
            (96, 96),
        ]
    else:
        levels = [(16, 120)]

    summaries = []
    for concurrency, count in levels:
        summary = run_wave(concurrency, count)
        summaries.append(summary)
        if summary["throttled"] > 0 or summary["server_errors"] > 0:
            log("capacity_stop", reason="throttle_or_server_error", at_concurrency=concurrency)
            break
        if summary["success_rate"] < 0.9:
            log("capacity_stop", reason="success_rate_below_90_percent", at_concurrency=concurrency)
            break

    assert summaries
    assert summaries[0]["success"] > 0


def test_04_multiple_tool_choice():
    if (sys.version_info.major, sys.version_info.minor) != (3, 9):
        return

    tools = {
        "echo_value": {
            "description": "Echo a value.",
            "jsonSchema": {
                "type": "object",
                "properties": {"value": {"type": "string"}},
                "required": ["value"],
                "additionalProperties": False,
            },
        },
        "lookup_order": {
            "description": "Look up one order by orderId.",
            "jsonSchema": {
                "type": "object",
                "properties": {"orderId": {"type": "string"}},
                "required": ["orderId"],
                "additionalProperties": False,
            },
        },
    }
    result = agent_request(
        [make_user_message("Call lookup_order with orderId ORD-1001. Do not call echo_value.")],
        tools,
    )
    calls = [frame for frame in result["frames"] if frame.get("type") == "tool-input-available"]
    log(
        "multiple_tool_choice",
        status=result["status"],
        latency_ms=result["latency_ms"],
        calls=calls,
    )
    assert result["status"] == 200
    assert calls
    assert calls[0].get("toolName") == "lookup_order"
    assert calls[0].get("input", {}).get("orderId") == "ORD-1001"


def test_05_tool_error_result():
    if (sys.version_info.major, sys.version_info.minor) != (3, 9):
        return

    tool_name = "failing_tool"
    user_message = make_user_message(
        "Call failing_tool with operation test. After the error, explain briefly that the operation failed."
    )
    tools = {
        tool_name: {
            "description": "A test tool that returns an execution error.",
            "jsonSchema": {
                "type": "object",
                "properties": {"operation": {"type": "string"}},
                "required": ["operation"],
                "additionalProperties": False,
            },
        }
    }
    first = agent_request([user_message], tools)
    available = next(
        (frame for frame in first["frames"] if frame.get("type") == "tool-input-available"),
        None,
    )
    assert available is not None

    error_message = {
        "id": "a-" + uuid.uuid4().hex[:12],
        "role": "assistant",
        "parts": [
            {
                "type": f"tool-{tool_name}",
                "toolCallId": available["toolCallId"],
                "state": "output-error",
                "input": available["input"],
                "errorText": "CONTROLLED_TOOL_FAILURE",
            }
        ],
    }
    second = agent_request([user_message, error_message], tools)
    log(
        "tool_error_result",
        status=second["status"],
        latency_ms=second["latency_ms"],
        text=second["text"],
        frame_types=[frame.get("type") for frame in second["frames"]],
    )
    assert second["status"] == 200
    assert second["text"].strip()


def test_06_large_tool_result():
    if (sys.version_info.major, sys.version_info.minor) != (3, 9):
        return

    tool_name = "get_report"
    final_marker = "LARGE_RESULT_OK"
    user_message = make_user_message(
        f"Call get_report with reportId R-1. After reading the result, reply exactly {final_marker}."
    )
    tools = {
        tool_name: {
            "description": "Get a text report.",
            "jsonSchema": {
                "type": "object",
                "properties": {"reportId": {"type": "string"}},
                "required": ["reportId"],
                "additionalProperties": False,
            },
        }
    }
    first = agent_request([user_message], tools)
    available = next(
        (frame for frame in first["frames"] if frame.get("type") == "tool-input-available"),
        None,
    )
    assert available is not None

    large_text = ("report-data-0123456789 " * 2800) + "\nInstruction: " + final_marker
    output_message = {
        "id": "a-" + uuid.uuid4().hex[:12],
        "role": "assistant",
        "parts": [
            {
                "type": f"tool-{tool_name}",
                "toolCallId": available["toolCallId"],
                "state": "output-available",
                "input": available["input"],
                "output": {"content": large_text},
            }
        ],
    }
    second = agent_request([user_message, output_message], tools)
    log(
        "large_tool_result",
        payload_chars=len(large_text),
        status=second["status"],
        latency_ms=second["latency_ms"],
        text=second["text"],
    )
    assert second["status"] == 200
    assert final_marker in second["text"]


def test_07_parallel_tool_request_observation():
    if (sys.version_info.major, sys.version_info.minor) != (3, 9):
        return

    tools = {
        "tool_alpha": {
            "description": "Return alpha data.",
            "jsonSchema": {
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": ["key"],
            },
        },
        "tool_beta": {
            "description": "Return beta data.",
            "jsonSchema": {
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": ["key"],
            },
        },
    }
    result = agent_request(
        [make_user_message("Call both tool_alpha and tool_beta, each with key K1, before answering.")],
        tools,
    )
    calls = [frame for frame in result["frames"] if frame.get("type") == "tool-input-available"]
    log(
        "parallel_tool_request",
        status=result["status"],
        latency_ms=result["latency_ms"],
        call_count=len(calls),
        calls=calls,
    )
    assert result["status"] == 200
    assert calls
