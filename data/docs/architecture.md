## Scope & Sources

This file defines the project **verticals**, primary **document sources**, example URLs, and expected incoming formats for the RAG + Finetuning pipeline.

| Source name                                        | Vertical(s)                                 | Example URL (public)                                                                | Expected format(s)            | Notes                                                                               |
| -------------------------------------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------- |
| SEC EDGAR (10‑K, 10‑Q, 8‑K, XBRL filings)          | Equity/Issuer Research                      | [https://www.sec.gov/edgar/search/](https://www.sec.gov/edgar/search/)              | HTML, plain text, XBRL (.xml) | Use company CIK / accession numbers for stable IDs. XBRL useful for numeric tables. |
| Company Annual Reports (PDF)                       | Equity/Issuer Research                      | Company IR pages (e.g., [https://investor.apple.com/](https://investor.apple.com/)) | PDF, HTML                     | PDFs often contain tables; extract with OCR if needed.                              |
| Risk Factors (sections inside 10‑K/annual reports) | Equity/Issuer Research                      | within 10‑K text                                                                    | HTML, TXT                     | Treat as document sub‑sections and preserve section headers.                        |
| RBI circulars / master directions                  | Regulatory/Compliance                       | [https://www.rbi.org.in/](https://www.rbi.org.in/)                                  | HTML, PDF                     | Indian regulations; often stable HTML pages.                                        |
| SEBI lists & circulars                             | Regulatory/Compliance                       | [https://www.sebi.gov.in/](https://www.sebi.gov.in/)                                | HTML, PDF                     | Capture effective dates & amendment history.                                        |
| FINRA rules & notices                              | Regulatory/Compliance                       | [https://www.finra.org/](https://www.finra.org/)                                    | HTML, PDF                     | US financial industry rules and notices.                                            |
| SEC rules & guidance (Reg‑S‑K, Reg‑S‑X, etc.)      | Regulatory/Compliance                       | [https://www.sec.gov/rules](https://www.sec.gov/rules)                              | HTML, PDF                     | Include dates of publication & effective date metadata.                             |
| Fund prospectuses / fee schedules                  | Equity/Issuer Research (Funds) / Compliance | Fund websites / SEC form N‑1A                                                       | PDF, HTML, CSV                | Prospectuses often include expense tables and fees.                                 |
| Press releases & investor presentations            | Equity/Issuer Research                      | Company websites (IR)                                                               | PDF, PPTX, HTML               | Use for recency; treat as separate doc type.                                        |

### Ingestion & canonicalization notes

- Canonical document ID format: `/{vertical}/{regulator_or_company}/{doc_type}/{YYYY-MM-DD}/{source_id}` — include source URL and extraction timestamp in metadata.
- Preserve original raw, parsed text, extracted tables, and original binary (PDF/XBRL) in artifact store.
- Normalize dates to ISO 8601 and currencies to ISO 4217 (store original strings too).
- For numeric tables: store both cell text and canonical numeric values (float + units; e.g., `1000000 USD`).


---