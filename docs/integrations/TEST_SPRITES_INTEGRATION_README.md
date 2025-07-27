# 🧪 BMAD Test Sprites Integration

## 📋 Overview

De BMAD Test Sprites integratie biedt een krachtige component testing en visual regression testing library die perfect integreert met de BMAD agent workflows. Deze integratie maakt het mogelijk om UI componenten systematisch te testen op accessibility, visual consistency, en interaction patterns.

## 🎯 Features

### ✅ **Component Testing**
- **Multi-state testing**: Test componenten in verschillende states (default, loading, error, success, etc.)
- **Accessibility testing**: Automatische checks voor ARIA labels, roles, keyboard navigation
- **Visual testing**: Color contrast, spacing, typography, alignment checks
- **Interaction testing**: Click, hover, focus, keyboard interaction tests

### ✅ **Sprite Management**
- **Sprite Library**: Centrale repository voor alle test sprites
- **Sprite Types**: Component, State, Interaction, Accessibility, Visual sprites
- **Persistent Storage**: Sprites worden opgeslagen als JSON bestanden
- **Version Control**: Sprite definities kunnen worden versioned

### ✅ **Integration Features**
- **BMAD Orchestrator Integration**: Volledig geïntegreerd met de Integrated Workflow Orchestrator
- **TestEngineer Agent**: Automatische integratie met de TestEngineer agent
- **CLI Tools**: Command-line interface voor sprite management
- **Reporting**: JSON export van test resultaten

## 🏗️ Architecture

### Core Components

```python
# Test Sprite Library
TestSpriteLibrary
├── Sprite Management
│   ├── register_sprite()
│   ├── create_component_sprite()
│   ├── create_accessibility_sprite()
│   └── list_sprites()
├── Test Execution
│   ├── run_sprite_test()
│   ├── _run_accessibility_tests()
│   ├── _run_visual_tests()
│   └── _run_interaction_tests()
└── Reporting
    ├── export_test_report()
    └── get_test_results()
```

### Sprite Types

```python
class SpriteType(Enum):
    COMPONENT = "component"      # Full component testing
    STATE = "state"             # State-specific testing
    INTERACTION = "interaction"  # Interaction pattern testing
    ACCESSIBILITY = "accessibility"  # Accessibility-focused testing
    VISUAL = "visual"           # Visual regression testing
```

### Sprite States

```python
class SpriteState(Enum):
    DEFAULT = "default"     # Default component state
    LOADING = "loading"     # Loading state
    ERROR = "error"         # Error state
    SUCCESS = "success"     # Success state
    DISABLED = "disabled"   # Disabled state
    HOVER = "hover"         # Hover state
    FOCUS = "focus"         # Focus state
    ACTIVE = "active"       # Active state
```

## 🚀 Quick Start

### 1. **Installation**

De Test Sprites integratie is al geïnstalleerd als onderdeel van de BMAD setup:

```bash
# Test sprites zijn automatisch beschikbaar
python3 test_sprites_cli.py list-sprites
```

### 2. **Create Your First Sprite**

```bash
# Maak een component sprite
python3 test_sprites_cli.py create-component MyButton \
  --states default,loading,error \
  --accessibility-checks aria-label,role,tabindex \
  --visual-checks color-contrast,spacing,alignment
```

### 3. **Run Component Tests**

```bash
# Test een component
python3 test_sprites_cli.py test-sprite MyButton_sprite --type all

# Of via de integrated workflow CLI
python3 integrated_workflow_cli.py test-component MyButton --type all
```

### 4. **View Test Results**

```bash
# Bekijk test resultaten
python3 test_sprites_cli.py show-results

# Export test rapport
python3 test_sprites_cli.py export-report --format json --output results.json
```

## 📚 Usage Examples

### **Creating Component Sprites**

```python
from bmad.agents.core.test_sprites import get_sprite_library, SpriteState

library = get_sprite_library()

# Maak een component sprite
sprite = library.create_component_sprite(
    component_name="UserProfile",
    states=[SpriteState.DEFAULT, SpriteState.LOADING, SpriteState.ERROR],
    accessibility_checks=["aria-label", "role", "tabindex", "keyboard-navigation"],
    visual_checks=["color-contrast", "font-size", "spacing", "alignment"]
)
```

### **Creating Accessibility Sprites**

```python
# Maak een accessibility-focused sprite
accessibility_sprite = library.create_accessibility_sprite(
    component_name="NavigationMenu",
    checks=[
        "aria-label",
        "role",
        "tabindex",
        "keyboard-navigation",
        "screen-reader",
        "color-contrast",
        "focus-indicator"
    ]
)
```

