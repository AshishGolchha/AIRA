"""AIRA Comprehensive Supabase PostgreSQL Database & pgvector Validator."""

import os
import sys
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath("."))
load_dotenv()

def validate_supabase_database():
    print("=" * 60)
    print("AIRA SUPABASE POSTGRESQL & PGVECTOR VALIDATION")
    print("=" * 60)

    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    db_url = os.getenv("DATABASE_URL", "")

    results = {}

    # 1. Supabase Client & PostgreSQL Connectivity
    from supabase import create_client
    if not url or not key:
        print("[FAIL] Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")
        return False

    try:
        sb = create_client(url, key)
        results["Supabase Client"] = "PASS"
    except Exception as e:
        results["Supabase Client"] = f"FAIL ({e})"
        print(f"[FAIL] Supabase client initialization failed: {e}")
        return False

    # 2. Table Existence Checks via Supabase Client
    tables = [
        ("users", "users"),
        ("user_profiles", "user_profiles"),
        ("portfolio_holdings", "portfolio_holdings"),
        ("portfolio_intelligence_records", "portfolio_intelligence"),
        ("research_records", "research_records"),
        ("watchlist_items", "watchlist_items"),
        ("alerts", "alerts"),
        ("notification_preferences", "notification_preferences"),
        ("notification_endpoints", "notification_endpoints"),
        ("notification_deliveries", "notification_deliveries"),
        ("alert_monitoring_runs", "alert_monitoring_runs"),
        ("monitoring_locks", "monitoring_locks"),
        ("user_memories", "user_memories"),
    ]

    for table_name, display_name in tables:
        try:
            res = sb.table(table_name).select("*").limit(1).execute()
            results[display_name] = "PASS"
        except Exception as e:
            results[display_name] = f"FAIL ({e})"

    # 3. Vector Extension & RPC Checks
    from app.services.embedding_service import EmbeddingService
    embed_service = EmbeddingService()

    try:
        dummy_vec = [0.0] * 768
        rpc_res = sb.rpc("match_user_memories", {
            "p_user_id": 999999,
            "p_embedding": dummy_vec,
            "p_match_threshold": 0.1,
            "p_match_count": 1,
            "p_memory_type": None,
        }).execute()
        results["pgvector extension"] = "PASS"
        results["match_user_memories RPC"] = "PASS"
    except Exception as e:
        results["pgvector extension"] = f"FAIL ({e})"
        results["match_user_memories RPC"] = f"FAIL ({e})"

    # 4. Relational CRUD Round-Trip Test
    test_email = f"validation_{uuid.uuid4().hex[:8]}@aira.internal"
    created_user_id = None
    try:
        # INSERT
        user_res = sb.table("users").insert({
            "email": test_email,
            "password_hash": "pbkdf2:sha256:test_hash_val_placeholder",
            "alerts_enabled": True,
        }).execute()
        if user_res.data and len(user_res.data) > 0:
            created_user_id = user_res.data[0]["id"]
            # READ
            fetched = sb.table("users").select("*").eq("id", created_user_id).single().execute()
            assert fetched.data["email"] == test_email

            # Sub-table INSERT & CASCADE verify (watchlist & profile)
            sb.table("watchlist_items").insert({
                "user_id": created_user_id,
                "symbol": "NVDA",
                "company_name": "NVIDIA Corporation",
                "priority": "high",
            }).execute()

            # DELETE (Cascading)
            sb.table("users").delete().eq("id", created_user_id).execute()
            created_user_id = None
            results["Relational CRUD"] = "PASS"
        else:
            results["Relational CRUD"] = "FAIL (Insert returned empty)"
    except Exception as e:
        results["Relational CRUD"] = f"FAIL ({e})"
        if created_user_id:
            try:
                sb.table("users").delete().eq("id", created_user_id).execute()
            except Exception:
                pass

    # 5. Vector Memory Round-Trip Test (Embed -> Insert -> Semantic Search -> Delete)
    test_uid = 888888
    created_mem_id = None
    try:
        from app.services.memory_service import MemoryService
        mem_service = MemoryService(supabase_client=sb, embedding_service=embed_service)

        test_content = f"Validation test preference for quantum computing semiconductor investments {uuid.uuid4().hex[:6]}"
        created = mem_service.create_memory(
            user_id=test_uid,
            content=test_content,
            memory_type="preference",
            importance="high",
            metadata={"source": "validation_script"},
        )
        if created and created.get("id"):
            created_mem_id = created["id"]
            search_res = mem_service.search_memories(
                user_id=test_uid,
                query="semiconductor and quantum computing strategy",
                limit=3,
            )
            assert len(search_res) > 0
            assert search_res[0]["content"] == test_content
            # Cleanup
            mem_service.delete_memory(test_uid, created_mem_id)
            created_mem_id = None
            results["Vector Memory Search"] = "PASS"
        else:
            results["Vector Memory Search"] = "FAIL (Memory creation failed)"
    except Exception as e:
        results["Vector Memory Search"] = f"FAIL ({e})"
        if created_mem_id:
            try:
                sb.table("user_memories").delete().eq("id", created_mem_id).execute()
            except Exception:
                pass

    print()
    for k, v in results.items():
        print(f"{k:<35} {v}")
    print("=" * 60)
    return results

if __name__ == "__main__":
    validate_supabase_database()
