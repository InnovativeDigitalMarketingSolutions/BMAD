# Agent Documentation Maintenance Guide

## Overview
Deze guide beschrijft de verplichte documentatie maintenance workflow voor alle BMAD agents. Agent documentatie moet altijd up-to-date blijven na elke wijziging aan een agent.

## Verplichte Documentatie Bestanden

### 1. Agent-specifieke Documentatie
- **`<agentname>.md`** - Agent documentatie met capabilities en usage
- **`changelog.md`** - Agent changelog met wijzigingen en beslissingen
- **`<agentname>.yaml`** - Agent configuratie met commands en dependencies
- **`README.md`** - Agent overview en quick start (indien aanwezig)

### 2. Project Documentatie
- **`agents-overview.md`** - Overzicht van alle agents en hun status
- **`docs/deployment/KANBAN_BOARD.md`** - Project progress en task status
- **`docs/guides/`** - Alle guide files (best practices, lessons learned, etc.)

## Documentatie Update Workflow

### Stap 1: Changelog Update (Verplicht)
Na elke agent wijziging moet de changelog worden bijgewerkt:

```markdown
## [YYYY-MM-DD] Feature/Enhancement Name
### Added
- **Feature 1**: Beschrijving van nieuwe functionaliteit
- **Feature 2**: Beschrijving van nieuwe functionaliteit

### Enhanced
- **Existing Feature**: Beschrijving van verbeteringen
- **Performance**: Beschrijving van performance verbeteringen

### Technical
- **Implementation Details**: Technische implementatie details
- **Dependencies**: Nieuwe of gewijzigde dependencies
- **Configuration**: Configuratie wijzigingen
```

**Verplichte Elementen:**
- [ ] **Datum**: YYYY-MM-DD formaat
- [ ] **Categorieën**: Added, Enhanced, Technical secties
- [ ] **Details**: Specifieke features en wijzigingen
- [ ] **Technical Details**: Implementatie details voor developers

### Stap 2: Agent .md File Update (Verplicht)
Update de agent documentatie met nieuwe capabilities:

**Secties die altijd up-to-date moeten zijn:**
- [ ] **Overview**: Agent beschrijving en core features
- [ ] **MCP Integration**: MCP capabilities en tools
- [ ] **CLI Commands**: Volledige command lijst met voorbeelden
- [ ] **Usage Examples**: Praktische voorbeelden voor alle features
- [ ] **Integration Points**: Beschrijving van inter-agent communicatie

### Stap 3: YAML Configuration Update (Verplicht)
Update de agent YAML configuratie:

**Verplichte Updates:**
- [ ] **Commands**: Alle commands met korte beschrijvingen
- [ ] **Dependencies**: Volledige dependency lijst
- [ ] **Persona**: Agent persona en core principles
- [ ] **Customization**: Agent-specifieke customization details

### Stap 4: Agents Overview Update (Verplicht)
Update `agents-overview.md` met nieuwe status:

**Verplichte Updates:**
- [ ] **Message Bus Integration Status**: Update status voor specifieke agent
- [ ] **Workflow Compliance Status**: Update compliance status
- [ ] **Progress Metrics**: Update overall project progress

### Stap 5: Project Documentation Sync (Verplicht)
Synchroniseer alle project documentatie:

**Verplichte Updates:**
- [ ] **Kanban Board**: Update progress en status
- [ ] **Integration Reports**: Update relevante rapporten
- [ ] **Best Practices**: Voeg nieuwe lessons learned toe
- [ ] **Workflow Guides**: Update workflow guides indien nodig

## Documentatie Standards

### Changelog Standards
- **Datum Formaat**: YYYY-MM-DD
- **Categorieën**: Added, Enhanced, Technical
- **Details**: Specifiek en gedetailleerd
- **Technical Details**: Voor developer begrip

### Agent .md File Standards
- **Overview**: Duidelijke agent beschrijving
- **Features**: Volledige feature lijst
- **CLI Commands**: Alle commands met voorbeelden
- **Usage Examples**: Praktische voorbeelden
- **Integration**: Inter-agent communicatie beschrijving

### YAML Configuration Standards
- **Commands**: Alle commands met beschrijvingen
- **Dependencies**: Volledige dependency lijst
- **Persona**: Agent persona en principles
- **Customization**: Agent-specifieke details

### Project Documentation Standards
- **Status Updates**: Accurate status voor alle agents
- **Progress Tracking**: Real-time progress updates
- **Integration Reports**: Up-to-date integratie rapporten
- **Best Practices**: Nieuwe lessons learned

## Quality Assurance Checklist