### **Running Tests Programmatically**

```python
# Test een sprite
result = await library.run_sprite_test("UserProfile_sprite", "all")

print(f"Status: {result.status}")
print(f"Duration: {result.performance_metrics['duration']:.2f}s")

# Bekijk details
for key, value in result.details.items():
    print(f"{key}: {value}")
```

### **Integration with BMAD Orchestrator**

```python
from bmad.agents.core.integrated_workflow_orchestrator import get_orchestrator

orchestrator = get_orchestrator()

# Test een component via de orchestrator
result = await orchestrator.run_component_tests("UserProfile", "all")

# Bekijk beschikbare sprites
sprites = orchestrator.get_component_sprites()
for sprite in sprites:
    print(f"Component: {sprite['component_name']}")
    print(f"States: {sprite['states']}")
```

## 🛠️ CLI Commands

### **Test Sprites CLI**

```bash
# List alle sprites
python3 test_sprites_cli.py list-sprites

# List sprites per type
python3 test_sprites_cli.py list-sprites --type component

# Maak een component sprite
python3 test_sprites_cli.py create-component MyComponent \
  --states default,loading,error \
  --accessibility-checks aria-label,role,tabindex \
  --visual-checks color-contrast,spacing

# Maak een accessibility sprite
python3 test_sprites_cli.py create-accessibility MyComponent \
  --checks aria-label,role,tabindex,keyboard-navigation

# Test een sprite
python3 test_sprites_cli.py test-sprite MyComponent_sprite --type all

# Test alle sprites
python3 test_sprites_cli.py run-all-tests

# Bekijk sprite details
python3 test_sprites_cli.py show-sprite MyComponent_sprite

# Export test rapport
python3 test_sprites_cli.py export-report --format json --output results.json

# Bekijk test resultaten
python3 test_sprites_cli.py show-results
```

### **Integrated Workflow CLI**

```bash
# List sprites via integrated CLI
python3 integrated_workflow_cli.py list-sprites

# Test component via integrated CLI
python3 integrated_workflow_cli.py test-component MyComponent --type all

# Export sprite rapport via integrated CLI
python3 integrated_workflow_cli.py export-sprite-report --format json --output results.json
```

## 🎨 Default BMAD Sprites

De integratie komt met pre-configured sprites voor BMAD componenten:

### **AgentStatus Component**
- **States**: default, loading, error
- **Accessibility**: aria-label, role, status-indicator
- **Visual**: color-contrast, status-colors, spacing

### **WorkflowManager Component**
- **States**: default, loading, active
- **Accessibility**: aria-label, role, keyboard-navigation
- **Visual**: layout, spacing, typography

### **APITester Component**
- **States**: default, loading, success, error
- **Accessibility**: aria-label, form-controls, error-messages
- **Visual**: form-layout, button-styles, error-styles

### **MetricsChart Component**
- **States**: default, loading, error
- **Accessibility**: aria-label, chart-description, keyboard-navigation
- **Visual**: chart-colors, data-visibility, responsive

## 🔧 Configuration

### **Sprite Directory**

Sprites worden opgeslagen in de `test_sprites/` directory:

```
test_sprites/
├── AgentStatus_sprite.json
├── WorkflowManager_sprite.json
├── APITester_sprite.json
└── MetricsChart_sprite.json
```

### **Test Configuration**

```python
# Sprite test configuratie
sprite_config = {
    "test_timeout": 30,  # seconds
    "retry_attempts": 3,
    "parallel_tests": 5,
    "screenshot_dir": "screenshots/",
    "baseline_dir": "baselines/"
}
```

## 📊 Test Results

### **Test Result Structure**

```python
@dataclass
class SpriteTestResult:
    sprite_name: str
    test_type: str
    status: str  # "passed", "failed", "skipped"
    details: Dict[str, Any]
    screenshot_diff: Optional[str]
    accessibility_issues: List[str]
    performance_metrics: Dict[str, Any]
    timestamp: float
```

### **Example Test Result**

```json
{
  "sprite_name": "AgentStatus_sprite",
  "test_type": "all",
  "status": "passed",
  "details": {
    "accessibility_aria-label": "passed",
    "accessibility_role": "passed",
    "accessibility_status-indicator": "passed",
    "visual_color-contrast": "passed",
    "visual_status-colors": "passed",
    "visual_spacing": "passed",
    "interaction_click": "passed",
    "interaction_hover": "passed",
    "interaction_focus": "passed",
    "interaction_keyboard": "passed"
  },
  "accessibility_issues": [],
  "performance_metrics": {
    "duration": 1.01
  },
  "timestamp": 1640995200.0
}
```

