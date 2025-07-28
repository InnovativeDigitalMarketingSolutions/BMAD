#!/usr/bin/env python3
"""
ClickUp Setup Helper

Dit script helpt je met het configureren van de ClickUp integratie.
"""

import os
from pathlib import Path


def check_env_file():
    """Check of .env file bestaat en toon huidige configuratie."""
    env_path = Path(".env")

    if not env_path.exists():
        print("❌ .env file niet gevonden!")
        print("Maak een .env file aan in de root van het project.")
        return False

    print("✅ .env file gevonden")
    return True

def show_clickup_setup_guide():
    """Toon ClickUp setup instructies."""
    print("\n" + "="*60)
    print("🔧 CLICKUP SETUP INSTRUCTIES")
    print("="*60)

    print("\n📋 Stap 1: API Key Genereren")
    print("1. Ga naar https://app.clickup.com/settings/apps")
    print("2. Klik op 'Create App'")
    print("3. Geef je app een naam (bijv. 'BMAD Integration')")
    print("4. Kopieer de API Key")

    print("\n📋 Stap 2: Space, Folder en List IDs Vinden")
    print("1. Ga naar je ClickUp workspace")
    print("2. Open de Space waar je projecten wilt maken")
    print("3. Open de Folder waar je taken wilt maken")
    print("4. Open de List waar je taken wilt maken")
    print("5. Kopieer de IDs uit de URL:")
    print("   - Space ID: https://app.clickup.com/[TEAM_ID]/v/li/[SPACE_ID]")
    print("   - Folder ID: https://app.clickup.com/[TEAM_ID]/v/li/[SPACE_ID]/f/[FOLDER_ID]")
    print("   - List ID: https://app.clickup.com/[TEAM_ID]/v/li/[SPACE_ID]/f/[FOLDER_ID]/li/[LIST_ID]")

    print("\n📋 Stap 3: .env File Updaten")
    print("Voeg deze regels toe aan je .env file:")
    print("""
# ClickUp Configuration
CLICKUP_API_TOKEN=your_clickup_api_key_here
CLICKUP_TEAM_ID=your_clickup_team_id_here
CLICKUP_SPACE_ID=your_space_id_here
CLICKUP_FOLDER_ID=your_folder_id_here
CLICKUP_LIST_ID=your_list_id_here
""")

def create_env_template():
    """Maak een .env template aan."""
    template_content = """# BMAD Environment Configuration

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Figma API Configuration
FIGMA_API_TOKEN=your_figma_api_token_here
FIGMA_DEMO_MODE=true

# ClickUp Configuration
CLICKUP_API_TOKEN=your_clickup_api_token_here
CLICKUP_TEAM_ID=your_clickup_team_id_here
CLICKUP_SPACE_ID=your_space_id_here
CLICKUP_FOLDER_ID=your_folder_id_here
CLICKUP_LIST_ID=your_list_id_here

# Slack Configuration
SLACK_BOT_TOKEN=your_slack_bot_token_here
SLACK_SIGNING_SECRET=your_slack_signing_secret_here
SLACK_WEBHOOK_URL=your_slack_webhook_url_here

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# BMAD Configuration
BMAD_LOG_LEVEL=INFO
BMAD_CACHE_ENABLED=true
BMAD_MAX_RETRIES=3

# Development Configuration
DEBUG=true
ENVIRONMENT=development
"""

    with open(".env.template", "w") as f:
        f.write(template_content)

    print("✅ .env.template aangemaakt")
    print("📝 Kopieer .env.template naar .env en vul je waarden in")

def test_clickup_connection():
    """Test ClickUp verbinding als credentials beschikbaar zijn."""
    required_vars = [
        "CLICKUP_API_TOKEN",
        "CLICKUP_TEAM_ID",
        "CLICKUP_SPACE_ID",
        "CLICKUP_FOLDER_ID",
        "CLICKUP_LIST_ID"
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"\n❌ Ontbrekende environment variables: {', '.join(missing_vars)}")
        return False

    print("\n✅ Alle ClickUp environment variables zijn ingesteld!")
    print("🧪 Test de verbinding met: python tests/integration/test_clickup_integration.py")
    return True

def main():
    """Main setup functie."""
    print("🚀 ClickUp Setup Helper")
    print("="*40)

    # Check .env file
    if not check_env_file():
        print("\n📝 Wil je een .env template aanmaken? (y/n): ", end="")
        if input().lower() == "y":
            create_env_template()
        return

    # Show setup guide
    show_clickup_setup_guide()

    # Offer automatic ID finder
    print("\n" + "="*40)
    print("🔍 AUTOMATISCHE CONFIGURATIE")
    print("="*40)

    print("💡 Tip: Gebruik de automatische ClickUp ID Finder!")
    print("Run: python clickup_id_finder.py")
    print("Dit script helpt je automatisch alle benodigde IDs te vinden.")

    # Test connection
    print("\n" + "="*40)
    print("🔍 TESTING CONFIGURATION")
    print("="*40)

    if test_clickup_connection():
        print("\n🎉 ClickUp setup is klaar!")
        print("📋 Volgende stappen:")
        print("1. Test de verbinding: python tests/integration/test_clickup_integration.py")
        print("2. Test agent integratie: python test_llm_clickup_integration.py")
        print("3. Start met project management!")
    else:
        print("\n⚠️  Vul eerst de ontbrekende environment variables in.")
        print("📝 Opties:")
        print("   - Gebruik de automatische finder: python clickup_id_finder.py")
        print("   - Volg de handmatige instructies hierboven")

if __name__ == "__main__":
    main()
