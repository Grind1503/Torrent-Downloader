import asyncio
import nest_asyncio
import json
import os
from dotenv import load_dotenv
import aiohttp
from mcp import ClientSession
from mcp.client.sse import sse_client

nest_asyncio.apply()
load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
AVAILABLE_CATEGORIES = ["Movies", "Games", "TV", "Music", "Apps", "Documentaries", "Anime", "Other", "XXX"]

async def ask_perplexity(prompt: str) -> dict:
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "queries": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["category", "queries"]
                }
            }
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(PERPLEXITY_API_URL, headers=headers, json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"Perplexity API error {resp.status}: {text}")
            result = await resp.json()
            return json.loads(result["choices"][0]["message"]["content"])

async def generate_keywords(user_query: str) -> dict:
    llm_prompt = f"""
                    Convert this user's request into optimized torrent search keywords and categorize them.
                    User query: "{user_query}".
                    Categories: {AVAILABLE_CATEGORIES}.

                    Output JSON only in this format:
                    {{
                        "category": "Movies",
                        "queries": ["keyword1", "keyword2"]
                    }}

                    Rules:
                    - Always return queries as an array.
                    - If the user asks for one specific item, return an array with just one element.
                    - If the user asks for a series, collection, or multiple items (e.g. "all Harry Potter movies"), expand into separate queries for each item in order.
                    - Queries should be concise, realistic torrent search keywords (e.g. movie/show/game names, not long sentences).
                    - Do NOT generate synonyms or spelling variations. Stick to canonical titles/names.
                """
    try:
        return await ask_perplexity(llm_prompt)
    except Exception as e:
        return {"category": "Other", "queries": [user_query]}

def generate_keywords_sync(user_query: str) -> dict:
    print(f"[LLM] User query: {user_query}")
    result = asyncio.run(generate_keywords(user_query))
    print(f"[LLM] Generated keywords & category: {json.dumps(result, indent=2)}")
    return result
