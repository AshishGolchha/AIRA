import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("AIRA REAL AI READINESS CHECK SCRIPT")
print("=" * 60)

gemini_key = os.getenv("GEMINI_API_KEY")
gemini_model = os.getenv("GEMINI_LLM_MODEL", "gemini/gemini-2.0-flash")
gemini_embed = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
db_url = os.getenv("DATABASE_URL")

print(f"GEMINI_API_KEY present: {bool(gemini_key and len(gemini_key) > 10)}")
print(f"GEMINI_LLM_MODEL: {gemini_model}")
print(f"GEMINI_EMBEDDING_MODEL: {gemini_embed}")
print(f"SUPABASE_URL present: {bool(supabase_url)}")
print(f"SUPABASE_SERVICE_ROLE_KEY present: {bool(supabase_key)}")
print(f"DATABASE_URL: {db_url}")
print("-" * 60)

# 1. Test yfinance
print("\n[TEST 1: YFINANCE DATA RETRIEVAL]")
try:
    import yfinance as yf
    ticker = yf.Ticker("AAPL")
    info = ticker.info
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    name = info.get("shortName") or info.get("longName")
    print(f"[PASS] yfinance SUCCESS: {name} (${ticker.ticker}) current price = ${price}")
except Exception as e:
    print(f"[FAIL] yfinance FAILED: {e}")

# 2. Test Gemini Embeddings
print("\n[TEST 2: GEMINI EMBEDDINGS]")
if gemini_key:
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=gemini_key)
        config = types.EmbedContentConfig(output_dimensionality=768)
        model_to_test = gemini_embed if gemini_embed else "gemini-embedding-2"
        print(f"Testing model: {model_to_test}...")
        response = client.models.embed_content(
            model=model_to_test,
            contents="AIRA investment research preferences",
            config=config,
        )
        if response.embeddings and response.embeddings[0].values:
            dim = len(response.embeddings[0].values)
            print(f"[PASS] Gemini Embedding SUCCESS: Generated {dim}-dim vector with {model_to_test}")
        else:
            print("[FAIL] Gemini Embedding returned empty values")
    except Exception as e:
        print(f"[FAIL] Gemini Embedding FAILED with {gemini_embed}: {e}")
        try:
            print("Testing fallback 'text-embedding-004'...")
            response = client.models.embed_content(
                model="text-embedding-004",
                contents="AIRA investment research preferences",
                config=config,
            )
            if response.embeddings and response.embeddings[0].values:
                dim = len(response.embeddings[0].values)
                print(f"[PASS] text-embedding-004 SUCCESS: Generated {dim}-dim vector")
        except Exception as e2:
            print(f"[FAIL] text-embedding-004 also failed: {e2}")
else:
    print("SKIPPED: GEMINI_API_KEY is not set.")

# 3. Test Supabase Vector Memory
print("\n[TEST 3: SUPABASE VECTOR MEMORY]")
if supabase_url and supabase_key:
    try:
        from supabase import create_client
        client = create_client(supabase_url, supabase_key)
        
        # Test table query
        res = client.table("user_memories").select("id").limit(1).execute()
        print(f"[PASS] Supabase Table 'user_memories' EXISTS: data={res.data}")
        
        # Test RPC match_user_memories
        dummy_embedding = [0.0] * 768
        rpc_res = client.rpc("match_user_memories", {
            "p_user_id": 999999,
            "p_embedding": dummy_embedding,
            "p_match_threshold": 0.1,
            "p_match_count": 1,
            "p_memory_type": None,
        }).execute()
        print(f"[PASS] Supabase RPC 'match_user_memories' EXISTS: data={rpc_res.data}")
    except Exception as e:
        print(f"[FAIL] Supabase FAILED: {e}")
else:
    print("SKIPPED: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing.")

# 4. Test CrewAI + Gemini LLM
print("\n[TEST 4: CREWAI + GEMINI LLM REASONING]")
if gemini_key:
    try:
        from crewai import LLM, Agent, Task, Crew, Process
        print(f"Initializing CrewAI LLM with model: {gemini_model}...")
        llm = LLM(model=gemini_model, api_key=gemini_key)
        agent = Agent(
            role="Financial Analyst",
            goal="Provide a 1-sentence assessment of AAPL.",
            backstory="You are an equity analyst.",
            llm=llm,
            verbose=False,
        )
        task = Task(
            description="Give a 1-sentence summary of Apple Inc.",
            expected_output="A 1-sentence string.",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
        output = crew.kickoff()
        raw_str = str(output.raw if hasattr(output, "raw") else output)
        print(f"[PASS] CrewAI + Gemini LLM SUCCESS: {raw_str[:120]}...")
    except Exception as e:
        print(f"[FAIL] CrewAI + Gemini LLM FAILED: {e}")
else:
    print("SKIPPED: GEMINI_API_KEY is not set.")

# 5. Test MySQL Database
print("\n[TEST 5: MYSQL DATABASE CONNECTION]")
if db_url:
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            print(f"[PASS] MySQL SUCCESS: Connected and executed SELECT 1 -> {result}")
    except Exception as e:
        print(f"[FAIL] MySQL Connection FAILED: {e}")
else:
    print("SKIPPED: DATABASE_URL not set.")

print("\n" + "=" * 60)
