# BMAD Teststrategie (Productie‑klaar)

Deze teststrategie waarborgt de kwaliteit van het DevOps‑AI‑agent‑systeem. Ze combineert traditionele softwaretests met AI‑specifieke evaluaties, sluit aan op onze async‑ en message‑bus wrapper‑standaard, en fungeert als quality gate voor release.

Gerelateerde documenten:
- Agent Completeness Prevention Strategy
- Agent Enhancement Workflow
- Agent Completeness Implementation Workflow
- Message Bus Event Standards

## 1. Overzicht & verdeling

| Testlaag              | Richtlijn % | Doel                                                    |
| --------------------- | ----------: | ------------------------------------------------------- |
| Statische analyse     |         –   | Codekwaliteit, beveiliging, typechecks                  |
| Unit‑tests            |       ~50%  | Isoleren van functies/klassen en core business‑logica   |
| Integratie‑tests      |       ~20%  | Valideren van services + externe deps                   |
| Component‑tests       |       ~10%  | Groep services/agents samen testen                      |
| E2E‑tests             |       ~10%  | Kritieke gebruikersflows over het hele systeem          |
| AI‑evaluatietests     |       ~10%  | Kwaliteit/nauwkeurigheid/ethiek van AI‑agent‑output     |

Richtlijnen zijn risicogebaseerd; aanpasbaar per component. De laag AI‑evaluatie waarborgt GPT‑5‑gedrag (nauwkeurigheid, volledigheid, intent, toolgebruik, ethiek).

## 2. Traditionele lagen (technische tests)

### 2.1 Statische analyse
- Tools: ruff/flake8, mypy, Bandit, ESLint/Prettier (frontend), IaC‑linters
- CI: gating vóór tests; auto‑fix waar mogelijk (format, import‑sort)
- Doel: snelle detectie van syntax/type/security‑issues

### 2.2 Unit‑tests (~50%)
- Scope: functies/klassen van agents, core modules, CLI
- Frameworks: pytest (+ pytest‑asyncio), jest/vitest voor JS
- Richtlijnen:
  - Dependency injection en mocks; geen netwerk/IO
  - Parametriseren; randgevallen en foutpaden
  - Mock `publish_agent_event` (AsyncMock), niet directe `publish(...)`
  - Niet triviale code testen, meaningful assertions

### 2.3 Integratie‑tests (~20%)
- Scope: microservice + DB/message‑bus/externe API’s
- Tools: testcontainers / docker‑compose; toxiproxy (fout/latency injectie)
- Cases:
  - API‑calls, transacties, event‑flows (Completed/Failed), retries/DLQ
  - Asynchrone workflows met meerdere handlers
  - GPT‑5 integratie via stubserver; timeouts en foutafhandeling

### 2.4 Component‑tests (~10%)
- Scope: subsysteem (meerdere agents)
- Voorbeelden: StrategiePartner → ProductOwner → ScrumMaster; ScrumMaster → Developer → TestEngineer → QualityGuardian
- Validatie: events, DB‑wijzigingen, recovery bij failures, concurrency‑issues

### 2.5 E2E‑tests (~10%)
- Scope: volledige gebruikersjourneys
- Frameworks: Playwright/Cypress (web), pexpect (CLI), Slack‑mocks
- Aandacht: kritieke paden, synchronisatie/retries, geïsoleerde preview‑omgeving per PR

### 2.6 Regressie & niet‑functioneel
- Performance: Locust/k6; latency/throughput/resource‑usage; SLA’s
- Security: SAST + DAST; RBAC, rate limiting, misbruikscenario’s
- Chaos/resilience: circuit breakers, retries, failover (Chaostoolkit)
- Consistency: data reset; deterministische tests (seed)

## 3. AI‑evaluatietests (~10%)

### 3.1 Prompt‑ & outputtests
- Doel: verificatie dat agent‑prompt/toolcall correcte output geeft
- Testset: representatieve input → gewenste reacties/eigenschappen
- Evaluatie:
  - LLM‑as‑judge (GPT‑5) met rubrics + embeddings/string‑metrics (cosine, LCS)
  - Frameworks: promptfoo, Langfuse, of custom scripts
- Criteria: nauwkeurigheid, compleetheid, intent‑resolutie, opdrachttrouw, toolcall‑nauwkeurigheid

### 3.2 Performance & efficiency
- Metrics: responstijd, tokenverbruik (kosten), task completion time, throughput
- Aanpak: workloads variëren (promptlengte/complexiteit); automatische rapportage

