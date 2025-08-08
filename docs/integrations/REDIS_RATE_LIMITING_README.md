# Redis-backed Rate Limiting for BMAD API

## Waarom Redis?
- Gedeelde state voor meerdere API-instances (horizontale schaalbaarheid)
- Atomaire limieten (geen race conditions) en correcte X-RateLimit-* headers
- Eenvoudig namespacing (tenant:, user:, ip:) voor quota en fair usage
- Optionele persistente counters (AOF/RDB) en simpele observability

## Snelstart

1) Start Redis lokaal via docker-compose
```bash
docker compose up -d redis
```

2) Start backend met Redis storage (buiten DEV)
```bash
# macOS/zsh
source .venv/bin/activate
export DEV_MODE=false
export RATELIMIT_STORAGE_URI=redis://localhost:6379/0
python bmad/api.py
```

3) Check headers
```bash
curl -i http://localhost:5003/test/ping | sed -n '1,20p'
# Verwacht: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
```

4) Terug naar DEV (frontend soepel houden)
```bash
export DEV_MODE=true
python bmad/api.py
```

## Configuratie
- `RATELIMIT_STORAGE_URI`: bijv. `redis://localhost:6379/0`
- `RATELIMIT_STRATEGY`: `fixed-window` (default) of `moving-window`
- `DEFAULT_RATE_LIMITS`: fallback limieten (bijv. `200 per day;50 per hour;10 per minute`)

## Implementatiedetails (bmad/api.py)
- Centrale `IS_DEV` vlag stuurt limiter-config aan
- `rate_limit_key()` gebruikt `request.tenant_id` (indien aanwezig) of client IP
- Per-route decorators (bijv. `/api/metrics` 60/min, `/api/agents` 120/min)
- Exempt voor health/test/swagger en `metrics-lite`
- 429-handler voegt `Retry-After` toe buiten DEV

## Tips
- Gebruik Redis monitoring (bijv. `redis-cli MONITOR`) voor debugging
- In productie: run Redis als managed service of met persistence en monitoring 