# AI Bias Check Template

## Bias Detection Checklist

### Data Bias
- [ ] **Dataset Balance**: Check for class imbalance in training data
- [ ] **Demographic Representation**: Ensure diverse demographic representation
- [ ] **Geographic Bias**: Check for geographic bias in data collection
- [ ] **Temporal Bias**: Verify data isn't biased towards specific time periods
- [ ] **Source Bias**: Ensure data sources are diverse and representative

### Model Bias
- [ ] **Feature Bias**: Check for biased features in the model
- [ ] **Algorithm Bias**: Verify algorithm choice doesn't introduce bias
- [ ] **Training Bias**: Ensure training process doesn't amplify existing biases
- [ ] **Evaluation Bias**: Check evaluation metrics for bias

### Fairness Metrics
- [ ] **Demographic Parity**: Equal positive prediction rates across groups
- [ ] **Equal Opportunity**: Equal true positive rates across groups
- [ ] **Equalized Odds**: Equal true positive and false positive rates
- [ ] **Individual Fairness**: Similar individuals receive similar predictions

### Bias Mitigation Strategies
- [ ] **Pre-processing**: Clean biased data before training
- [ ] **In-processing**: Use fairness-aware algorithms
- [ ] **Post-processing**: Adjust predictions for fairness
- [ ] **Regular Auditing**: Regular bias checks and monitoring

## Implementation Example

```python
import pandas as pd
from sklearn.metrics import classification_report
from fairlearn.metrics import demographic_parity_difference

def check_bias(model, X_test, y_test, sensitive_features):
    # Predictions
    y_pred = model.predict(X_test)
    
    # Overall performance
    print("Overall Performance:")
    print(classification_report(y_test, y_pred))
    
    # Demographic parity
    dp_diff = demographic_parity_difference(
        y_true=y_test,
        y_pred=y_pred,
        sensitive_features=sensitive_features
    )
    
    print(f"Demographic Parity Difference: {dp_diff:.4f}")
    
    # Group-wise analysis
    for group in sensitive_features.unique():
        mask = sensitive_features == group
        group_acc = (y_test[mask] == y_pred[mask]).mean()
        print(f"Accuracy for group {group}: {group_acc:.4f}")
```

## Bias Detection Tools
- **Fairlearn**: Microsoft's fairness toolkit
- **AIF360**: IBM's AI Fairness 360
- **SHAP**: Explainable AI for bias detection
- **LIME**: Local interpretable model explanations

## Reporting Template

### Bias Analysis Report
- **Model**: [Model Name]
- **Dataset**: [Dataset Name]
- **Analysis Date**: [Date]
- **Overall Bias Score**: [Score]
- **Critical Issues**: [List of issues]
- **Recommendations**: [Mitigation strategies]
- **Next Steps**: [Action items] 