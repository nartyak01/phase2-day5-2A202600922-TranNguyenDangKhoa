# Trace Summary — Multi-Agent Workflow

Deliverable: **screenshot trace** — file `reports/trace_summary_screenshot.png`

**Query mẫu:** `Research GraphRAG state-of-the-art and write a 500-word summary`

**File trace JSON:** `reports/trace.json`  
**File benchmark traces:** `reports/benchmark_traces.json`

---

## Route history

```text
researcher → analyst → writer → done
```

4 bước supervisor (iteration 1–4), mỗi worker chạy đúng 1 lần.

---

## Trace timeline

| Step | Agent | Chi tiết |
|------|-------|----------|
| 1 | supervisor | route=`researcher`, iteration=1 |
| 2 | researcher | 5 sources, 749 in / 620 out tokens, ~$0.00048, **10.96s** |
| 3 | supervisor | route=`analyst`, iteration=2 |
| 4 | analyst | 673 in / 827 out tokens, ~$0.00060, **13.67s** |
| 5 | supervisor | route=`writer`, iteration=3 |
| 6 | writer | 1056 in / 904 out tokens, ~$0.00070, **13.72s** |
| 7 | supervisor | route=`done`, iteration=4 |

**Tổng ước lượng:** ~2478 input tokens, ~2351 output tokens, ~$0.00178 USD, wall-clock ~38s

---

## Ai làm gì?

| Agent | Input | Output trong state |
|-------|-------|-------------------|
| **Supervisor** | Kiểm tra field thiếu | `route_history` |
| **Researcher** | Query + Tavily search | `sources`, `research_notes` |
| **Analyst** | `research_notes` | `analysis_notes` (claims, evidence) |
| **Writer** | `analysis_notes` + sources | `final_answer` (~500 từ, có references) |

---

## Cách tái tạo trace

```powershell
python -m multi_agent_research_lab.cli multi-agent `
  -q "Research GraphRAG state-of-the-art and write a 500-word summary" `
  --save-trace
```

Log console sẽ hiện:

```text
trace_span supervisor.route duration=...
trace_span researcher.run duration=...
trace_span analyst.run duration=...
trace_span writer.run duration=...
```

**Nộp bài:** đính kèm `reports/trace_summary_screenshot.png` hoặc file JSON `reports/trace.json`.
