# Product Owner Output & Best Practices

## Rol en verantwoordelijkheden
De Product Owner bewaakt de productwaarde, prioriteert de backlog en vertaalt wensen van stakeholders naar heldere user stories en epics.

---

## Voorbeeld User Story

```markdown
**User Story:**  
Als gebruiker wil ik kunnen inloggen zodat ik toegang krijg tot mijn dashboard.

**Acceptatiecriteria:**
- Gebruiker kan inloggen met e-mail en wachtwoord
- Foutmelding bij onjuiste inloggegevens
- Sessie blijft 24 uur geldig
```

---

## Voorbeeld Epic

```markdown
**Epic:**  
Gebruikersauthenticatie en -beheer

**Beschrijving:**  
Implementeer registratie, login, wachtwoord reset en gebruikersprofielbeheer.
```

---

## Voorbeeld Acceptance Criteria

```markdown
**Acceptatiecriteria:**
- Duidelijk, testbaar en meetbaar
- Altijd gekoppeld aan een user story
- Gevalideerd met stakeholders
```

---

## ClickUp JSON Output

```json
{
  "operation": "createTask",
  "parameters": {
    "list_id": "LIST_ID_HIER",
    "name": "User Authentication Flow",
    "content": "Implementeer login, registratie en beveiligde sessies",
    "status": "todo",
    "priority": 2,
    "tags": ["Frontend", "Security"],
    "assignees": ["USER_ID_HIER"]
  }
}
```

---

## Backlog Refinement Tips
- Splits grote stories in kleinere, testbare items
- Voeg altijd acceptatiecriteria toe
- Prioriteer op waarde en risico

---

## Definition of Ready (DoR)
- Story is klein genoeg om in één sprint op te leveren
- Acceptatiecriteria zijn duidelijk
- Dependencies zijn bekend

## Definition of Done (DoD)
- Alle acceptatiecriteria zijn behaald
- Code is gereviewd en getest
- Documentatie is bijgewerkt

---

## Veelgemaakte fouten (anti-patterns)
- Stories zonder acceptatiecriteria
- Te grote epics zonder splitsing
- Onvoldoende stakeholderafstemming

---

## Do’s & Don’ts

**Do:**
- Werk user stories altijd uit met acceptatiecriteria
- Betrek stakeholders bij refinement

**Don’t:**
- Voeg geen vage of onmeetbare criteria toe
- Laat stories niet te groot worden

---

## Meer weten?
Zie de resource-bestanden in `resources/templates/general/` voor actuele templates.