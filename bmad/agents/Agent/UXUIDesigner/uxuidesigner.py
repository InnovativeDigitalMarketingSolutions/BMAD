from bmad.agents.core.message_bus import publish, subscribe
from bmad.agents.core.supabase_context import save_context, get_context
from bmad.agents.core.llm_client import ask_openai
from bmad.agents.core.figma_client import FigmaClient
import logging
import json
from typing import Dict, List, Optional

class UXUIDesigner:
    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        publish("design_finalized", {"status": "success", "agent": "UXUIDesigner"})
        save_context("UXUIDesigner", {"design_status": "finalized"})
        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("UXUIDesigner")
        print(f"Opgehaalde context: {context}")

def design_feedback(feedback_text):
    prompt = f"Analyseer de volgende design feedback en doe 2 concrete verbetervoorstellen:\n{feedback_text}"
    result = ask_openai(prompt)
    logging.info(f"[UXUIDesigner][LLM Design Feedback]: {result}")
    return result

def document_component(component_desc):
    prompt = f"Genereer een korte documentatie voor deze UI-component:\n{component_desc}"
    result = ask_openai(prompt)
    logging.info(f"[UXUIDesigner][LLM Component Doc]: {result}")
    return result

def analyze_figma_design(figma_file_id: str) -> Dict:
    """
    Analyseer een Figma design op layout, kleurgebruik, en accessibility-signalen.
    """
    try:
        client = FigmaClient()
        
        # Haal file data op
        file_data = client.get_file(figma_file_id)
        
        logging.info(f"[UXUIDesigner][Figma Analysis] Analyzing file: {file_data.get('name', 'Unknown')}")
        
        # Analyseer document structuur
        document = file_data.get('document', {})
        pages = document.get('children', [])
        
        analysis_result = {
            'file_name': file_data.get('name', ''),
            'file_id': figma_file_id,
            'total_pages': len(pages),
            'pages': [],
            'design_insights': {},
            'accessibility_issues': [],
            'color_analysis': {},
            'layout_analysis': {}
        }
        
        # Analyseer elke pagina
        for page in pages:
            page_analysis = analyze_page(page)
            analysis_result['pages'].append(page_analysis)
        
        # Genereer algemene design insights met LLM
        design_insights = generate_design_insights(analysis_result)
        analysis_result['design_insights'] = design_insights
        
        # Analyseer kleurgebruik
        color_analysis = analyze_colors(file_data)
        analysis_result['color_analysis'] = color_analysis
        
        # Analyseer layout
        layout_analysis = analyze_layout(file_data)
        analysis_result['layout_analysis'] = layout_analysis
        
        # Check accessibility
        accessibility_issues = check_accessibility(file_data)
        analysis_result['accessibility_issues'] = accessibility_issues
        
        logging.info(f"[UXUIDesigner][Figma Analysis] Completed analysis for {len(pages)} pages")
        return analysis_result
        
    except Exception as e:
        logging.error(f"[UXUIDesigner][Figma Analysis Error]: {str(e)}")
        return {'error': str(e)}

def analyze_page(page_data: Dict) -> Dict:
    """Analyseer een individuele Figma pagina."""
    return {
        'name': page_data.get('name', ''),
        'id': page_data.get('id', ''),
        'type': page_data.get('type', ''),
        'children_count': len(page_data.get('children', [])),
        'has_components': has_components(page_data),
        'has_text': has_text_elements(page_data),
        'has_images': has_image_elements(page_data)
    }

def has_components(node: Dict) -> bool:
    """Check of een node componenten bevat."""
    if node.get('type') == 'COMPONENT':
        return True
    for child in node.get('children', []):
        if has_components(child):
            return True
    return False

def has_text_elements(node: Dict) -> bool:
    """Check of een node tekst elementen bevat."""
    if node.get('type') == 'TEXT':
        return True
    for child in node.get('children', []):
        if has_text_elements(child):
            return True
    return False

def has_image_elements(node: Dict) -> bool:
    """Check of een node afbeeldingen bevat."""
    if node.get('type') in ['RECTANGLE', 'ELLIPSE', 'VECTOR']:
        fills = node.get('fills', [])
        for fill in fills:
            if fill.get('type') == 'IMAGE':
                return True
    for child in node.get('children', []):
        if has_image_elements(child):
            return True
    return False

