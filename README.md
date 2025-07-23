# BMAD Project

Dit project volgt de BMAD-methode (Business, Multi-Agent, Agile, DevOps) en bestaat uit een set van samenwerkende agents, elk met een eigen verantwoordelijkheid en resource-bibliotheek.

## Projectstructuur

- `bmad/agents/Agent/` — Alle agents (Python, YAML, Markdown)
- `bmad/resources/data/` — Data-bestanden per agent/type
- `bmad/resources/templates/` — Templates per agent/type
- `bmad/resources/data/general/` — Centrale changelog, backlog, roadmap, etc.

## BMAD-methode
- **Business:** Focus op waarde, stakeholders, visie
- **Multi-Agent:** Samenwerkende AI-agents met eigen taken
- **Agile:** Sprints, retrospectives, changelogs, feedbackloops
- **DevOps:** CI/CD, infra-as-code, monitoring, security
- **Samenwerking:** Agents communiceren via een centrale message bus en delen context/status via Supabase. Zie [bmad/agents/Agent/agents-overview.md](bmad/agents/Agent/agents-overview.md) voor details.

## Aan de slag
1. Clone deze repo
2. Installeer Python dependencies (optioneel: `pip install -r requirements.txt`)
3. Bekijk de agent-mappen voor voorbeelden en documentatie
4. Gebruik de centrale changelog en resource-templates als startpunt

## Bijdragen
- Zie `CONTRIBUTING.md` voor richtlijnen
- Gebruik duidelijke commit messages en update changelogs
- Voeg nieuwe resources toe in de juiste map

## Automatisering
- Changelogs worden automatisch gemerged (zie `merge_agent_changelogs.py`)
- CI/CD workflows voor linting, testen en documentatie

## LLM-integratie
- Agents kunnen nu automatisch en handmatig LLM-advies ophalen voor:
  - Codegeneratie, code review, bug-analyse
  - User stories, requirements, changelogs, documentatie
  - Testgeneratie, test review
  - Security reviews, incident-samenvattingen
  - Data quality checks, pipeline-uitleg
  - Design feedback, component documentatie
  - DevOps pipeline advies, incident response
- Zowel event-driven (via message bus) als handmatig aan te roepen
- Context-injectie en prompt-templates zorgen voor relevante, project-specifieke antwoorden

## Contact
Voor vragen of bijdragen: open een issue of neem contact op met het team. 