# Retention opportunity model

## Business decision

The aim is not simply to describe who churned. The model ranks **currently active customers** by the estimated value at risk, helping a retention team decide where to investigate or intervene first.

## Method

1. Train a logistic-regression churn model on historical customers with known outcomes: `Stayed` and `Churned`.
2. Hold out 25% of those customers for an honest, stratified test.
3. Exclude outcome and post-churn fields: customer status, churn label, source churn score, churn category, and churn reason.
4. Score active customers (`Stayed` and `Joined`) using predicted churn probability.
5. Calculate **Expected Revenue at Risk = Churn Probability × source CLTV**.
6. Rank customers and assign a recommended first action using transparent business rules.

## Outputs

Running `python analysis/retention_opportunity.py` creates:

- `outputs/retention_model_metrics.json` — holdout performance and assumptions.
- `outputs/retention_model_top_drivers.csv` — the 20 strongest logistic-regression drivers.
- `outputs/retention_intervention_list.csv` — ranked active-customer action list.
- `outputs/retention_action_summary.csv` — summary of recommended actions by expected revenue at risk.
- `outputs/retention_decision_summary.json` — the priority segment and low/base/high retention scenarios used by the dashboard decision brief.

## Important limitations

- This is a portfolio model trained on one historical California snapshot; it is not a production churn model.
- The very high holdout score may reflect the source dataset's structure. It should be treated as a validation result to investigate, not evidence that the same performance will transfer to a new telecom customer base.
- CLTV and churn score are supplied by the dataset. CLTV is used only as a value-weighting input; the source churn score is not used by the model.
- A score identifies prioritisation opportunities, not a causal reason to offer a discount. Recommended actions should be evaluated through controlled experiments before rollout.
