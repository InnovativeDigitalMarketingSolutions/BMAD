# Explainability Examples

```python
import shap
explainer = shap.Explainer(model)
shap_values = explainer(X_test)
shap.summary_plot(shap_values, X_test)
```

- SHAP summary plot shows the most important features for prediction
- Use explainability in model selection and debugging