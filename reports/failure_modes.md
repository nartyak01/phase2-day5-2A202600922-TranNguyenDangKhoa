# Failure Modes & Fixes

Tài liệu này đáp ứng deliverable **giải thích failure mode và cách fix** cho Lab 20.

---

## 1. Search trả về nguồn kém hoặc API fail

**Triệu chứng:** `research_notes` mơ hồ, Analyst phân tích sai, Writer không có URL thật để cite.

**Nguyên nhân:** `TAVILY_API_KEY` thiếu/hết quota, hoặc query quá rộng khiến snippets không liên quan.

**Cách fix đã implement:**
- `SearchClient` fallback sang mock sources khi không có key hoặc API lỗi (`search_client.py`).
- Giới hạn `max_sources` trong `ResearchQuery` để tránh noise.

**Cách fix thêm (nếu cần):**
- Lọc snippet theo độ dài tối thiểu.
- Retry search 1 lần trước khi fallback.

---

## 2. Multi-agent tốn token/latency hơn baseline nhưng quality không cao hơn tương xứng

**Triệu chứng:** Benchmark cho thấy multi-agent chậm 3–4x, cost cao hơn 3–4x; baseline vẫn viết được câu trả lời đủ dài.

**Nguyên nhân:** Mỗi agent là 1 LLM call riêng; overhead routing + prompt lặp lại context.

**Cách fix:**
- Chỉ dùng multi-agent cho query phức tạp (research dài, cần citation).
- So sánh công bằng: giới hạn **tổng token budget** giữa baseline và multi-agent.
- Dùng model rẻ hơn cho Supervisor (rule-based, không cần LLM — đã làm).

---

## 3. Supervisor loop / hết `max_iterations` trước khi Writer xong

**Triệu chứng:** `final_answer` rỗng, `route_history` dừng sớm, `errors` có thể có message từ Analyst/Writer.

**Nguyên nhân:** `MAX_ITERATIONS=6` nhưng mỗi vòng supervisor tăng `iteration`; agent fail giữa chừng.

**Cách fix:**
- Tăng `MAX_ITERATIONS` trong `.env` nếu thêm Critic agent.
- Analyst/Writer validate input và ghi `errors` thay vì loop vô ích (đã implement).
- Supervisor route `done` khi đủ `final_answer`.

---

## 4. Thiếu import / lỗi runtime khi phát triển từng agent

**Triệu chứng:** `NameError: LLMClient is not defined`, `IndentationError` trong `search_client.py`.

**Nguyên nhân:** Copy logic agent mà quên import; thân hàm không thụt lề đúng.

**Cách fix:**
- Mọi agent chỉ gọi qua `LLMClient` / `SearchClient`, không gọi OpenAI trực tiếp.
- Chạy `pytest` sau mỗi milestone.
- Dùng `python -m multi_agent_research_lab.cli multi-agent -q "..."` để smoke test end-to-end.

---

## 5. Citation coverage thấp ở baseline

**Triệu chứng:** Baseline `citation_cov=0%` vì một LLM call không có search thật.

**Nguyên nhân:** Baseline không có bước Researcher lấy URL.

**Cách fix / giải thích:**
- Đây là expected behavior — baseline không search web.
- Multi-agent có Researcher + sources → citation coverage cao hơn (điểm mạnh của decomposition).

---

## Exit ticket (Lab)

1. **Nên dùng multi-agent khi:** task nghiên cứu dài, cần nguồn/citation, cần trace từng bước để debug hoặc chấm điểm.
2. **Không nên dùng multi-agent khi:** câu hỏi ngắn, latency/cost quan trọng, hoặc một prompt đủ tốt cho task.
