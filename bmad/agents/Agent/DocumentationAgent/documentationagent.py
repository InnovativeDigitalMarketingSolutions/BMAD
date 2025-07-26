import glob
import logging
from agents.core.slack_notify import send_slack_message
from agents.core.llm import ask_openai
from agents.core.message_bus import subscribe
from agents.core.figma_client import FigmaClient
import json
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def summarize_changelogs():
    changelogs = glob.glob("bmad/agents/Agent/*/changelog.md")
    for log_path in changelogs:
        with open(log_path, encoding="utf-8") as f:
            content = f.read(256)  # Alleen eerste 256 tekens voor samenvatting
        logging.info(f"[DocumentationAgent] Samenvatting {log_path}: {content}")
        send_slack_message(f"[DocumentationAgent] Samenvatting {log_path}: {content}")

def summarize_changelogs_llm(changelog_texts):
    prompt = f"Vat de volgende changelogs samen in maximaal 5 bullets:\n" + "\n".join(changelog_texts)
    result = ask_openai(prompt)
    logging.info(f"[DocumentationAgent][LLM Changelog-samenvatting]: {result}")
    return result

def document_figma_ui(figma_file_id: str) -> Dict:
    """
    Documenteer UI-onderdelen uit een Figma file met exports en structuurinfo.
    """
    try:
        client = FigmaClient()
        
        # Haal file data op
        file_data = client.get_file(figma_file_id)
        components_data = client.get_components(figma_file_id)
        
        logging.info(f"[DocumentationAgent][Figma UI Doc] Documenting file: {file_data.get('name', 'Unknown')}")
        
        # Genereer documentatie structuur
        documentation = {
            'file_name': file_data.get('name', ''),
            'file_id': figma_file_id,
            'last_modified': file_data.get('lastModified', ''),
            'version': file_data.get('version', ''),
            'components': [],
            'pages': [],
            'design_system': {},
            'export_info': {}
        }
        
        # Documenteer componenten
        components = components_data.get('meta', {}).get('components', {})
        for component_id, component_info in components.items():
            component_doc = document_component_info(component_info, component_id)
            documentation['components'].append(component_doc)
        
        # Documenteer pagina's
        document = file_data.get('document', {})
        pages = document.get('children', [])
        for page in pages:
            page_doc = document_page_info(page)
            documentation['pages'].append(page_doc)
        
        # Genereer design system documentatie
        design_system = generate_design_system_doc(file_data)
        documentation['design_system'] = design_system
        
        # Genereer export informatie
        export_info = generate_export_info(file_data)
        documentation['export_info'] = export_info
        
        # Genereer markdown documentatie
        markdown_doc = generate_markdown_documentation(documentation)
        
        result = {
            'documentation': documentation,
            'markdown': markdown_doc,
            'total_components': len(documentation['components']),
            'total_pages': len(documentation['pages'])
        }
        
        logging.info(f"[DocumentationAgent][Figma UI Doc] Generated documentation for {len(documentation['components'])} components")
        return result
        
    except Exception as e:
        logging.error(f"[DocumentationAgent][Figma UI Doc Error]: {str(e)}")
        return {'error': str(e)}

def document_component_info(component_info: Dict, component_id: str) -> Dict:
    """Documenteer een individuele component."""
    return {
        'id': component_id,
        'name': component_info.get('name', ''),
        'description': component_info.get('description', ''),
        'key': component_info.get('key', ''),
        'created_at': component_info.get('created_at', ''),
        'updated_at': component_info.get('updated_at', ''),
        'usage_count': component_info.get('usage_count', 0),
        'documentation': generate_component_documentation(component_info)
    }

def document_page_info(page_data: Dict) -> Dict:
    """Documenteer een individuele pagina."""
    return {
        'name': page_data.get('name', ''),
        'id': page_data.get('id', ''),
        'type': page_data.get('type', ''),
        'children_count': len(page_data.get('children', [])),
        'description': generate_page_description(page_data)
    }

