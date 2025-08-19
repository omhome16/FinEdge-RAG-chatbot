## Purpose

This folder contains the **golden question set** (curated ground truth) used for manual and automated evaluation of retrieval + answer quality for RAG and finetuned models.

## Schema (fields for CSV / JSONL)

Each row/document in the golden set must include the following fields (CSV header / JSON keys):

- `qid` — unique question id (string)
- `question` — the question text (string)
- `vertical` — one of: `regulatory`, `equity` (string)
- `doc_refs` — optional; canonical doc ids or URLs the question is intended to target (array or pipe‑separated string)
- `expected_answer_traits` — short descriptors (array or semicolon delimited string), e.g. `numeric;table_lookup;footnote`; these guide evaluation rules
- `expected_answer` — the canonical answer (string). For "insufficient evidence" cases this should be `INSUFFICIENT_EVIDENCE` and an explanation in `evaluation_notes`.
- `answer_span` — optional: character offsets or sentence index in the referenced document(s) that support the expected answer (string)
- `citations` — list of canonical doc ids and optional spans that justify the answer (array/string)
- `numeric_tolerance` — optional numeric tolerance for numeric answers (e.g., `+-0.5%` or absolute `+-1000`)
- `difficulty` — `easy`/`medium`/`hard` (string)
- `taxonomy_labels` — comma separated taxonomy tags, e.g., `table_lookup,footnote,comparative`
- `evaluation_notes` — instructions for graders / edge cases (string)

### Example rows (CSV & JSONL)

**CSV header (first line)**

```
qid,question,vertical,doc_refs,expected_answer_traits,expected_answer,answer_span,citations,numeric_tolerance,difficulty,taxonomy_labels,evaluation_notes
```

**CSV example row**

```
reg-0001,"What was the total revenue reported by XYZ Corp in FY2023 (in USD)?",equity,https://www.sec.gov/Archives/xyz-10k.html,numeric;table_lookup,123456789,"Table 5, row 'Total Revenue'",https://www.sec.gov/Archives/xyz-10k.html#table5,+-0.5%,easy,table_lookup;numeric,"Use XBRL primary if available; prefer consolidated statements"
```

**JSONL example**

```json
{ "qid": "reg-0001", "question": "What was the total revenue reported by XYZ Corp in FY2023 (in USD)?", "vertical": "equity", "doc_refs": ["https://www.sec.gov/Archives/xyz-10k.html"], "expected_answer_traits": ["numeric","table_lookup"], "expected_answer": "123456789", "answer_span": "Table 5, row 'Total Revenue'", "citations": ["https://www.sec.gov/Archives/xyz-10k.html#table5"], "numeric_tolerance": "+-0.5%", "difficulty": "easy", "taxonomy_labels": ["table_lookup","numeric"], "evaluation_notes": "Use XBRL primary if available; prefer consolidated statements" }
```

### Guidelines for question curation

- Aim for 60–120 questions total across both verticals; balance numeric/table questions (\~30%), definitional/interpretive (\~30%), time‑bounded and cross‑doc (\~20%), and edge cases like "insufficient evidence" (\~10%).
- Tag each question with `taxonomy_labels` to enable stratified evaluation.
- Clearly mark questions that must be answered `INSUFFICIENT_EVIDENCE` when the document set does not contain supporting facts.

---