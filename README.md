# Semantic Layer + MCP + Evaluation: a small prototype

**Question:** Can an AI agent reliably answer business questions over invoicing data? And if we put a governed semantic layer in front of the data, where does it still fall short?

This repo is a small, runnable prototype that answers that question end to end: a toy multi-tenant invoicing dataset, a semantic layer, an MCP server that exposes it to an AI agent, and an evaluation with a golden answer set and a gap matrix.

## The approach

| Step | File | What it does |
|---|---|---|
| 1. Data | `step1_build_db.py` | Two businesses (multi-tenant), custom account names mapped to standard types (a tiny ontology), invoices with multiple line items, a refund, an unpaid invoice |
| 2. Break it | `step2_raw_sql.py` | Five plausible raw-SQL attempts at the same question ("Maya's September revenue") produce five different answers |
| 3. Semantic layer | `semantic_layer.yaml`, `semantic.py`, `step3_demo.py` | Metrics defined once with grain, join paths and allowed dimensions; the engine generates the SQL and always injects tenant scope |
| 4. MCP server | `mcp_server.py`, `step4_agent_client.py` | The semantic layer exposed as MCP tools (`list_metrics`, `list_dimensions`, `query_metric`) and a read-only resource (`metrics://definitions`) |
| 5. Evaluation | `step5_eval.py` | 8 golden questions with an answer key; raw SQL (3 runs each) vs. semantic layer; gap matrix |

## What raw SQL got wrong (step 2)

| Attempt | Result | Failure |
|---|---|---|
| No company filter | 1,500 | Included another tenant's data (security leak) |
| Joined invoices to line items, summed invoice totals | 2,900 | Join fan-out: each invoice counted once per line item |
| Matched account *name* "Sales" | 450 | Missed "Catering Income" and the refund; fails for tenants with different names |
| Dropped refunds | 1,250 | Made up its own definition of revenue |
| Correct | 1,200 | Right this time, not guaranteed next time |

## How the semantic layer fixes it (steps 3–4)

- **One definition per metric:** `revenue = SUM(line amount) WHERE standard_type IN (REVENUE, REFUND)`
- **Ontology, not names:** uses `standard_type`, so it works across businesses that name accounts differently
- **Grain rules:** revenue is computed at line grain, invoice metrics at invoice grain, so no fan-out; disallowed combinations are refused
- **Tenant security in the server:** the MCP tool has no `company_id` parameter. Tenant scope comes from the authenticated session, so a model can't request another company's data even if it tries
- **Refuse, don't guess:** an unknown metric returns an error listing valid ones, so the agent can recover

## Results (step 5)

| Question | Raw SQL (3 runs) | Semantic layer |
|---|---|---|
| Q1 Revenue, Sep (tenant 1) | PASS fail fail | PASS |
| Q2 Revenue, Sep (tenant 2) | PASS fail fail | PASS |
| Q3 Revenue by customer | PASS fail fail | PASS |
| Q4 Invoice count | PASS fail fail | PASS |
| Q5 Unpaid amount | PASS PASS PASS | PASS |
| Q6 Revenue, fiscal Q1 | fail PASS fail | can't answer |
| Q7 Customers with a refund AND an unpaid invoice | PASS fail PASS | can't answer |
| Q8 Catering revenue only | PASS fail PASS | can't answer |

| | Raw SQL | Semantic layer |
|---|---|---|
| Correctness | 50% of runs | 100% of answered |
| Consistency | same answer on 1 of 8 questions | always |
| Coverage | 8 of 8 attempted | 5 of 8 |

**Note:** the raw-SQL attempts are hand-written to represent common failure patterns. They simulate an agent writing its own SQL; they are not measured output from a specific model.

## Gaps and recommendation

| Gap | Cause | Recommendation |
|---|---|---|
| Fiscal-period questions | No fiscal calendar | **Extend:** add a fiscal calendar dimension + business rule in the context layer |
| Relationship questions | Not a metric question | **Combine:** route to a knowledge graph |
| Revenue sub-types | Ontology too coarse | **Extend:** finer standard types (e.g., product vs. service revenue) |

**Overall:** adopt the semantic layer as the source of truth for numbers, extend it where gaps are small, combine it with a knowledge graph for relationship questions, and never fall back to raw SQL for financial figures. Uncovered questions become the roadmap.

## Run it

```bash
pip install -r requirements.txt
bash run_all.sh
```

Requires Python 3.10+.

## How this was built

Built with AI-assisted coding. I designed the problem framing, test questions, answer key, and evaluation, and reviewed every component.