def generate_component_documentation(component_info: Dict) -> str:
    """Genereer documentatie voor een component met LLM."""
    try:
        prompt = f"""
        Genereer korte documentatie voor dit Figma component:
        
        Naam: {component_info.get('name', '')}
        Beschrijving: {component_info.get('description', '')}
        Key: {component_info.get('key', '')}
        
        Geef een korte beschrijving van:
        1. Doel van het component
        2. Wanneer te gebruiken
        3. Belangrijke eigenschappen
        
        Antwoord in maximaal 3 zinnen.
        """
        
        result = ask_openai(prompt)
        return result
        
    except Exception as e:
        logging.error(f"[DocumentationAgent][Component Doc Error]: {str(e)}")
        return "Documentatie kon niet worden gegenereerd."

def generate_page_description(page_data: Dict) -> str:
    """Genereer beschrijving voor een pagina met LLM."""
    try:
        prompt = f"""
        Genereer een korte beschrijving voor deze Figma pagina:
        
        Naam: {page_data.get('name', '')}
        Type: {page_data.get('type', '')}
        Aantal kinderen: {len(page_data.get('children', []))}
        
        Geef een korte beschrijving van het doel van deze pagina.
        """
        
        result = ask_openai(prompt)
        return result
        
    except Exception as e:
        logging.error(f"[DocumentationAgent][Page Description Error]: {str(e)}")
        return "Beschrijving kon niet worden gegenereerd."

def generate_design_system_doc(file_data: Dict) -> Dict:
    """Genereer design system documentatie."""
    design_system = {
        'colors': extract_colors(file_data),
        'typography': extract_typography(file_data),
        'spacing': extract_spacing(file_data),
        'components': extract_design_system_components(file_data)
    }
    
    return design_system

def extract_colors(file_data: Dict) -> List[Dict]:
    """Extraheer kleuren uit het design."""
    colors = []
    
    def extract_colors_from_node(node):
        fills = node.get('fills', [])
        for fill in fills:
            if fill.get('type') == 'SOLID':
                color = fill.get('color', {})
                if color:
                    color_info = {
                        'r': int(color.get('r', 0) * 255),
                        'g': int(color.get('g', 0) * 255),
                        'b': int(color.get('b', 0) * 255),
                        'hex': rgb_to_hex(color.get('r', 0), color.get('g', 0), color.get('b', 0)),
                        'node_name': node.get('name', '')
                    }
                    if color_info not in colors:
                        colors.append(color_info)
        
        for child in node.get('children', []):
            extract_colors_from_node(child)
    
    document = file_data.get('document', {})
    extract_colors_from_node(document)
    
    return colors

def extract_typography(file_data: Dict) -> List[Dict]:
    """Extraheer typography uit het design."""
    typography = []
    
    def extract_typography_from_node(node):
        if node.get('type') == 'TEXT':
            style = node.get('style', {})
            if style:
                typo_info = {
                    'font_family': style.get('fontFamily', ''),
                    'font_size': style.get('fontSize', ''),
                    'font_weight': style.get('fontWeight', ''),
                    'line_height': style.get('lineHeightPx', ''),
                    'node_name': node.get('name', '')
                }
                if typo_info not in typography:
                    typography.append(typo_info)
        
        for child in node.get('children', []):
            extract_typography_from_node(child)
    
    document = file_data.get('document', {})
    extract_typography_from_node(document)
    
    return typography

def extract_spacing(file_data: Dict) -> Dict:
    """Extraheer spacing patterns uit het design."""
    spacing_values = []
    
    def extract_spacing_from_node(node):
        if 'absoluteBoundingBox' in node:
            bounds = node['absoluteBoundingBox']
            if bounds:
                spacing_values.extend([
                    bounds.get('x', 0),
                    bounds.get('y', 0),
                    bounds.get('width', 0),
                    bounds.get('height', 0)
                ])
        
        for child in node.get('children', []):
            extract_spacing_from_node(child)
    
    document = file_data.get('document', {})
    extract_spacing_from_node(document)
    
    # Vind unieke spacing waarden
    unique_spacing = sorted(list(set(spacing_values)))
    
    return {
        'unique_values': unique_spacing,
        'common_values': [val for val in unique_spacing if spacing_values.count(val) > 1]
    }

