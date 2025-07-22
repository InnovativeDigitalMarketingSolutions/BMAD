# BMAD Agent Template & Checklist (Geoptimaliseerd)

## 1. Agent YAML configuratie
- [ ] Maak een `<agentnaam>.yaml` aan met:
  - name, id, title, customization
  - persona (role, style, identity, focus, core_principles)
  - commands (met korte beschrijving, output/snippet commando's expliciet)
  - dependencies (templates/data met volledige paden)
  - (Optioneel) Versiebeheer: changelog, versieveld, datum laatste wijziging

## 2. Python implementatie
- [ ] Maak `<agentnaam>.py` aan met:
  - CLI interface (`argparse` of click)
  - Hybride structuur: resource-bestanden als eerste, Python-fallback als backup
  - Alle commando’s uit YAML geïmplementeerd
  - Output/snippet commando's (bijv. `show-<snippet>`, `export-<output>`)
  - (Optioneel) Integratie met message_bus voor inter-agent communicatie
  - (Optioneel) ClickUp/webhook integratie
  - (Optioneel) AI-integratie (LLM, prompt engineering, feedback-loop)
  - (Optioneel) Security checks (input validatie, logging)

## 3. Markdown best practices
- [ ] Maak `<agentnaam>.md` aan met:
  - Voorbeelden van output, best practices, tips, anti-patterns
  - Uitleg over de rol van de agent
  - Lessons learned, DoR/DoD, refinement tips

## 4. Resource-bestanden aanmaken
- [ ] Templates: Plaats in `resources/templates/general/` of `resources/templates/<agentnaam>/`
- [ ] Data: Plaats in `resources/data/general/` of `resources/data/<agentnaam>/`
- [ ] Vul templates/data met relevante voorbeelden, checklists, output, etc.
- [ ] Voeg indien nodig testdata toe voor testbaarheid

## 5. YAML dependencies updaten
- [ ] Zorg dat alle dependencies in de YAML verwijzen naar de juiste resource-bestanden
- [ ] Controleer of alle paden kloppen na verplaatsingen

## 6. Testen
- [ ] Test alle commando’s via de CLI (inclusief output/snippet commando's)
- [ ] Controleer of alle resource-bestanden correct worden gelezen/geschreven
- [ ] Controleer of inter-agent communicatie werkt (indien van toepassing)
- [ ] Test edge cases en foutafhandeling

## 7. Documentatie
- [ ] Voeg uitleg toe aan de agent-README of centrale documentatie
- [ ] Licht toe hoe de agent samenwerkt met andere agents (indien relevant)
- [ ] Documenteer AI-integratie, security, versiebeheer en uitbreidbaarheid

---

## Voorbeeld resource-bestanden
- `resources/templates/<agentnaam>/<template>.md`
- `resources/data/<agentnaam>/<data>.md`
- `resources/data/general/<shared-data>.md`
- `resources/data/<agentnaam>/testdata.json`

## Voorbeeld commando’s
- `show-<snippet>`: Toon een resource-bestand
- `generate-<output>`: Genereer output op basis van data/templates
- `sync-<tool>`: Synchroniseer met externe tool (ClickUp, Slack, etc.)
- `update-<status>`: Update status van een taak of item
- `export-<output>`: Exporteer data naar gewenst formaat (md, json, csv)

---

**Gebruik deze checklist bij het aanmaken van elke nieuwe BMAD agent voor een consistente, onderhoudbare, veilige en krachtige workflow!**
