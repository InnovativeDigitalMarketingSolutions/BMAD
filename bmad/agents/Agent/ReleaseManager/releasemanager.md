# ReleaseManager Agent

De ReleaseManager agent is verantwoordelijk voor releaseplanning, changelogs en deployment.

## Verantwoordelijkheden
- Plannen en coördineren van releases
- Bijhouden van changelogs
- Samenwerken met alle agents voor releasevoorbereiding

## Belangrijke resources
- [Changelog](changelog.md)

## Samenwerking & Automatisering

De ReleaseManager werkt nauw samen met:
- **TestEngineer:** Start releaseproces na geslaagde tests.
- **DevOpsInfra:** Automatiseert deployment en monitoring.
- **Product Owner:** Wacht op goedkeuring voor release.
- **Architect:** Checkt of architecturale eisen zijn geborgd.

De ReleaseManager kan automatisch events ontvangen via de message bus, zoals:
- `tests_passed` (TestEngineer): Start release flow.
- `release_approved` (Product Owner): Zet release live.
- `deployment_failed` (DevOpsInfra): Start rollback of notificatie.
