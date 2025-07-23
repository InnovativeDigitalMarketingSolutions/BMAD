# Orchestrator Agent

De Orchestrator agent is de centrale regisseur binnen het BMAD-platform. Deze agent coördineert de samenwerking tussen alle andere agents, verdeelt taken, monitort de status en zorgt voor een soepele workflow volgens de BMAD-methode.

## Verantwoordelijkheden
- Starten, stoppen en monitoren van agents en workflows
- Routeren van events tussen agents (event-bus)
- Taakverdeling en prioritering (optioneel met LLM-ondersteuning)
- Escalatie en foutafhandeling
- Verzamelpunt voor status, metrics en rapportages
- Faciliteren van feedback loops en contextdeling

## Samenwerking
- Werkt samen met alle agents (Business, Multi-Agent, Agile, DevOps)
- Stuurt events naar agents op basis van status, context of user input
- Kan LLM gebruiken voor intelligente taakverdeling, prioritering en workflow-optimalisatie

## BMAD-compliance
- Zorgt dat alle workflows, events en samenwerkingen voldoen aan de BMAD-principes
- Documenteert beslissingen, status en verbeteringen

## Belangrijke resources
- [Changelog](changelog.md)
- [Orchestrator config](orchestrator.yaml) 