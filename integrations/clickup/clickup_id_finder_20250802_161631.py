#!/usr/bin/env python3
"""
ClickUp ID Finder

Dit script helpt je automatisch ClickUp IDs te vinden en te configureren.
"""

from typing import Dict, List, Optional

import requests


class ClickUpIDFinder:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.clickup.com/api/v2"
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }

    def get_teams(self) -> List[Dict]:
        """Haal alle teams op."""
        try:
            response = requests.get(f"{self.base_url}/team", headers=self.headers)
            response.raise_for_status()
            return response.json().get("teams", [])
        except Exception as e:
            print(f"❌ Error ophalen teams: {e}")
            return []

    def get_spaces(self, team_id: str) -> List[Dict]:
        """Haal alle spaces op voor een team."""
        try:
            response = requests.get(f"{self.base_url}/team/{team_id}/space", headers=self.headers)
            response.raise_for_status()
            return response.json().get("spaces", [])
        except Exception as e:
            print(f"❌ Error ophalen spaces: {e}")
            return []

    def get_folders(self, space_id: str) -> List[Dict]:
        """Haal alle folders op voor een space."""
        try:
            response = requests.get(f"{self.base_url}/space/{space_id}/folder", headers=self.headers)
            response.raise_for_status()
            return response.json().get("folders", [])
        except Exception as e:
            print(f"❌ Error ophalen folders: {e}")
            return []

    def get_lists(self, space_id: str, folder_id: Optional[str] = None) -> List[Dict]:
        """Haal alle lists op voor een space of folder."""
        try:
            if folder_id:
                url = f"{self.base_url}/folder/{folder_id}/list"
            else:
                url = f"{self.base_url}/space/{space_id}/list"

            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("lists", [])
        except Exception as e:
            print(f"❌ Error ophalen lists: {e}")
            return []

    def find_all_ids(self) -> Dict:
        """Vind alle IDs en toon ze in een overzicht."""
        print("🔍 ClickUp ID Finder")
        print("=" * 50)

        # Get teams
        print("\n📋 Teams:")
        teams = self.get_teams()
        if not teams:
            print("❌ Geen teams gevonden of API token ongeldig")
            return {}

        for team in teams:
            print(f"  🏢 {team.get('name', 'Unknown')} (ID: {team.get('id', 'Unknown')})")

        # Get spaces for first team
        if teams:
            team = teams[0]
            team_id = team.get("id")
            print(f"\n📁 Spaces voor team '{team.get('name')}':")

            spaces = self.get_spaces(team_id)
            if not spaces:
                print("  ❌ Geen spaces gevonden")
                return {"team_id": team_id}

            for space in spaces:
                print(f"  📂 {space.get('name', 'Unknown')} (ID: {space.get('id', 'Unknown')})")

            # Get folders and lists for first space
            if spaces:
                space = spaces[0]
                space_id = space.get("id")
                print(f"\n📂 Folders voor space '{space.get('name')}':")

                folders = self.get_folders(space_id)
                if folders:
                    for folder in folders:
                        print(f"  📁 {folder.get('name', 'Unknown')} (ID: {folder.get('id', 'Unknown')})")

                    # Get lists for first folder
                    folder = folders[0]
                    folder_id = folder.get("id")
                    print(f"\n📋 Lists voor folder '{folder.get('name')}':")

                    lists = self.get_lists(space_id, folder_id)
                    if lists:
                        for list_item in lists:
                            print(f"  📝 {list_item.get('name', 'Unknown')} (ID: {list_item.get('id', 'Unknown')})")

                    # Return recommended configuration
                    if lists:
                        recommended_list = lists[0]
                        return {
                            "team_id": team_id,
                            "space_id": space_id,
                            "folder_id": folder_id,
                            "list_id": recommended_list.get("id"),
                            "recommendation": {
                                "team_name": team.get("name"),
                                "space_name": space.get("name"),
                                "folder_name": folder.get("name"),
                                "list_name": recommended_list.get("name")
                            }
                        }
                else:
                    # No folders, get lists directly from space
                    print("  📋 Lists voor space (geen folders):")
                    lists = self.get_lists(space_id)
                    if lists:
                        for list_item in lists:
                            print(f"  📝 {list_item.get('name', 'Unknown')} (ID: {list_item.get('id', 'Unknown')})")

                        if lists:
                            recommended_list = lists[0]
                            return {
                                "team_id": team_id,
                                "space_id": space_id,
                                "list_id": recommended_list.get("id"),
                                "recommendation": {
                                    "team_name": team.get("name"),
                                    "space_name": space.get("name"),
                                    "list_name": recommended_list.get("name")
                                }
                            }

        return {}

def create_env_config(config: Dict) -> str:
    """Maak .env configuratie string."""
    env_config = f"""# ClickUp Configuration (Auto-generated)
CLICKUP_API_TOKEN=your_clickup_api_token_here
CLICKUP_TEAM_ID={config.get('team_id', 'your_team_id_here')}
CLICKUP_SPACE_ID={config.get('space_id', 'your_space_id_here')}"""

    if config.get("folder_id"):
        env_config += f"\nCLICKUP_FOLDER_ID={config.get('folder_id')}"
    else:
        env_config += "\nCLICKUP_FOLDER_ID=your_folder_id_here"

    env_config += f"\nCLICKUP_LIST_ID={config.get('list_id', 'your_list_id_here')}"

    return env_config

def main():
    """Main functie."""
    print("🚀 ClickUp ID Finder")
    print("=" * 50)

    # Get API token
    api_token = input("🔑 Voer je ClickUp API token in: ").strip()

    if not api_token:
        print("❌ API token is vereist")
        return

    # Test API token
    if not api_token.startswith("pk_"):
        print("⚠️  API token moet beginnen met 'pk_'")
        print("Ga naar: https://app.clickup.com/settings/apps")
        return

    # Find IDs
    finder = ClickUpIDFinder(api_token)
    config = finder.find_all_ids()

    if not config:
        print("\n❌ Kon geen configuratie vinden")
        return

    # Show recommendation
    print("\n" + "=" * 50)
    print("🎯 AANBEVOLEN CONFIGURATIE")
    print("=" * 50)

    recommendation = config.get("recommendation", {})
    print(f"Team: {recommendation.get('team_name', 'Unknown')}")
    print(f"Space: {recommendation.get('space_name', 'Unknown')}")
    if recommendation.get("folder_name"):
        print(f"Folder: {recommendation.get('folder_name', 'Unknown')}")
    print(f"List: {recommendation.get('list_name', 'Unknown')}")

    # Generate .env config
    env_config = create_env_config(config)

    print("\n📝 Voeg deze regels toe aan je .env file:")
    print("-" * 50)
    print(env_config)
    print("-" * 50)

    # Save to file
    save_to_file = input("\n💾 Wil je deze configuratie opslaan in .env.template? (y/n): ").strip().lower()

    if save_to_file == "y":
        try:
            with open(".env.template", "w") as f:
                f.write(env_config)
            print("✅ Configuratie opgeslagen in .env.template")
            print("📝 Kopieer de inhoud naar je .env file en vul je API token in")
        except Exception as e:
            print(f"❌ Error opslaan configuratie: {e}")

    print("\n🎉 ClickUp ID Finder voltooid!")
    print("📋 Volgende stappen:")
    print("1. Voeg de configuratie toe aan je .env file")
    print("2. Test de integratie: python tests/integration/test_clickup_integration.py")
    print("3. Start met project management!")

if __name__ == "__main__":
    main()