def extract_design_system_components(file_data: Dict) -> List[Dict]:
    """Extraheer design system componenten."""
    components = []
    
    def extract_components_from_node(node):
        if node.get('type') == 'COMPONENT':
            component_info = {
                'name': node.get('name', ''),
                'id': node.get('id', ''),
                'description': node.get('description', ''),
                'type': 'component'
            }
            components.append(component_info)
        
        for child in node.get('children', []):
            extract_components_from_node(child)
    
    document = file_data.get('document', {})
    extract_components_from_node(document)
    
    return components

def generate_export_info(file_data: Dict) -> Dict:
    """Genereer export informatie."""
    export_info = {
        'exportable_nodes': [],
        'image_formats': ['PNG', 'JPG', 'SVG', 'PDF'],
        'export_settings': {}
    }
    
    def find_exportable_nodes(node):
        if node.get('exportSettings'):
            export_info['exportable_nodes'].append({
                'name': node.get('name', ''),
                'id': node.get('id', ''),
                'type': node.get('type', ''),
                'export_settings': node.get('exportSettings', [])
            })
        
        for child in node.get('children', []):
            find_exportable_nodes(child)
    
    document = file_data.get('document', {})
    find_exportable_nodes(document)
    
    return export_info

def generate_markdown_documentation(documentation: Dict) -> str:
    """Genereer markdown documentatie."""
    markdown = f"""# {documentation['file_name']} - UI Documentation

## Overzicht
- **File ID**: {documentation['file_id']}
- **Laatst gewijzigd**: {documentation['last_modified']}
- **Versie**: {documentation['version']}
- **Aantal componenten**: {len(documentation['components'])}
- **Aantal pagina's**: {len(documentation['pages'])}

## Componenten
"""
    
    for component in documentation['components']:
        markdown += f"""
### {component['name']}
- **ID**: {component['id']}
- **Beschrijving**: {component['description']}
- **Documentatie**: {component['documentation']}
- **Gebruik**: {component['usage_count']} keer gebruikt

"""
    
    markdown += """
## Pagina's
"""
    
    for page in documentation['pages']:
        markdown += f"""
### {page['name']}
- **Type**: {page['type']}
- **Aantal elementen**: {page['children_count']}
- **Beschrijving**: {page['description']}

"""
    
    markdown += """
## Design System

### Kleuren
"""
    
    for color in documentation['design_system'].get('colors', []):
        markdown += f"- RGB({color['r']}, {color['g']}, {color['b']}) - {color['hex']}\n"
    
    markdown += """
### Typography
"""
    
    for typo in documentation['design_system'].get('typography', []):
        markdown += f"- {typo['font_family']} {typo['font_size']}px - {typo['font_weight']}\n"
    
    return markdown

def rgb_to_hex(r: float, g: float, b: float) -> str:
    """Converteer RGB naar hex."""
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

def on_figma_documentation_requested(event):
    """Event handler voor Figma documentatie requests."""
    figma_file_id = event.get("figma_file_id", "")
    
    if not figma_file_id:
        logging.error("[DocumentationAgent] No figma_file_id provided in event")
        return
    
    result = document_figma_ui(figma_file_id)
    logging.info(f"[DocumentationAgent][Event] Processed Figma documentation request: {result}")

def on_summarize_changelogs(event):
    changelog_texts = event.get("changelog_texts", [])
    summarize_changelogs_llm(changelog_texts)

# Event subscriptions
subscribe("summarize_changelogs", on_summarize_changelogs)
subscribe("figma_documentation_requested", on_figma_documentation_requested)
