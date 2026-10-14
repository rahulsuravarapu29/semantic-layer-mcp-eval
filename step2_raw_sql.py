"""STEP 2: Pretend 5 different AI attempts write their OWN SQL for:
   "What was Maya's revenue in September 2026?"
Correct answer (our answer key) = 1200
"""
import sqlite3
con = sqlite3.connect("quickbooks.db")

attempts = {
"A. Forgot to filter by company": """
    SELECT SUM(invoice_total) FROM invoices
    WHERE invoice_date LIKE '2026-09%'
""",
"B. Joined to line items, then summed invoice_total (fan-out)": """
    SELECT SUM(i.invoice_total)
    FROM invoices i JOIN invoice_lines l ON i.invoice_id = l.invoice_id
    WHERE i.company_id = 1 AND i.invoice_date LIKE '2026-09%'
""",
"C. Searched for the account NAME 'Sales'": """
    SELECT SUM(l.amount)
    FROM invoice_lines l JOIN accounts a ON l.account_id = a.account_id
    JOIN invoices i ON i.invoice_id = l.invoice_id
    WHERE a.account_name = 'Sales' AND i.company_id = 1
      AND i.invoice_date LIKE '2026-09%'
""",
"D. Decided refunds don't count": """
    SELECT SUM(invoice_total) FROM invoices
    WHERE company_id = 1 AND invoice_date LIKE '2026-09%' AND invoice_total > 0
""",
"E. Got everything right": """
    SELECT SUM(invoice_total) FROM invoices
    WHERE company_id = 1 AND invoice_date LIKE '2026-09%'
""",
}

for name, sql in attempts.items():
    result = con.execute(sql).fetchone()[0]
    mark = "CORRECT" if result == 1200 else "WRONG"
    print(f"{name:65s} -> {result:>7}   {mark}")
