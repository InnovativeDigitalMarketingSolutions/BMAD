# Figma API Integratie voor BMAD

## 📋 Overzicht

Deze integratie maakt het mogelijk om Figma design files te analyseren, componenten te genereren, en automatisch documentatie te maken via verschillende BMAD agents.

## 🚀 Quick Start

### 1. Installatie

```bash
# Zorg dat je in de BMAD directory bent
cd /path/to/BMAD

# Activeer virtual environment
source path/to/venv/bin/activate

# Installeer dependencies (indien nodig)
pip install requests python-dotenv
```

### 2. Configuratie

#### Demo Mode (Aanbevolen voor ontwikkeling)
Voor ontwikkeling en testing zonder echte Figma API toegang:

```bash
# Voeg toe aan .env file
FIGMA_DEMO_MODE=true
```

#### Echte API (Voor productie)
Voor echte Figma API toegang (vereist Pro account):

```bash
# Voeg toe aan .env file
FIGMA_API_TOKEN=figd_your_token_here
FIGMA_DEMO_MODE=false
```

### 3. Testen

```bash
# Test demo mode
FIGMA_DEMO_MODE=true python3 -c "from agents.core.figma_client import FigmaClient; client = FigmaClient(demo_mode=True); print('Demo mode working!')"

# Test echte API (indien beschikbaar)
python3 -c "from agents.core.figma_client import FigmaClient; client = FigmaClient(); print('API working!')"
```

## 🎭 Demo Mode

### Wat is Demo Mode?
Demo mode simuleert de Figma API met mock data, zodat je de volledige integratie kunt testen zonder echte API toegang.

### Voordelen:
- ✅ **Geen API token nodig**
- ✅ **Werkt met gratis Figma accounts**
- ✅ **Snelle ontwikkeling en testing**
- ✅ **Consistente test data**

### Gebruik:
```python
from agents.core.figma_client import FigmaClient

# Demo mode aan
client = FigmaClient(demo_mode=True)

# Alle normale API calls werken
file_data = client.get_file('any_file_id')
components = client.get_components('any_file_id')
comments = client.get_comments('any_file_id')
```

### Mock Data:
Demo mode genereert realistische mock data:
- **File structure** met pages en components
- **Component metadata** met names en descriptions
- **Comments** met user data
- **Design elements** met colors en typography

## 🔧 Gebruik

### CLI Tool

```bash
# Test verbinding
python3 bmad/figma_cli.py test <file_id>

# Genereer componenten
python3 bmad/figma_cli.py components <file_id>

# Analyseer design
python3 bmad/figma_cli.py analyze <file_id>

# Genereer documentatie
python3 bmad/figma_cli.py document <file_id>

# Start monitoring
python3 bmad/figma_cli.py monitor <file_id>
```

### Programmatisch Gebruik

```python
from agents.core.figma_client import FigmaClient
from agents.Agent.FrontendDeveloper.frontenddeveloper import generate_components_from_figma
from agents.Agent.UXUIDesigner.uxuidesigner import analyze_figma_design
from agents.Agent.DocumentationAgent.documentationagent import document_figma_ui

# Initialiseer client
client = FigmaClient()

# Haal file data op
file_data = client.get_file("your_file_id")

# Genereer componenten
components_result = generate_components_from_figma("your_file_id")

# Analyseer design
analysis_result = analyze_figma_design("your_file_id")

# Genereer documentatie
docs_result = document_figma_ui("your_file_id")
```

## 🤖 Agents

### FrontendDeveloper Agent
- **Functie**: Genereert Next.js + Tailwind componenten uit Figma designs
- **Input**: Figma file ID
- **Output**: React componenten met styling

### UXUIDesigner Agent
- **Functie**: Analyseert design patterns, kleuren, en accessibility
- **Input**: Figma file ID
- **Output**: Design insights en accessibility rapport

### DocumentationAgent Agent
- **Functie**: Genereert automatische documentatie voor UI componenten
- **Input**: Figma file ID
- **Output**: Markdown documentatie en export templates

## 📡 Slack Integratie

### Automatische Notificaties
- **Design updates**: Wanneer files worden gewijzigd
- **Nieuwe comments**: Wanneer er comments worden toegevoegd
- **Component generation**: Wanneer componenten worden gegenereerd
- **Analysis completion**: Wanneer design analyse is voltooid

### Configuratie
```bash
# Voeg toe aan .env
FIGMA_NOTIFICATION_CHANNEL=#design-updates
FIGMA_POLL_INTERVAL=300  # 5 minuten
FIGMA_FILES_TO_MONITOR=file_id_1,file_id_2
```

## 🔍 Troubleshooting

### Demo Mode Problemen
```bash
# Controleer demo mode instelling
echo $FIGMA_DEMO_MODE

# Test demo mode
FIGMA_DEMO_MODE=true python3 -c "from agents.core.figma_client import FigmaClient; client = FigmaClient(demo_mode=True); print('Demo mode working')"
```

### API Authenticatie Problemen

#### 403 "Invalid token" Error
**Oorzaak**: Gratis Figma accounts hebben geen API toegang
**Oplossing**: 
1. Gebruik demo mode voor ontwikkeling
2. Upgrade naar Pro account voor echte API
3. Vraag collega met Pro account om token

#### Token niet gevonden
```bash
# Controleer .env file
cat .env | grep FIGMA

# Test token direct
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('FIGMA_API_TOKEN', 'NOT_FOUND'))"
```

#### File niet toegankelijk
- Controleer of file publiek is gedeeld
- Controleer file permissions
- Gebruik demo mode voor testing

### Import Problemen
```bash
# Zorg dat je in de juiste directory bent
cd /path/to/BMAD/bmad

# Test imports
python3 -c "from agents.core.figma_client import FigmaClient; print('Imports working')"
```

## 📁 Bestandsstructuur

```
bmad/
├── agents/
│   ├── core/
│   │   ├── figma_client.py          # Hoofdclient voor Figma API
│   │   ├── figma_slack_notifier.py  # Slack notificaties
│   │   └── slack_notify.py          # Slack utilities
│   └── Agent/
│       ├── FrontendDeveloper/
│       │   └── frontenddeveloper.py # Component generatie
│       ├── UXUIDesigner/
│       │   └── uxuidesigner.py      # Design analyse
│       └── DocumentationAgent/
│           └── documentationagent.py # Documentatie generatie
├── figma_cli.py                     # CLI tool
└── FIGMA_INTEGRATION_README.md      # Deze documentatie
```

## 🔄 Migratie van Demo naar Productie

### Stap 1: Zet demo mode uit
```bash
# In .env file
FIGMA_DEMO_MODE=false
```

### Stap 2: Voeg echte token toe
```bash
# In .env file
FIGMA_API_TOKEN=figd_your_real_token_here
```

### Stap 3: Test overschakeling
```bash
python3 -c "from agents.core.figma_client import FigmaClient; client = FigmaClient(); print('Real API working!')"
```

**Geen code wijzigingen nodig!** Dezelfde code werkt met zowel demo als echte API.

## 📚 Meer Informatie

- [Figma API Documentation](https://www.figma.com/developers/api)
- [Personal Access Tokens](https://www.figma.com/developers/api#access-tokens)
- [BMAD Agents Documentation](../docs/)

## 🤝 Bijdragen

Voor vragen of problemen:
1. Controleer eerst deze documentatie
2. Test met demo mode
3. Open een issue in de repository 