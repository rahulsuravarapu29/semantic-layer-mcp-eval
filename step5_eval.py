"""STEP 5: Evaluation. Golden questions + answer key, two approaches, gap matrix.

Business context for Q6: Maya's FISCAL year starts in SEPTEMBER,
so fiscal Q1 = Sep-Nov 2026.
"""
import sqlite3
import semantic

con = sqlite3.connect("quickbooks.db")
def sql(q):
    return [tuple(round(x, 2) if isinstance(x, float) else x for x in r)
            for r in con.execute(q).fetchall()]

def sem(*a, **k):
    rows = semantic.query_metric(*a, **k)
    return [tuple(r.values()) for r in rows]

# ---------- GOLDEN SET: question, answer key, 3 raw-SQL attempts, semantic-layer call ----------
GOLDEN = [
 ("Q1 Maya revenue, Sep 2026", [(1200.0,)],
  ["SELECT SUM(invoice_total) FROM invoices WHERE company_id=1 AND invoice_date LIKE '2026-09%'",
   "SELECT SUM(i.invoice_total) FROM invoices i JOIN invoice_lines l USING(invoice_id) WHERE i.company_id=1 AND i.invoice_date LIKE '2026-09%'",
   "SELECT SUM(invoice_total) FROM invoices WHERE invoice_date LIKE '2026-09%'"],
  lambda: sem(1, "revenue", month="2026-09")),

 ("Q2 Leo revenue, Sep 2026", [(300.0,)],
  ["SELECT SUM(invoice_total) FROM invoices WHERE company_id=2 AND invoice_date LIKE '2026-09%'",
   "SELECT SUM(l.amount) FROM invoice_lines l JOIN accounts a USING(account_id) WHERE a.company_id=2 AND a.account_name='Sales'",
   "SELECT SUM(i.invoice_total) FROM invoices i JOIN invoice_lines l USING(invoice_id) WHERE i.company_id=2"],
  lambda: sem(2, "revenue", month="2026-09")),

 ("Q3 Maya revenue by customer, Sep", [("City Office", 800.0), ("Joe's Cafe", 400.0)],
  ["SELECT c.name, SUM(i.invoice_total) FROM invoices i JOIN customers c USING(customer_id) WHERE i.company_id=1 AND i.invoice_date LIKE '2026-09%' GROUP BY c.name ORDER BY c.name",
   "SELECT c.name, SUM(i.invoice_total) FROM invoices i JOIN customers c USING(customer_id) WHERE i.company_id=1 AND i.invoice_date LIKE '2026-09%' AND i.invoice_total>0 GROUP BY c.name ORDER BY c.name",
   "SELECT c.name, SUM(i.invoice_total) FROM invoices i JOIN customers c USING(customer_id) JOIN invoice_lines l USING(invoice_id) WHERE i.company_id=1 AND i.invoice_date LIKE '2026-09%' GROUP BY c.name ORDER BY c.name"],
  lambda: sorted(sem(1, "revenue", group_by=["customer"], month="2026-09"))),

 ("Q4 Maya invoice count, Sep", [(3,)],
  ["SELECT COUNT(*) FROM invoices WHERE company_id=1 AND invoice_date LIKE '2026-09%'",
   "SELECT COUNT(*) FROM invoices i JOIN invoice_lines l USING(invoice_id) WHERE i.company_id=1 AND i.invoice_date LIKE '2026-09%'",
   "SELECT COUNT(*) FROM invoices WHERE company_id=1 AND invoice_date LIKE '2026-09%' AND invoice_total>0"],
  lambda: sem(1, "invoice_count", month="2026-09")),

 ("Q5 Maya unpaid amount", [(900.0,)],
  ["SELECT SUM(invoice_total) FROM invoices WHERE company_id=1 AND status='UNPAID'",
   "SELECT SUM(invoice_total) FROM invoices WHERE status='UNPAID'",
   "SELECT SUM(i.invoice_total) FROM invoices i JOIN invoice_lines l USING(invoice_id) WHERE i.company_id=1 AND i.status='UNPAID'"],
  lambda: sem(1, "unpaid_amount")),

 ("Q6 Maya revenue, fiscal Q1 (Sep-Nov)", [(1200.0,)],
  ["SELECT SUM(invoice_total) FROM invoices WHERE company_id=1 AND invoice_date BETWEEN '2026-07-01' AND '2026-09-30'",
   "SELECT SUM(invoice_total) FROM invoices WHERE company_id=1 AND invoice_date BETWEEN '2026-09-01' AND '2026-11-30'",
   "SELECT SUM(invoice_total) FROM invoices WHERE company_id=1 AND invoice_date LIKE '2026%'"],
  None),   # semantic layer has no fiscal calendar -> can't answer

 ("Q7 Maya customers with a refund AND an unpaid invoice", [],
  ["SELECT DISTINCT c.name FROM customers c WHERE c.company_id=1 AND EXISTS (SELECT 1 FROM invoices i WHERE i.customer_id=c.customer_id AND i.invoice_total<0) AND EXISTS (SELECT 1 FROM invoices i WHERE i.customer_id=c.customer_id AND i.status='UNPAID')",
   "SELECT DISTINCT c.name FROM customers c JOIN invoices i USING(customer_id) WHERE c.company_id=1 AND (i.invoice_total<0 OR i.status='UNPAID') ORDER BY c.name",
   "SELECT DISTINCT c.name FROM customers c WHERE c.company_id=1 AND EXISTS (SELECT 1 FROM invoices i WHERE i.customer_id=c.customer_id AND i.invoice_total<0) AND EXISTS (SELECT 1 FROM invoices i WHERE i.customer_id=c.customer_id AND i.status='UNPAID')"],
  None),   # relationship question -> not a metric

 ("Q8 Maya catering revenue only", [(1700.0,)],
  ["SELECT SUM(l.amount) FROM invoice_lines l JOIN accounts a USING(account_id) WHERE a.company_id=1 AND a.account_name='Catering Income'",
   "SELECT SUM(l.amount) FROM invoice_lines l JOIN accounts a USING(account_id) WHERE a.company_id=1 AND a.standard_type='REVENUE'",
   "SELECT SUM(l.amount) FROM invoice_lines l JOIN accounts a USING(account_id) WHERE a.company_id=1 AND a.account_name LIKE '%Catering%'"],
  None),   # ontology only knows REVENUE/REFUND/EXPENSE, not 'catering'
]

