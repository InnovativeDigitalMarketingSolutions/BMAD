#### Memory Design
- Short-term: Redis (TTL 1h, per user/session)
- Long-term: Supabase (Postgres, JSONB, vector search via pgvector)
- AI context: pgvector (semantic search, context retrieval for LLMs)