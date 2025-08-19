from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import json
from llmclient import generate_keywords_sync
from mcp.client.sse import sse_client
from mcp import ClientSession

app = Flask(__name__)
CORS(app)

MCP_URL = "http://localhost:8050/sse"  # MCP server SSE endpoint

async def call_mcp_tools(queries, category=None):
    results = []
    async with sse_client(MCP_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            for q in queries:
                print(f"[MCP] Calling search_torrents with query: {q} | Category: {category}")
                resp = await session.call_tool("search_torrents", arguments={"query": q, "limit": 1, "category": category})
                try:
                    torrents = json.loads(resp.content[0].text)
                except Exception:
                    torrents = []
                for t in torrents:
                    if t.get("magnet"):
                        print(f"[MCP] Auto-downloading: {t['name']} | Magnet: {t['magnet']}")
                        dl_resp = await session.call_tool("download_torrent", arguments={"magnet": t["magnet"]})
                        dl_json = json.loads(dl_resp.content[0].text)
                        t["download_status"] = dl_json.get("success")
                        t["download_error"] = dl_json.get("error")
                        print(f"[MCP] Download result: {dl_json}")
                results.extend(torrents)
    return results

@app.route("/llm_keywords", methods=["POST"])
def llm_keywords():
    data = request.get_json()
    query = data.get("query")
    if not query:
        return jsonify({"error": "Query missing"}), 400

    try:
        # Step 1: Generate optimized keywords
        llm_result = generate_keywords_sync(query)
        queries = llm_result.get("queries", [query])
        category = llm_result.get("category")

        # Step 2: Call MCP tools asynchronously
        torrents = asyncio.run(call_mcp_tools(queries, category))
        return jsonify({"results": torrents})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=8000, debug=True)