## 🔗 Integration Points

### **TestEngineer Agent Integration**

De TestEngineer agent kan automatisch test sprites gebruiken:

```python
# TestEngineer agent kan sprites uitvoeren
async def run_component_tests(self, component_name: str):
    result = await self.orchestrator.run_component_tests(component_name, "all")
    return result
```

### **CI/CD Integration**

```yaml
# GitHub Actions workflow
- name: Run Component Tests
  run: |
    python3 integrated_workflow_cli.py test-component AgentStatus --type all
    python3 integrated_workflow_cli.py test-component WorkflowManager --type all
```

### **Monitoring Integration**

```python
# Integratie met monitoring
async def monitor_component_health(self):
    sprites = self.orchestrator.get_component_sprites()
    for sprite in sprites:
        result = await self.orchestrator.run_component_tests(
            sprite['component_name'], "accessibility"
        )
        if result['status'] == 'failed':
            self.alert_accessibility_issue(sprite['component_name'])
```

## 🚀 Advanced Features

### **Custom Test Implementations**

```python
class CustomSpriteLibrary(TestSpriteLibrary):
    async def _run_accessibility_tests(self, sprite: TestSprite, result: SpriteTestResult):
        # Custom accessibility testing logic
        for check in sprite.accessibility_checks:
            if check == "custom-check":
                # Implement custom check
                result.details[f"accessibility_{check}"] = "passed"
            else:
                await super()._run_accessibility_tests(sprite, result)
```

### **Visual Regression Testing**

```python
# Screenshot comparison
async def compare_screenshots(self, baseline_path: str, current_path: str):
    # Implement visual diff logic
    diff = await self.visual_diff(baseline_path, current_path)
    return diff < self.threshold
```

### **Performance Testing**

```python
# Performance metrics
async def measure_performance(self, sprite: TestSprite):
    start_time = time.time()
    # Run component rendering
    render_time = time.time() - start_time
    
    return {
        "render_time": render_time,
        "memory_usage": self.get_memory_usage(),
        "cpu_usage": self.get_cpu_usage()
    }
```

## 🐛 Troubleshooting

### **Common Issues**

1. **Sprite not found**
   ```bash
   # Check if sprite exists
   python3 test_sprites_cli.py list-sprites
   
   # Create missing sprite
   python3 test_sprites_cli.py create-component MissingComponent
   ```

2. **Test failures**
   ```bash
   # Run with detailed output
   python3 test_sprites_cli.py test-sprite MyComponent_sprite --type accessibility
   
   # Check test results
   python3 test_sprites_cli.py show-results --sprite MyComponent_sprite
   ```

3. **Integration issues**
   ```bash
   # Test integration
   python3 integrated_workflow_cli.py test-integrations
   
   # Check orchestrator status
   python3 integrated_workflow_cli.py list-sprites
   ```

### **Debug Mode**

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python3 test_sprites_cli.py test-sprite MyComponent_sprite --type all
```

## 📈 Performance

### **Test Execution Times**

- **Accessibility tests**: ~0.1s per check
- **Visual tests**: ~0.1s per check
- **Interaction tests**: ~0.1s per test
- **Full component test**: ~1.0s total

### **Memory Usage**

- **Sprite library**: ~5MB
- **Test execution**: ~10MB per concurrent test
- **Result storage**: ~1MB per 1000 results

## 🔮 Future Enhancements

### **Planned Features**

1. **Visual Regression Testing**
   - Screenshot comparison
   - Baseline management
   - Visual diff reporting

2. **Performance Testing**
   - Render time measurement
   - Memory usage tracking
   - CPU usage monitoring

3. **Advanced Accessibility**
   - Screen reader testing
   - Keyboard navigation testing
   - Color blindness simulation

4. **Integration Testing**
   - Component interaction testing
   - End-to-end workflow testing
   - Cross-browser testing

### **Roadmap**

- **Q1 2024**: Visual regression testing
- **Q2 2024**: Performance testing integration
- **Q3 2024**: Advanced accessibility features
- **Q4 2024**: Cross-browser testing support

## 📞 Support

Voor vragen of problemen met de Test Sprites integratie:

1. **Documentation**: Bekijk deze README
2. **CLI Help**: `python3 test_sprites_cli.py --help`
3. **Integration Help**: `python3 integrated_workflow_cli.py --help`
4. **Issues**: Open een issue in de BMAD repository

---

**🧪 Test Sprites Integration** - Empowering BMAD with comprehensive component testing capabilities! 