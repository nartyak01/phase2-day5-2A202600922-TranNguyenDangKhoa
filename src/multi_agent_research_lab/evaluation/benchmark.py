"""Benchmark for single-agent vs multi-agent."""

from __future__ import annotations

import re
from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState

Runner = Callable[[str], ResearchState]

_INPUT_COST_PER_TOKEN = 0.15 / 1_000_000
_OUTPUT_COST_PER_TOKEN = 0.60 / 1_000_000


def _sum_tokens(state: ResearchState) -> tuple[int, int, float | None]:
    total_input = 0
    total_output = 0
    for event in state.trace:
        payload = event.get("payload", {})
        total_input += int(payload.get("input_tokens") or 0)
        total_output += int(payload.get("output_tokens") or 0)
    cost = None
    if total_input or total_output:
        cost = (total_input * _INPUT_COST_PER_TOKEN) + (total_output * _OUTPUT_COST_PER_TOKEN)
    return total_input, total_output, cost


def _citation_coverage(state: ResearchState) -> float:
    if not state.final_answer or not state.sources:
        return 0.0
    cited = sum(
        1
        for source in state.sources
        if (source.url and source.url in state.final_answer)
        or source.title.lower() in state.final_answer.lower()
    )
    return cited / len(state.sources)


def _word_count(text: str | None) -> int:
    if not text:
        return 0
    return len(re.findall(r"\w+", text))


def _estimate_quality(
    state: ResearchState,
    run_name: str,
    citation_cov: float,
    failed: bool,
) -> float:
    if failed or not state.final_answer:
        return 0.0

    score = 6.5
    if _word_count(state.final_answer) >= 400:
        score += 0.5
    if citation_cov >= 0.8:
        score += 1.5
    elif citation_cov >= 0.4:
        score += 1.0
    elif citation_cov > 0:
        score += 0.5
    if run_name.startswith("multi-agent") and state.route_history:
        score += 0.5
    if state.errors:
        score -= 2.0
    return min(10.0, max(0.0, score))


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency, cost, citation coverage, and failure rate."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started

    total_input, total_output, cost = _sum_tokens(state)
    citation_cov = _citation_coverage(state)
    failed = bool(state.errors) or not state.final_answer
    quality = _estimate_quality(state, run_name, citation_cov, failed)

    notes_parts = [
        f"errors={len(state.errors)}",
        f"routes={state.route_history}",
        f"tokens_in={total_input}",
        f"tokens_out={total_output}",
        f"citation_cov={citation_cov:.0%}",
        f"words={_word_count(state.final_answer)}",
    ]
    if failed:
        notes_parts.append("status=FAIL")
    else:
        notes_parts.append("status=OK")

    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=cost,
        quality_score=quality,
        notes="; ".join(notes_parts),
    )
    return state, metrics


def run_all_benchmarks(
    queries: list[str],
    baseline_runner: Runner,
    multi_agent_runner: Runner,
) -> list[tuple[ResearchState, BenchmarkMetrics]]:
    """Run baseline and multi-agent for each query."""

    results: list[tuple[ResearchState, BenchmarkMetrics]] = []
    for index, query in enumerate(queries, start=1):
        baseline = run_benchmark(f"baseline-q{index}", query, baseline_runner)
        multi = run_benchmark(f"multi-agent-q{index}", query, multi_agent_runner)
        results.extend([baseline, multi])
    return results
