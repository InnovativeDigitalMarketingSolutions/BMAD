# AI Explainability Template

## Explainability Methods

### Model-Agnostic Methods
- **SHAP (SHapley Additive exPlanations)**: Game theory-based feature importance
- **LIME (Local Interpretable Model-agnostic Explanations)**: Local linear approximations
- **Permutation Importance**: Feature importance by permutation
- **Partial Dependence Plots**: Show feature effects on predictions

### Model-Specific Methods
- **Decision Trees**: Naturally interpretable
- **Linear Models**: Coefficient interpretation
- **Neural Networks**: Attention mechanisms, saliency maps
- **Gradient-based**: Grad-CAM, Integrated Gradients

## Implementation Examples

### SHAP Implementation
```python
import shap
import numpy as np

def explain_with_shap(model, X_test, feature_names=None):
    # Create explainer
    explainer = shap.Explainer(model, X_test)
    
    # Calculate SHAP values
    shap_values = explainer(X_test)
    
    # Summary plot
    shap.summary_plot(shap_values, X_test, feature_names=feature_names)
    
    # Force plot for specific instance
    shap.force_plot(explainer.expected_value, shap_values[0], X_test[0])
    
    # Dependence plot
    shap.dependence_plot("feature_name", shap_values, X_test)
    
    return shap_values
```

### LIME Implementation
```python
from lime.lime_tabular import LimeTabularExplainer

def explain_with_lime(model, X_test, feature_names, class_names):
    # Create explainer
    explainer = LimeTabularExplainer(
        X_test,
        feature_names=feature_names,
        class_names=class_names,
        mode='classification'
    )
    
    # Explain specific instance
    exp = explainer.explain_instance(
        X_test[0], 
        model.predict_proba,
        num_features=10
    )
    
    # Show explanation
    exp.show_in_notebook()
    
    return exp
```

### Feature Importance Analysis
```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_feature_importance(model, feature_names):
    # Get feature importance
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importance = np.abs(model.coef_[0])
    else:
        return
    
    # Create DataFrame
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    # Plot
    plt.figure(figsize=(10, 6))
    sns.barplot(data=feature_importance.head(20), x='importance', y='feature')
    plt.title('Feature Importance')
    plt.tight_layout()
    plt.show()
```

## Explainability Metrics

### Interpretability Metrics
- **Completeness**: How much of the model behavior is explained
- **Stability**: Consistency of explanations across similar inputs
- **Accuracy**: How well explanations match model behavior
- **Simplicity**: Complexity of explanations

### Evaluation Framework
```python
def evaluate_explanations(model, explainer, X_test, y_test):
    # Generate explanations
    explanations = []
    for i in range(len(X_test)):
        exp = explainer.explain_instance(X_test[i], model.predict_proba)
        explanations.append(exp)
    
    # Evaluate completeness
    completeness = calculate_completeness(explanations)
    
    # Evaluate stability
    stability = calculate_stability(explanations, X_test)
    
    # Evaluate accuracy
    accuracy = calculate_explanation_accuracy(model, explanations, X_test)
    
    return {
        'completeness': completeness,
        'stability': stability,
        'accuracy': accuracy
    }
```

## Reporting Template

### Explainability Report
- **Model**: [Model Name]
- **Dataset**: [Dataset Name]
- **Analysis Date**: [Date]
- **Explainability Method**: [Method Used]
- **Key Features**: [Top important features]
- **Explanation Quality**: [Metrics scores]
- **Insights**: [Key findings]
- **Recommendations**: [Action items]

## Best Practices

### Do's
- Use multiple explainability methods
- Validate explanations with domain experts
- Document explanation methodology
- Monitor explanation quality over time
- Consider ethical implications

### Don'ts
- Rely on single explanation method
- Ignore model complexity
- Over-interpret local explanations
- Use explanations as truth
- Ignore computational costs

## Tools and Libraries
- **SHAP**: shap.readthedocs.io
- **LIME**: github.com/marcotcr/lime
- **InterpretML**: interpret.ml
- **Alibi**: github.com/SeldonIO/alibi
- **Captum**: pytorch.org/captum 