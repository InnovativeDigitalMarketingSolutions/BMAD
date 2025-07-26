from agents.core.llm_client import ask_openai
from agents.core.message_bus import subscribe
from agents.core.figma_client import FigmaClient
import logging
import json
from typing import Dict, List, Optional

def code_review(code_snippet):
    prompt = f"Geef een korte code review van de volgende code:\n{code_snippet}"
    result = ask_openai(prompt)
    logging.info(f"[FrontendDeveloper][LLM Code Review]: {result}")
    return result

def bug_root_cause(error_log):
    prompt = f"Analyseer deze foutmelding/log en geef een mogelijke oorzaak en oplossing:\n{error_log}"
    result = ask_openai(prompt)
    logging.info(f"[FrontendDeveloper][LLM Bug Analyse]: {result}")
    return result

def parse_figma_components(figma_file_id: str) -> Dict:
    """
    Parse Figma components en converteer naar een abstract model voor code generatie.
    """
    try:
        client = FigmaClient()
        
        # Haal file info op
        file_data = client.get_file(figma_file_id)
        components_data = client.get_components(figma_file_id)
        
        logging.info(f"[FrontendDeveloper][Figma Parse] File: {file_data.get('name', 'Unknown')}")
        
        # Parse components naar abstract model
        components = []
        for component_id, component_info in components_data.get('meta', {}).get('components', {}).items():
            component = {
                'id': component_id,
                'name': component_info.get('name', ''),
                'description': component_info.get('description', ''),
                'key': component_info.get('key', ''),
                'created_at': component_info.get('created_at', ''),
                'updated_at': component_info.get('updated_at', '')
            }
            components.append(component)
        
        return {
            'file_name': file_data.get('name', ''),
            'file_id': figma_file_id,
            'components': components,
            'total_components': len(components)
        }
        
    except Exception as e:
        logging.error(f"[FrontendDeveloper][Figma Parse Error]: {str(e)}")
        return {'error': str(e)}

def generate_nextjs_component(component_data: Dict, component_name: str) -> str:
    """
    Genereer Next.js + Tailwind component code uit Figma component data.
    """
    try:
        # Maak een prompt voor de LLM om component code te genereren
        prompt = f"""
        Genereer een Next.js component met Tailwind CSS voor het volgende Figma component:
        
        Component Naam: {component_name}
        Component Data: {json.dumps(component_data, indent=2)}
        
        Vereisten:
        - Gebruik Next.js functional component syntax
        - Gebruik Tailwind CSS voor styling
        - Maak het component responsive
        - Voeg TypeScript types toe
        - Zorg voor goede accessibility
        - Gebruik moderne React patterns (hooks, etc.)
        
        Genereer alleen de component code, geen uitleg.
        """
        
        result = ask_openai(prompt)
        logging.info(f"[FrontendDeveloper][Component Generation] Generated component: {component_name}")
        return result
        
    except Exception as e:
        logging.error(f"[FrontendDeveloper][Component Generation Error]: {str(e)}")
        return f"// Error generating component: {str(e)}"

def generate_components_from_figma(figma_file_id: str, output_dir: str = "components") -> Dict:
    """
    Hoofdfunctie: Genereer alle componenten uit een Figma file.
    """
    try:
        # Parse Figma components
        figma_data = parse_figma_components(figma_file_id)
        
        if 'error' in figma_data:
            return figma_data
        
        generated_components = []
        
        # Genereer component voor elke Figma component
        for component in figma_data['components']:
            component_name = component['name'].replace(' ', '').replace('-', '')  # Clean name
            component_code = generate_nextjs_component(component, component_name)
            
            generated_components.append({
                'name': component_name,
                'figma_id': component['id'],
                'code': component_code,
                'file_path': f"{output_dir}/{component_name}.tsx"
            })
        
        result = {
            'file_name': figma_data['file_name'],
            'file_id': figma_file_id,
            'generated_components': generated_components,
            'total_generated': len(generated_components)
        }
        
        logging.info(f"[FrontendDeveloper][Figma Codegen] Generated {len(generated_components)} components")
        return result
        
    except Exception as e:
        logging.error(f"[FrontendDeveloper][Figma Codegen Error]: {str(e)}")
        return {'error': str(e)}

def on_figma_components_requested(event):
    """Event handler voor Figma component generatie requests."""
    figma_file_id = event.get("figma_file_id", "")
    output_dir = event.get("output_dir", "components")
    
    if not figma_file_id:
        logging.error("[FrontendDeveloper] No figma_file_id provided in event")
        return
    
    result = generate_components_from_figma(figma_file_id, output_dir)
    logging.info(f"[FrontendDeveloper][Event] Processed Figma components request: {result}")

def on_code_review_requested(event):
    code_snippet = event.get("code_snippet", "")
    code_review(code_snippet)

def on_bug_analysis_requested(event):
    error_log = event.get("error_log", "")
    bug_root_cause(error_log)

# Event subscriptions
subscribe("code_review_requested", on_code_review_requested)
subscribe("bug_analysis_requested", on_bug_analysis_requested)
subscribe("figma_components_requested", on_figma_components_requested)