def fmt(x): return "PASS" if x else "fail"

print(f"{'Question':52s} | {'Raw SQL (3 runs)':18s} | {'Semantic layer':14s}")
print("-" * 92)
raw_correct = raw_total = raw_consistent = sem_correct = sem_answered = 0
for name, key, attempts, sem_call in GOLDEN:
    results = [sql(a) for a in attempts]
    passes = [r == key for r in results]
    raw_correct += sum(passes); raw_total += len(passes)
    raw_consistent += len(set(map(str, results))) == 1
    raw_cell = " ".join(fmt(p) for p in passes)
    if sem_call is None:
        sem_cell = "CAN'T ANSWER"
    else:
        ok = sem_call() == key
        sem_answered += 1; sem_correct += ok
        sem_cell = fmt(ok)
    print(f"{name:52s} | {raw_cell:18s} | {sem_cell}")

n = len(GOLDEN)
print("-" * 92)
print(f"\nRAW SQL AGENT:   correct {raw_correct}/{raw_total} runs ({raw_correct/raw_total:.0%}), "
      f"same answer all 3 runs on {raw_consistent}/{n} questions, answered {n}/{n}")
print(f"SEMANTIC LAYER:  correct {sem_correct}/{sem_answered} answered ({sem_correct/sem_answered:.0%}), "
      f"consistent {sem_answered}/{sem_answered}, coverage {sem_answered}/{n} ({sem_answered/n:.0%})")