def generate_design_insights(analysis_data: Dict) -> Dict:
    """Genereer design insights met LLM."""
    try:
        prompt = f"""
        Analyseer deze Figma design data en geef design insights:
        
        {json.dumps(analysis_data, indent=2)}
        
        Geef een korte analyse van:
        1. Design patterns en consistentie
        2. Mogelijke verbeteringen
        3. Best practices die gevolgd worden
        
        Antwoord in JSON format.
        """
        
        result = ask_openai(prompt)
        logging.info(f"[UXUIDesigner][Design Insights] Generated insights")
        return {'insights': result}
        
    except Exception as e:
        logging.error(f"[UXUIDesigner][Design Insights Error]: {str(e)}")
        return {'error': str(e)}

def analyze_colors(file_data: Dict) -> Dict:
    """Analyseer kleurgebruik in het design."""
    colors = {}
    
    def extract_colors(node):
        fills = node.get('fills', [])
        for fill in fills:
            if fill.get('type') == 'SOLID':
                color = fill.get('color', {})
                if color:
                    color_key = f"rgb({int(color.get('r', 0) * 255)}, {int(color.get('g', 0) * 255)}, {int(color.get('b', 0) * 255)})"
                    colors[color_key] = colors.get(color_key, 0) + 1
        
        for child in node.get('children', []):
            extract_colors(child)
    
    document = file_data.get('document', {})
    extract_colors(document)
    
    return {
        'total_colors': len(colors),
        'color_frequency': colors,
        'primary_colors': sorted(colors.items(), key=lambda x: x[1], reverse=True)[:5]
    }

def analyze_layout(file_data: Dict) -> Dict:
    """Analyseer layout structuur."""
    layout_info = {
        'total_frames': 0,
        'total_groups': 0,
        'total_components': 0,
        'nested_depth': 0
    }
    
    def analyze_node(node, depth=0):
        layout_info['nested_depth'] = max(layout_info['nested_depth'], depth)
        
        if node.get('type') == 'FRAME':
            layout_info['total_frames'] += 1
        elif node.get('type') == 'GROUP':
            layout_info['total_groups'] += 1
        elif node.get('type') == 'COMPONENT':
            layout_info['total_components'] += 1
        
        for child in node.get('children', []):
            analyze_node(child, depth + 1)
    
    document = file_data.get('document', {})
    analyze_node(document)
    
    return layout_info

def check_accessibility(file_data: Dict) -> List[Dict]:
    """Check accessibility issues in het design."""
    issues = []
    
    def check_node(node):
        # Check voor tekst contrast
        if node.get('type') == 'TEXT':
            fills = node.get('fills', [])
            if not fills:
                issues.append({
                    'type': 'accessibility',
                    'severity': 'medium',
                    'message': f'Text element "{node.get("name", "Unknown")}" heeft geen fills/kleur',
                    'node_id': node.get('id')
                })
        
        # Check voor alt tekst op afbeeldingen
        if node.get('type') in ['RECTANGLE', 'ELLIPSE']:
            fills = node.get('fills', [])
            for fill in fills:
                if fill.get('type') == 'IMAGE' and not node.get('name', '').startswith('alt:'):
                    issues.append({
                        'type': 'accessibility',
                        'severity': 'low',
                        'message': f'Image element "{node.get("name", "Unknown")}" heeft geen alt tekst',
                        'node_id': node.get('id')
                    })
        
        for child in node.get('children', []):
            check_node(child)
    
    document = file_data.get('document', {})
    check_node(document)
    
    return issues

def on_figma_analysis_requested(event):
    """Event handler voor Figma design analyse requests."""
    figma_file_id = event.get("figma_file_id", "")
    
    if not figma_file_id:
        logging.error("[UXUIDesigner] No figma_file_id provided in event")
        return
    
    result = analyze_figma_design(figma_file_id)
    logging.info(f"[UXUIDesigner][Event] Processed Figma analysis request: {result}")
    
    # Publiceer resultaat
    publish("figma_analysis_completed", {
        "file_id": figma_file_id,
        "analysis": result
    })

def on_design_feedback_requested(event):
    feedback_text = event.get("feedback_text", "")
    design_feedback(feedback_text)

def on_document_component(event):
    component_desc = event.get("component_desc", "")
    document_component(component_desc)

# Event subscriptions
subscribe("design_feedback_requested", on_design_feedback_requested)
subscribe("document_component", on_document_component)
subscribe("figma_analysis_requested", on_figma_analysis_requested)
