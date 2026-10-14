"""STEP 4: The rule book, wrapped in an MCP server.

Any MCP-compatible AI app (Claude, an internal Intuit agent, ...) can plug in
and use these tools. No custom integration per app.

SECURITY: which company's data you see comes from the LOGGED-IN USER
(here simulated by the QB_COMPANY_ID environment variable set at login),
NOT from anything the AI model sends. There is no company_id parameter at all.
"""
import os
from mcp.server.fastmcp import FastMCP
import semantic

COMPANY_ID = int(os.environ["QB_COMPANY_ID"])   # set by "login", never by the model

mcp = FastMCP("quickbooks-semantic-layer")


# ---- RESOURCE: read-only data the AI can read ----
@mcp.resource("metrics://definitions")
def metric_definitions() -> str:
    """The governed definitions of every metric."""
    return "\n".join(f"{name}: {d}" for name, d in semantic.list_metrics().items())


# ---- TOOLS: actions the AI can call ----
@mcp.tool()
def list_metrics() -> dict:
    """List every governed metric and what it means. Call this first."""
    return semantic.list_metrics()


@mcp.tool()
def list_dimensions() -> list:
    """List the dimensions metrics can be sliced by (month, customer, account_type)."""
    return list(semantic.RULES["dimensions"])


@mcp.tool()
def query_metric(metric: str, group_by: list[str] | None = None,
                 month: str | None = None) -> list:
    """Get a governed metric for the logged-in user's company.

    metric:   one of list_metrics(), e.g. "revenue"
    group_by: optional dimensions, e.g. ["month"] or ["customer"]
    month:    optional filter "YYYY-MM", e.g. "2026-09"
    """
    # company_id is injected here from the login. The model cannot change it.
    return semantic.query_metric(COMPANY_ID, metric, group_by, month)


if __name__ == "__main__":
    mcp.run()   # talks MCP over stdio
