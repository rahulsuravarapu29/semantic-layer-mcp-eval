"""The semantic layer ENGINE: reads the rule book and writes the SQL.
Nobody (human or AI) writes SQL by hand anymore. They just ask for a metric.
"""
import sqlite3, yaml

RULES = yaml.safe_load(open("semantic_layer.yaml"))


def list_metrics():
    return {name: m["description"] for name, m in RULES["metrics"].items()}


def build_sql(company_id, metric, group_by=None, month=None):
    if metric not in RULES["metrics"]:
        raise ValueError(f"Unknown metric '{metric}'. Valid: {list(RULES['metrics'])}")
    m = RULES["metrics"][metric]
    grain = m["grain"]
    group_by = group_by or []

    dims = []
    for d in group_by:
        dim = RULES["dimensions"].get(d)
        if dim is None:
            raise ValueError(f"Unknown dimension '{d}'")
        if grain not in dim["grains"]:
            raise ValueError(f"'{metric}' can't be sliced by '{d}'")
        dims.append(f"{dim['sql']} AS {d}")

    # SECURITY: company filter is ALWAYS added by the engine, never optional
    where = [m["where"], "i.company_id = ?"]
    params = [company_id]
    if month:
        where.append("strftime('%Y-%m', i.invoice_date) = ?")
        params.append(month)

    select = ", ".join(dims + [f"{m['sql']} AS {metric}"])
    sql = f"SELECT {select}\nFROM {RULES['grains'][grain]['from']}WHERE " + " AND ".join(where)
    if dims:
        sql += "\nGROUP BY " + ", ".join(group_by)
    return sql, params


def query_metric(company_id, metric, group_by=None, month=None):
    sql, params = build_sql(company_id, metric, group_by, month)
    con = sqlite3.connect("quickbooks.db")
    cur = con.execute(sql, params)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]
