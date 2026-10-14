"""STEP 1: Build a tiny QuickBooks-style database.

Two businesses (multi-tenant!):
  company 1 = Maya's Bakery
  company 2 = Leo's Coffee

Each business names its accounts differently (that's the ontology problem).
"""
import sqlite3, os

DB = "quickbooks.db"
if os.path.exists(DB):
    os.remove(DB)
con = sqlite3.connect(DB)
cur = con.cursor()

cur.executescript("""
CREATE TABLE companies (company_id INTEGER, name TEXT);

-- Each company makes up its own account names.
-- standard_type is our ONTOLOGY mapping: what the account REALLY is.
CREATE TABLE accounts (
  account_id INTEGER, company_id INTEGER,
  account_name TEXT,      -- what the business calls it
  standard_type TEXT      -- what it means: REVENUE / REFUND / EXPENSE
);

CREATE TABLE customers (customer_id INTEGER, company_id INTEGER, name TEXT);

-- One invoice = one bill sent to a customer
CREATE TABLE invoices (
  invoice_id INTEGER, company_id INTEGER, customer_id INTEGER,
  invoice_date TEXT, invoice_total REAL, status TEXT   -- PAID / UNPAID
);

-- One invoice has MANY line items (cake, bread, delivery...)
CREATE TABLE invoice_lines (
  line_id INTEGER, invoice_id INTEGER, account_id INTEGER,
  item TEXT, amount REAL
);
""")

cur.executemany("INSERT INTO companies VALUES (?,?)",
    [(1, "Maya's Bakery"), (2, "Leo's Coffee")])

cur.executemany("INSERT INTO accounts VALUES (?,?,?,?)", [
    # Maya's names
    (10, 1, "Sales",           "REVENUE"),
    (11, 1, "Catering Income", "REVENUE"),
    (12, 1, "Refunds",         "REFUND"),
    (13, 1, "Flour Supplier",  "EXPENSE"),
    # Leo's names -- different words, same meanings
    (20, 2, "Coffee Sales",    "REVENUE"),
    (21, 2, "Event Orders",    "REVENUE"),
    (22, 2, "Returns",         "REFUND"),
])

cur.executemany("INSERT INTO customers VALUES (?,?,?)", [
    (100, 1, "Joe's Cafe"), (101, 1, "City Office"),
    (200, 2, "Tech Startup"),
])

cur.executemany("INSERT INTO invoices VALUES (?,?,?,?,?,?)", [
    # Maya: 3 invoices in September
    (1001, 1, 100, "2026-09-03", 450, "PAID"),
    (1002, 1, 101, "2026-09-12", 800, "PAID"),
    (1003, 1, 100, "2026-09-20", -50, "PAID"),    # a refund
    # Maya: 1 invoice in August
    (1004, 1, 101, "2026-08-15", 900, "UNPAID"),
    # Leo
    (2001, 2, 200, "2026-09-05", 300, "PAID"),
])

cur.executemany("INSERT INTO invoice_lines VALUES (?,?,?,?,?)", [
    # invoice 1001 ($450) has THREE line items
    (1, 1001, 10, "Cakes",    300),
    (2, 1001, 10, "Bread",    100),
    (3, 1001, 10, "Delivery",  50),
    # invoice 1002 ($800) has TWO line items
    (4, 1002, 11, "Catering food",    700),
    (5, 1002, 11, "Catering service", 100),
    # invoice 1003 (refund -$50), one line
    (6, 1003, 12, "Refund stale bread", -50),
    # invoice 1004 ($900, August)
    (7, 1004, 11, "Wedding catering", 900),
    # Leo's invoice
    (8, 2001, 20, "Coffee", 200),
    (9, 2001, 21, "Event coffee bar", 100),
])
con.commit()

for t in ["companies", "accounts", "invoices", "invoice_lines"]:
    print(f"\n=== {t} ===")
    for row in cur.execute(f"SELECT * FROM {t}"):
        print(row)
con.close()
