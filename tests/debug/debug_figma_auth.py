#!/usr/bin/env python3
"""
Figma Authentication Debug Script
=================================

Dit script helpt bij het identificeren en oplossen van Figma API authenticatie problemen.
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_token_format():
    """Test de token format."""
    print("🔍 Testing token format...")
    
    token = os.getenv('FIGMA_API_TOKEN')
    if not token:
        print("❌ FIGMA_API_TOKEN is niet ingesteld in .env")
        return False
    
    print(f"✅ Token gevonden (length: {len(token)})")
    print(f"✅ Format: {token[:10]}...{token[-10:]}")
    print(f"✅ Starts with 'figd_': {token.startswith('figd_')}")
    print(f"✅ No spaces: {' ' not in token}")
    print(f"✅ No newlines: {'\\n' not in token}")
    
    return True

def test_api_endpoint(endpoint, description):
    """Test een specifieke API endpoint."""
    print(f"\n🔗 Testing {description}...")
    
    token = os.getenv('FIGMA_API_TOKEN')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f'https://api.figma.com/v1{endpoint}', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ {description} - SUCCESS")
            return True
        elif response.status_code == 403:
            print(f"❌ {description} - FORBIDDEN (Invalid token or no access)")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"⚠️  {description} - Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {description} - ERROR: {str(e)}")
        return False

def test_user_access():
    """Test of de token toegang heeft tot user info."""
    return test_api_endpoint('/me', 'User info access')

def test_public_file_access():
    """Test toegang tot publieke files."""
    return test_api_endpoint('/files/FigmaDesignSystem', 'Public file access')

def test_specific_file_access(file_id):
    """Test toegang tot een specifieke file."""
    return test_api_endpoint(f'/files/{file_id}', f'Specific file access ({file_id})')

def test_file_components(file_id):
    """Test toegang tot file componenten."""
    return test_api_endpoint(f'/files/{file_id}/components', f'File components ({file_id})')

def test_file_comments(file_id):
    """Test toegang tot file comments."""
    return test_api_endpoint(f'/files/{file_id}/comments', f'File comments ({file_id})')

def provide_solutions():
    """Geef oplossingen voor gevonden problemen."""
    print("\n" + "="*60)
    print("🔧 MOGELIJKE OPLOSSINGEN")
    print("="*60)
    
    print("\n1. TOKEN PROBLEMEN:")
    print("   • Genereer een nieuwe Personal Access Token")
    print("   • Ga naar: https://www.figma.com/settings")
    print("   • Account → Personal access tokens → Generate new token")
    print("   • Kopieer de token direct zonder extra spaties")
    
    print("\n2. FILE TOEGANG PROBLEMEN:")
    print("   • Controleer of je eigenaar bent van de file")
    print("   • Of zet de file op 'Anyone with the link → can view'")
    print("   • Of maak een kopie van de file in je eigen account")
    
    print("\n3. ACCOUNT PROBLEMEN:")
    print("   • Zorg dat je ingelogd bent met het juiste Figma account")
    print("   • Controleer of je account geen beperkingen heeft")
    print("   • Verifieer dat je account actief is")
    
    print("\n4. API ENDPOINT PROBLEMEN:")
    print("   • Gebruik alleen REST endpoints vanaf https://api.figma.com")
    print("   • Gebruik file keys, niet volledige URLs")
    print("   • Controleer of de file ID correct is")
    
    print("\n5. TEST STAPPEN:")
    print("   • Test eerst met een publieke file")
    print("   • Test dan met je eigen files")
    print("   • Test ten slotte met gedeelde files")

def main():
    """Hoofdfunctie."""
    print("🔍 FIGMA AUTHENTICATION DEBUG SCRIPT")
    print("="*50)
    
    # Test token format
    if not test_token_format():
        provide_solutions()
        return
    
    # Test verschillende endpoints
    results = []
    
    results.append(test_user_access())
    results.append(test_public_file_access())
    
    # Test specifieke file (als gegeven)
    file_id = "3Um1EVNov6Hf29HR9sjapE"
    if file_id:
        results.append(test_specific_file_access(file_id))
        results.append(test_file_components(file_id))
        results.append(test_file_comments(file_id))
    
    # Samenvatting
    print("\n" + "="*50)
    print("📊 SAMENVATTING")
    print("="*50)
    
    successful_tests = sum(results)
    total_tests = len(results)
    
    print(f"Tests uitgevoerd: {total_tests}")
    print(f"Succesvol: {successful_tests}")
    print(f"Gefaald: {total_tests - successful_tests}")
    
    if successful_tests == 0:
        print("\n❌ ALLE TESTS GEFAALD")
        print("Het probleem ligt waarschijnlijk bij de token of account toegang.")
    elif successful_tests < total_tests:
        print("\n⚠️  GEDEELTELIJK SUCCES")
        print("Sommige endpoints werken, andere niet. Mogelijk file-specifieke problemen.")
    else:
        print("\n✅ ALLE TESTS SUCCESVOL")
        print("De authenticatie werkt correct!")
    
    # Toon oplossingen
    if successful_tests < total_tests:
        provide_solutions()

if __name__ == "__main__":
    main() 