### 3.3 Robuustheid & ethiek
- Robuustheid/reliability: edge cases, contradicties, noise prompts
- Bias/fairness: diverse inputsets; scoring met fairness‑tools (bijv. Fairlearn)
- Security/prompt‑injection: respect voor systeemprompts/policies; geen gevaarlijke instructies
- Legal/ethiek: naleving bedrijfs- en wettelijke normen; bronvermelding indien gevraagd

### 3.4 Automatisering & opslag
- LLM‑as‑judge met human‑in‑the‑loop bij grensgevallen
- Bulktests via orchestrators; combineer LLM‑scores met asserties
- Opslag in database (bijv. Supabase) en dashboards voor trends

## 4. Structuur & organisatie

### 4.1 Directorystructuur
```
tests/
├── unit/             # core en agent specifieke unit‑tests
├── integration/      # service‑level integratie
├── component/        # subsystem tests (nieuw)
├── e2e/              # volledige gebruikersflows
├── ai_eval/          # GPT‑5 evaluatietests
│   ├── prompts/      # testcases voor prompts, expected outcomes
│   ├── metrics/      # scoreberekening (intent, completeness)
│   └── fairness/     # bias & ethiek checks
└── fixtures/         # testdata, config, model stubresponses
```

### 4.2 Conventies
- Async: `@pytest.mark.asyncio`; gebruik `AsyncMock` voor async methods
- Wrapper: mock `publish_agent_event`; payloads controleren op `status` + domeinsleutel + optioneel `request_id`
- CLI: sync entrypoints gebruiken `asyncio.run(...)` om async paden aan te roepen; in tests mock je dit waar nodig
- Pragmatische mocking: gebruik `patch.object` voor complexe dependencies
- Determinisme: vaste seeds; tijd/UUID mocken waar nodig
- Skip/xfail: alleen met motivatie + ticket; minimaliseer flakiness (retries beperkt)
- Rapportage: Allure/pytest‑HTML; artefacten per CI‑run bewaren

## 5. CI/CD integratie

Volgorde pipeline:
1) Lint & statische analyse (ruff/flake8, black, mypy, Bandit)
2) Unit & integration (parallel)
3) Component (docker‑compose/testcontainers)
4) AI‑evaluatie (tijds- en rate‑limits; nightly uitgebreid, PR subset)
5) E2E (in preview‑omgeving; flake‑guard)
6) Rapportage & quality gates

Quality gates (release‑blocking):
- Lint/type: 0 errors
- Wrapper‑compliance: geen directe `publish(` in agents
- Event‑contract: schema‑validatie groen (pydantic)
- Tests: 100% pass; coverage ≥ 70% totaal, ≥ 80% voor high‑risk modules
- AI‑evaluatie: minimale rubric‑score (bijv. ≥ 0.8) per kritieke agentprompt; geen ethics/security fails
- Security: SAST/DAST groen; secrets/dep scans zonder kritieke findings

## 6. Continuous improvement & governance
- Metrics: trends in AI‑scores, flake‑ratio, performance; regressies automatisch signaleren
- Dataset management: promptsets uitbreiden met echte feedback; versiebeheer datasets/prompts
- Experimenten: A/B en canary op LLM‑versies; evaluaties hergebruiken
- Transparantie: documenteer rubrics/thresholds; stakeholderrapportages
- Audit: archiveer testresultaten, modelversies en prompts per release

## 7. Praktische commando’s

- Unit/integration snel:
```
source .venv/bin/activate && pytest tests/unit -q && pytest tests/integration -q
```
- Wrapper check:
```
python scripts/check_no_direct_publish.py
```
- AI eval subset (voorbeeld placeholder):
```
python tests/ai_eval/run_subset.py --agent ProductOwner --limit 20
```

## 8. Acceptatiecriteria (prod‑klaar)
- 0 directe `publish(` in agents; 100% wrapper‑compliance
- Alle events voldoen aan pydantic schema’s; contracttests groen
- 100% test‑pass; coverage ≥ 70% (≥ 80% voor high‑risk)
- AI‑evaluatie‑scores ≥ drempel; geen ethics/security‑violaties
- CI‑pipeline groen inclusief security scans en SBOM

Deze strategie is bindend voor alle agents, core modules en integraties, en wordt periodiek herzien op basis van lessons learned en productierisico’s. 

## 9. Microservices teststructuur (aanvulling)

```
microservices/{service-name}/
├── tests/
│   ├── unit/
│   │   └── test_{module_name}.py
│   ├── integration/
│   │   └── test_api_endpoints.py
│   └── performance/
│       └── test_load.py
└── test_{service_name}.py
```

Deze sectie sluit aan bij bestaande workflow‑guides en vervangt oudere, overlapende strategieteksten in workflow‑documenten. 