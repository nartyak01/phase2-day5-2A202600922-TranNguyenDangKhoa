# Design Template

## Problem

Xây dựng research assistant nhận câu hỏi nghiên cứu dài, tìm nguồn, phân tích và viết câu trả lời cuối. Hệ thống phải so sánh được **single-agent baseline** với **multi-agent workflow** theo latency, cost, quality và traceability.

## Why multi-agent?

Single-agent gộp search + phân tích + viết trong một prompt dài → khó debug từng bước, dễ bỏ sót citation, khó kiểm soát chất lượng từng giai đoạn. Multi-agent tách role rõ ràng: Researcher thu thập nguồn, Analyst đánh giá evidence, Writer tổng hợp — mỗi bước có output riêng trong shared state và trace.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Route agent tiếp theo, enforce max iterations | `ResearchState` hiện tại | `route_history` entry | Loop vô hạn → fix bằng `max_iterations` |
| Researcher | Search + tóm tắt nguồn | `request.query` | `sources`, `research_notes` | Search fail → mock fallback |
| Analyst | Trích claims, so sánh viewpoints | `research_notes` | `analysis_notes` | Thiếu notes → ghi `errors` |
| Writer | Viết câu trả lời cuối có citation | `analysis_notes`, `sources` | `final_answer` | Thiếu analysis → skip |

## Shared state

| Field | Lý do |
|---|---|
| `request` | Câu hỏi gốc và config (max_sources, audience) |
| `sources` | Nguồn từ search cho citation |
| `research_notes` | Output Researcher cho Analyst |
| `analysis_notes` | Output Analyst cho Writer |
| `final_answer` | Kết quả cuối |
| `route_history` | Debug routing Supervisor |
| `trace` | Latency, tokens, cost per step |
| `errors` | Failure tracking cho benchmark |

## Routing policy

```text
supervisor → researcher → supervisor → analyst → supervisor → writer → supervisor → done
```

Rule-based:
- Chưa có `research_notes` → researcher
- Có research, chưa `analysis_notes` → analyst
- Có analysis, chưa `final_answer` → writer
- Đủ output hoặc `iteration >= max_iterations` → done

## Guardrails

- Max iterations: `6` (`.env` `MAX_ITERATIONS`)
- Timeout: `60s` per LLM call (`.env` `TIMEOUT_SECONDS`)
- Retry: `tenacity` 3 lần trên `LLMClient.complete`
- Fallback: mock search khi không có `TAVILY_API_KEY` hoặc API fail
- Validation: Analyst/Writer kiểm tra field bắt buộc trước khi chạy

## Benchmark plan

| Query | Metric | Expected |
|---|---|---|
| GraphRAG 500-word summary | latency, cost, citation_cov | multi chậm hơn, quality tốt hơn hoặc bằng |
| Single vs multi for customer support | token usage | baseline rẻ hơn |
| Production guardrails for LLM agents | failure rate | multi trace rõ hơn |

Chạy: `python -m multi_agent_research_lab.cli benchmark`
