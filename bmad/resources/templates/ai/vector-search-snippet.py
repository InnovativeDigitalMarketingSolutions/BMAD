# Vector Search Snippet (pgvector)

import psycopg2

conn = psycopg2.connect(...)
cur = conn.cursor()
cur.execute("SELECT * FROM documents ORDER BY embedding <-> %s LIMIT 5", (query_embedding,))
