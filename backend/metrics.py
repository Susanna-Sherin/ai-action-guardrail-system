import time

metrics = {
    "requests": 0,
    "allowed": 0,
    "blocked": 0,
    "hitl": 0,
    "prompt_tokens": 0,
    "response_time_ms": []
}


def estimate_tokens(text: str):
    # Approximation: ~1 token per 4 characters
    return max(1, len(text) // 4)


def start_timer():
    return time.perf_counter()


def end_timer(start):
    elapsed = (time.perf_counter() - start) * 1000
    metrics["response_time_ms"].append(round(elapsed, 2))
    return elapsed


def average_latency():
    if not metrics["response_time_ms"]:
        return 0

    return round(
        sum(metrics["response_time_ms"])
        / len(metrics["response_time_ms"]),
        2
    )