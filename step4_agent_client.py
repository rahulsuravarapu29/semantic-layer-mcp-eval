"""STEP 4 demo: act like an AI agent (MCP client) plugging into the server.
We connect twice: once logged in as Maya, once as Leo.
"""
import asyncio, json, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def show(result):
    if result.isError:
        return "ERROR -> " + result.content[0].text.splitlines()[-1]
    texts = [c.text for c in result.content]
    return texts[0] if len(texts) == 1 else "[" + ", ".join(texts) + "]"


async def session_as(company_id, label):
    params = StdioServerParameters(
        command=sys.executable, args=["mcp_server.py"],
        env={**os.environ, "QB_COMPANY_ID": str(company_id)})
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print(f"\n================ Logged in as {label} ================")

            tools = await s.list_tools()
            print("1) Tools the agent discovers:", [t.name for t in tools.tools])

            res = await s.list_resources()
            print("2) Resources it can read:   ", [str(x.uri) for x in res.resources])

            print("3) list_metrics()            ->", show(await s.call_tool("list_metrics", {})))
            print("4) revenue for 2026-09       ->",
                  show(await s.call_tool("query_metric", {"metric": "revenue", "month": "2026-09"})))
            print("5) revenue by month          ->",
                  show(await s.call_tool("query_metric", {"metric": "revenue", "group_by": ["month"]})))
            print("6) typo 'revenu'             ->",
                  show(await s.call_tool("query_metric", {"metric": "revenu"})))
            print("7) agent tries company_id=2  ->",
                  show(await s.call_tool("query_metric", {"metric": "revenue", "company_id": 2})))


async def main():
    await session_as(1, "MAYA (company 1)")
    await session_as(2, "LEO  (company 2)")

asyncio.run(main())
