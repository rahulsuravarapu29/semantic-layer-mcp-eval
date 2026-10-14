from semantic import query_metric, build_sql, list_metrics

print("Metrics in the rule book:", list_metrics(), "\n")

print("1) Maya, revenue, September  ->", query_metric(1, "revenue", month="2026-09"))
print("2) Leo,  revenue, September  ->", query_metric(2, "revenue", month="2026-09"))
print("3) Maya, revenue by month    ->", query_metric(1, "revenue", group_by=["month"]))
print("4) Maya, revenue by customer ->", query_metric(1, "revenue", group_by=["customer"], month="2026-09"))
print("5) Maya, invoice_count, Sept ->", query_metric(1, "invoice_count", month="2026-09"))
print("6) Maya, unpaid_amount       ->", query_metric(1, "unpaid_amount"))

print("\n--- The SQL the engine wrote for question 1 (nobody typed this) ---")
sql, params = build_sql(1, "revenue", month="2026-09")
print(sql, "\nparams:", params)

print("\n--- Asking for something the rule book doesn't allow ---")
for bad in [("revenu", None), ("invoice_count", ["account_type"])]:
    try:
        query_metric(1, bad[0], group_by=bad[1])
    except ValueError as e:
        print("Refused:", e)