### Pre-Update Checklist
- [ ] **Agent Analysis**: Volledige analyse van agent wijzigingen
- [ ] **Impact Assessment**: Bepaal impact op documentatie
- [ ] **Dependency Check**: Controleer alle documentatie dependencies

### Update Checklist
- [ ] **Changelog**: Nieuwe entry met alle wijzigingen
- [ ] **Agent .md**: Volledige update van agent documentatie
- [ ] **YAML Config**: Update configuratie indien nodig
- [ ] **Agents Overview**: Update status en progress
- [ ] **Project Docs**: Synchroniseer alle project documentatie

### Post-Update Checklist
- [ ] **Documentation Review**: Controleer alle documentatie updates
- [ ] **Consistency Check**: Controleer consistentie tussen documentatie
- [ ] **Link Validation**: Controleer alle links en referenties
- [ ] **Format Validation**: Controleer markdown formatting

## Success Criteria

### Changelog Success
- ✅ Nieuwe entry met correcte datum
- ✅ Alle wijzigingen gedocumenteerd
- ✅ Technische details toegevoegd
- ✅ Categorieën correct gebruikt

### Agent .md Success
- ✅ Overview up-to-date
- ✅ Features volledig gedocumenteerd
- ✅ CLI commands compleet
- ✅ Usage examples praktisch
- ✅ Integration points beschreven

### YAML Configuration Success
- ✅ Commands compleet en beschreven
- ✅ Dependencies up-to-date
- ✅ Persona correct beschreven
- ✅ Customization details toegevoegd

### Project Documentation Success
- ✅ Agents overview up-to-date
- ✅ Kanban board gesynchroniseerd
- ✅ Integration reports bijgewerkt
- ✅ Best practices toegevoegd

## Compliance Requirements

### Verplichte Updates
**CRITICAL**: De volgende updates zijn verplicht na elke agent wijziging:
1. **Changelog Update** - Nieuwe entry met alle wijzigingen
2. **Agent .md Update** - Volledige documentatie update
3. **YAML Config Update** - Configuratie update indien nodig
4. **Agents Overview Update** - Status en progress update
5. **Project Documentation Sync** - Alle project docs synchroniseren

### Compliance Monitoring
- **Pre-Commit Check**: Controleer documentatie updates voor commit
- **Post-Commit Review**: Review documentatie na commit
- **Regular Audits**: Regelmatige audits van documentatie compleetheid
- **Progress Tracking**: Track documentatie compliance in project metrics

## Best Practices

### Changelog Best Practices
- **Consistent Format**: Gebruik consistent format voor alle entries
- **Detailed Descriptions**: Geef gedetailleerde beschrijvingen van wijzigingen
- **Technical Context**: Voeg technische context toe voor developers
- **Date Accuracy**: Zorg voor accurate datums

### Agent Documentation Best Practices
- **Clear Structure**: Gebruik duidelijke structuur en secties
- **Practical Examples**: Voeg praktische voorbeelden toe
- **Complete Coverage**: Dek alle agent capabilities af
- **Regular Updates**: Update regelmatig, niet alleen bij grote wijzigingen

### Project Documentation Best Practices
- **Real-time Updates**: Update in real-time, niet achteraf
- **Consistency**: Zorg voor consistentie tussen alle documentatie
- **Cross-references**: Gebruik cross-references tussen documentatie
- **Version Control**: Track documentatie wijzigingen in version control

## Troubleshooting

### Common Issues
1. **Incomplete Updates**: Zorg dat alle documentatie wordt bijgewerkt
2. **Inconsistent Format**: Gebruik consistent format voor alle documentatie
3. **Missing Dependencies**: Controleer alle documentatie dependencies
4. **Outdated Information**: Regelmatige updates voorkomen outdated informatie

### Resolution Steps
1. **Identify Issue**: Identificeer het specifieke documentatie probleem
2. **Update Required Files**: Update alle benodigde documentatie bestanden
3. **Verify Consistency**: Controleer consistentie tussen documentatie
4. **Test Documentation**: Test documentatie voor accuracy en completeness

## Reference Documents
- Agent Enhancement Workflow Guide: `docs/guides/AGENT_ENHANCEMENT_WORKFLOW.md`
- Best Practices Guide: `docs/guides/BEST_PRACTICES_GUIDE.md`
- Lessons Learned Guide: `docs/guides/LESSONS_LEARNED_GUIDE.md`
- Quality Guide: `docs/guides/QUALITY_GUIDE.md`
- Test Workflow Guide: `docs/guides/TEST_WORKFLOW_GUIDE.md`

---

**CRITICAL**: Deze guide moet strikt gevolgd worden voor alle agent documentatie maintenance. Documentatie updates zijn verplicht en moeten altijd worden uitgevoerd na elke agent wijziging. 