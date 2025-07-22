# ... bestaande documentatie ...

## Centrale samenwerking tussen agents

Alle agents in het BMAD-platform kunnen nu samenwerken via een centrale message bus en gedeelde context in Supabase:

- **Message bus:** Agents publiceren events (zoals 'pipeline_validated', 'tests_passed', 'design_finalized') die door andere agents opgepikt kunnen worden.
- **Supabase context:** Agents delen status en relevante data in een centrale contexttabel, zodat andere agents deze kunnen inzien en gebruiken.

Zie de individuele agent-documentatie voor concrete voorbeelden van samenwerking en contextdeling. 