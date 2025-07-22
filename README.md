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

## Contact
Voor vragen of bijdragen: open een issue of neem contact op met het team. 