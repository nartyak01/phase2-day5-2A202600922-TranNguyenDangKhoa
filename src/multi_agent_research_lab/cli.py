"""Command-line entrypoint for the lab starter."""

from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from typing import Annotated

import typer
import yaml
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_all_benchmarks
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.services.llm_client import LLMClient

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()

_CONFIG_PATH = Path("configs/lab_default.yaml")
_REPORTS_DIR = Path("reports")


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


def _run_baseline(query: str) -> ResearchState:
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    client = LLMClient()
    started = perf_counter()
    response = client.complete(
        system_prompt=(
            "You are a research assistant. Answer the user's question thoroughly. "
            "Include key claims and mention sources if you know them."
        ),
        user_prompt=query,
    )
    latency = perf_counter() - started
    state.final_answer = response.content
    state.add_trace_event(
        "baseline.complete",
        {
            "latency_seconds": latency,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": response.cost_usd,
            "model": get_settings().openai_model,
        },
    )
    return state


def _run_multi_agent(query: str) -> ResearchState:
    state = ResearchState(request=ResearchQuery(query=query))
    return MultiAgentWorkflow().run(state)


def _load_benchmark_queries() -> list[str]:
    if not _CONFIG_PATH.exists():
        return [
            "Research GraphRAG state-of-the-art and write a 500-word summary",
        ]
    data = yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8"))
    return list(data.get("benchmark", {}).get("queries", []))


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a single-agent baseline."""

    _init()
    state = _run_baseline(query)
    console.print(Panel.fit(state.final_answer or "(empty)", title="Single-Agent Baseline"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
    save_trace: Annotated[bool, typer.Option("--save-trace", help="Save trace JSON to reports/")] = False,
) -> None:
    """Run the multi-agent workflow."""

    _init()
    try:
        result = _run_multi_agent(query)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc

    if save_trace:
        _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        trace_path = _REPORTS_DIR / "trace.json"
        trace_path.write_text(
            json.dumps({"query": query, "trace": result.trace, "route_history": result.route_history}, indent=2),
            encoding="utf-8",
        )
        console.print(f"Trace saved to {trace_path}")

    console.print(result.model_dump_json(indent=2))


@app.command()
def benchmark(
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Markdown report path"),
    ] = _REPORTS_DIR / "benchmark_report.md",
    queries: Annotated[
        int | None,
        typer.Option("--queries", help="Limit number of benchmark queries"),
    ] = None,
) -> None:
    """Run baseline vs multi-agent benchmark and write a report."""

    _init()
    query_list = _load_benchmark_queries()
    if queries is not None:
        query_list = query_list[:queries]

    console.print(f"Running benchmark on {len(query_list)} queries...")
    results = run_all_benchmarks(query_list, _run_baseline, _run_multi_agent)
    metrics = [item[1] for item in results]

    report = render_markdown_report(metrics, model=get_settings().openai_model)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")

    trace_path = output.parent / "benchmark_traces.json"
    trace_path.write_text(
        json.dumps(
            [
                {
                    "run_name": m.run_name,
                    "query": query_list[(i // 2)],
                    "route_history": s.route_history,
                    "errors": s.errors,
                    "trace": s.trace,
                }
                for i, (s, m) in enumerate(results)
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    console.print(Panel.fit(f"Report written to {output}\nTraces: {trace_path}", title="Benchmark Complete"))


if __name__ == "__main__":
    app()
