"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(
    metrics: list[BenchmarkMetrics],
    *,
    model: str = "gpt-4o-mini",
    extra_sections: str = "",
) -> str:
    """Render benchmark metrics and analysis to markdown."""

    lines = [
        "# Benchmark Report",
        "",
        f"Model: `{model}`",
        "",
        "## Summary",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality | Notes |",
        "|---|---:|---:|---:|---|",
    ]

    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.6f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        lines.append(
            f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} | {item.notes} |"
        )

    baseline_latencies = [m.latency_seconds for m in metrics if m.run_name.startswith("baseline")]
    multi_latencies = [m.latency_seconds for m in metrics if m.run_name.startswith("multi-agent")]
    baseline_costs = [m.estimated_cost_usd or 0 for m in metrics if m.run_name.startswith("baseline")]
    multi_costs = [m.estimated_cost_usd or 0 for m in metrics if m.run_name.startswith("multi-agent")]

    lines.extend(
        [
            "",
            "## Analysis",
            "",
            "### Latency",
            "",
        ]
    )
    if baseline_latencies and multi_latencies:
        avg_baseline = sum(baseline_latencies) / len(baseline_latencies)
        avg_multi = sum(multi_latencies) / len(multi_latencies)
        lines.append(
            f"- Average baseline latency: **{avg_baseline:.2f}s**"
        )
        lines.append(
            f"- Average multi-agent latency: **{avg_multi:.2f}s**"
        )
        if avg_baseline > 0:
            lines.append(
                f"- Multi-agent is **{avg_multi / avg_baseline:.1f}x** slower on average"
            )

    lines.extend(["", "### Cost", ""])
    if baseline_costs and multi_costs:
        avg_baseline_cost = sum(baseline_costs) / len(baseline_costs)
        avg_multi_cost = sum(multi_costs) / len(multi_costs)
        lines.append(f"- Average baseline cost: **${avg_baseline_cost:.6f}**")
        lines.append(f"- Average multi-agent cost: **${avg_multi_cost:.6f}**")

    lines.extend(
        [
            "",
            "### When to use multi-agent",
            "",
            "- Complex research queries requiring separate search, analysis, and writing stages.",
            "- When traceability per agent step matters for debugging or grading.",
            "",
            "### When single-agent is enough",
            "",
            "- Short factual questions with low latency/cost requirements.",
            "- Tasks where decomposition overhead exceeds quality gains.",
            "",
            "## Failure Modes",
            "",
            "1. **Weak search results** → Analyst builds on poor evidence. "
            "*Fix:* mock/Tavily fallback and source filtering.",
            "2. **Token budget unfairness** → multi-agent uses more calls. "
            "*Fix:* compare with equal total token caps in future runs.",
            "3. **Max iteration guard** → workflow stops before Writer completes. "
            "*Fix:* raise `MAX_ITERATIONS` or optimize routing.",
            "",
        ]
    )

    if extra_sections:
        lines.extend(["", extra_sections])

    return "\n".join(lines) + "\n"
