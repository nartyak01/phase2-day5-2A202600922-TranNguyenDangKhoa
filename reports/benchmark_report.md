# Benchmark Report

Model: `gpt-4o-mini`  
Date: 2026-06-24  
Author: Lab 20 — Multi-Agent Research System

## Queries

| ID | Query |
|----|-------|
| q1 | Research GraphRAG state-of-the-art and write a 500-word summary |
| q2 | Compare single-agent and multi-agent workflows for customer support |
| q3 | Summarize production guardrails for LLM agents |

## Summary

| Run | Latency (s) | Cost (USD) | Quality (0-10) | Notes |
|---|---:|---:|---:|---|
| baseline-q1 | 12.29 | 0.000432 | 7.0 | errors=0; tokens_in=49; tokens_out=707; citation_cov=0%; words=554; status=OK |
| multi-agent-q1 | 37.93 | 0.001881 | 8.5 | errors=0; routes=researcher→analyst→writer→done; citation_cov=100%; words=637; status=OK |
| baseline-q2 | 10.77 | 0.000442 | 7.0 | errors=0; tokens_in=44; tokens_out=725; citation_cov=0%; words=546; status=OK |
| multi-agent-q2 | 34.28 | 0.001593 | 8.0 | errors=0; routes=researcher→analyst→writer→done; citation_cov=80%; words=681; status=OK |
| baseline-q3 | 6.94 | 0.000344 | 6.5 | errors=0; tokens_in=44; tokens_out=563; citation_cov=0%; words=401; status=OK |
| multi-agent-q3 | 32.45 | 0.001554 | 8.5 | errors=0; routes=researcher→analyst→writer→done; citation_cov=100%; words=610; status=OK |

**Quality rubric (tự chấm):** structure, citation coverage, độ dài phù hợp, không lỗi pipeline.

## Analysis

### Latency

- Average baseline latency: **10.00s**
- Average multi-agent latency: **34.89s**
- Multi-agent is **3.5x** slower on average

### Cost

- Average baseline cost: **$0.000406**
- Average multi-agent cost: **$0.001676**
- Multi-agent costs **~4.1x** more (nhiều LLM calls + search)

### Quality

- Average baseline quality: **6.8 / 10**
- Average multi-agent quality: **8.3 / 10**
- Multi-agent tốt hơn chủ yếu nhờ **citation từ sources thật** và cấu trúc research → analysis → write

### Citation coverage

| Run | Citation cov |
|-----|-------------|
| multi-agent-q1 | 100% |
| multi-agent-q2 | 80% |
| multi-agent-q3 | 100% |
| baseline (all) | 0% (không có bước search) |

### When to use multi-agent

- Query nghiên cứu dài, cần nguồn và citation.
- Cần trace/debug từng bước (Researcher / Analyst / Writer).
- Peer review hoặc grading theo rubric từng agent.

### When single-agent is enough

- Câu hỏi ngắn, cần latency thấp.
- Không cần web search hoặc citation chính xác.
- Cost-sensitive workloads.

## Trace artifacts

- `reports/trace.json` — trace mẫu 1 query multi-agent
- `reports/benchmark_traces.json` — trace đầy đủ 6 runs
- `reports/trace_summary.md` — mô tả luồng trace (dùng chụp màn hình nộp bài)

## Failure Modes (chi tiết)

Xem `reports/failure_modes.md` — gồm 5 failure mode và cách fix đã áp dụng trong code.

## Exit ticket

1. **Nên multi-agent:** task research phức tạp, cần sources + phân tích + viết riêng, cần audit trail.
2. **Không nên multi-agent:** FAQ đơn giản, chat nhanh, hoặc khi 1 prompt đủ tốt và cost/latency quan trọng hơn citation.
