# KPI definitions

| KPI | Definition | Calculation | Decision use |
|---|---|---|---|
| Customers | Unique customers in the selected segment | Count of fact rows | Denominator for segment comparisons |
| Churned Customers | Customers whose source `Churn Label` is `Yes` | Count where `churned_flag = true` | Size of the retention problem |
| Churn Rate % | Share of selected customers who churned | Churned Customers ÷ Customers | Compare risk across segments |
| Revenue at Risk | Total lifetime revenue from customers who churned | Sum of `total_revenue` where churned | Prioritise segments by potential value |
| Average Tenure | Average months as a customer | Average `tenure_in_months` | Identify early-life churn |
| Churned Customer Satisfaction | Average satisfaction among churned customers | Average `satisfaction_score` where churned | Diagnose service experience risk |
| High Risk Customers | Customers with source churn score at least 75 | Count where `churn_score >= 75` | Prioritisation list, not a validated prediction |

## Important interpretation note

This is a historical, California-only snapshot. `Churn Score` is supplied by the source dataset, so it should be presented as a source-provided prioritisation field—not as a model trained or validated in this project.
