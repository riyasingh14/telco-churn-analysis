"""Build an explainable retention opportunity list from the Telco churn extract.

Run from the repository root:
    .venv/bin/python analysis/retention_opportunity.py

The model learns from customers with known historical outcomes (Stayed or Churned),
then ranks active customers (Stayed or Joined). It intentionally excludes outcome
and post-churn fields, including Churn Score, Churn Category, and Churn Reason.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "telco.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Fields available before an observed churn outcome. CLTV is deliberately excluded
# from this list; it is used after scoring to prioritise revenue at risk.
NUMERIC_FEATURES = [
    "Age",
    "Number of Dependents",
    "Number of Referrals",
    "Tenure in Months",
    "Avg Monthly Long Distance Charges",
    "Avg Monthly GB Download",
    "Monthly Charge",
    "Total Charges",
    "Total Refunds",
    "Total Extra Data Charges",
    "Total Long Distance Charges",
    "Satisfaction Score",
]
CATEGORICAL_FEATURES = [
    "Gender",
    "Under 30",
    "Senior Citizen",
    "Married",
    "Dependents",
    "Referred a Friend",
    "Offer",
    "Phone Service",
    "Multiple Lines",
    "Internet Service",
    "Internet Type",
    "Online Security",
    "Online Backup",
    "Device Protection Plan",
    "Premium Tech Support",
    "Streaming TV",
    "Streaming Movies",
    "Streaming Music",
    "Unlimited Data",
    "Contract",
    "Paperless Billing",
    "Payment Method",
]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def intervention_recommendation(row: pd.Series) -> tuple[str, str]:
    """Return an explainable segment label and recommended first action."""
    if row["Churn Probability"] >= 0.50 and row["Contract"] == "Month-to-Month":
        return (
            "High risk · month-to-month",
            "Offer a one-year contract migration with a targeted retention incentive.",
        )
    if row["Satisfaction Score"] <= 2 and row["Premium Tech Support"] == "No":
        return (
            "Service recovery opportunity",
            "Assign a proactive support callback before making a discount offer.",
        )
    if row["Payment Method"] == "Mailed Check":
        return (
            "Payment-friction opportunity",
            "Invite the customer to paperless billing and AutoPay with a clear value message.",
        )
    if row["Monthly Charge"] >= 75:
        return (
            "High-value price sensitivity",
            "Complete a plan and service-value review; avoid blanket discounting.",
        )
    return (
        "Monitor and nurture",
        "Use a personalised check-in and reassess risk at the next reporting cycle.",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(DATA_PATH)

    historical = df[df["Customer Status"].isin(["Stayed", "Churned"])].copy()
    active = df[df["Customer Status"].isin(["Stayed", "Joined"])].copy()
    y = (historical["Churn Label"] == "Yes").astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        historical[FEATURES], y, test_size=0.25, random_state=42, stratify=y
    )
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("one_hot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                CATEGORICAL_FEATURES,
            ),
        ]
    )
    model = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )
    model.fit(X_train, y_train)

    test_probability = model.predict_proba(X_test)[:, 1]
    metrics = {
        "training_customers": int(len(X_train)),
        "test_customers": int(len(X_test)),
        "test_churn_rate": round(float(y_test.mean()), 4),
        "roc_auc": round(float(roc_auc_score(y_test, test_probability)), 4),
        "average_precision": round(float(average_precision_score(y_test, test_probability)), 4),
        "model": "Logistic regression with scaled numeric and one-hot categorical features",
        "excluded_leakage_fields": [
            "Customer Status",
            "Churn Label",
            "Churn Score",
            "Churn Category",
            "Churn Reason",
            "CLTV (used only for prioritisation)",
        ],
    }
    (OUTPUT_DIR / "retention_model_metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )

    feature_names = model.named_steps["preprocessor"].get_feature_names_out()
    coefficients = model.named_steps["classifier"].coef_[0]
    drivers = pd.DataFrame(
        {"feature": feature_names, "coefficient": coefficients}
    )
    drivers["effect"] = drivers["coefficient"].map(
        lambda value: "Higher churn propensity" if value > 0 else "Lower churn propensity"
    )
    drivers["absolute_coefficient"] = drivers["coefficient"].abs()
    drivers = drivers.sort_values("absolute_coefficient", ascending=False)
    drivers[["feature", "coefficient", "effect"]].head(20).to_csv(
        OUTPUT_DIR / "retention_model_top_drivers.csv", index=False
    )

    opportunity = active[
        [
            "Customer ID",
            "Customer Status",
            "City",
            "Contract",
            "Payment Method",
            "Tenure in Months",
            "Monthly Charge",
            "Satisfaction Score",
            "Premium Tech Support",
            "CLTV",
        ]
    ].copy()
    opportunity["Churn Probability"] = model.predict_proba(active[FEATURES])[:, 1]
    opportunity["Expected Revenue at Risk"] = opportunity["Churn Probability"] * opportunity["CLTV"]
    opportunity[["Priority Segment", "Recommended Action"]] = opportunity.apply(
        intervention_recommendation, axis=1, result_type="expand"
    )
    opportunity["Priority Rank"] = (
        opportunity["Expected Revenue at Risk"].rank(method="first", ascending=False).astype(int)
    )
    opportunity = opportunity.sort_values("Priority Rank")
    opportunity["Churn Probability"] = opportunity["Churn Probability"].round(4)
    opportunity["Expected Revenue at Risk"] = opportunity["Expected Revenue at Risk"].round(2)
    opportunity.to_csv(OUTPUT_DIR / "retention_intervention_list.csv", index=False)

    action_summary = (
        opportunity.groupby(["Priority Segment", "Recommended Action"], as_index=False)
        .agg(
            customers=("Customer ID", "count"),
            expected_revenue_at_risk=("Expected Revenue at Risk", "sum"),
        )
        .sort_values("expected_revenue_at_risk", ascending=False)
    )
    action_summary["expected_revenue_at_risk"] = action_summary[
        "expected_revenue_at_risk"
    ].round(2)
    action_summary.to_csv(OUTPUT_DIR / "retention_action_summary.csv", index=False)

    priority_segment = opportunity[
        opportunity["Priority Segment"] == "High risk · month-to-month"
    ].copy()
    scenarios = []
    for name, retention_rate in (("Low", 0.05), ("Base", 0.10), ("High", 0.15)):
        scenarios.append(
            {
                "scenario": name,
                "incremental_retention_rate": retention_rate,
                "estimated_customers_retained": round(len(priority_segment) * retention_rate, 1),
                "estimated_revenue_protected": round(
                    priority_segment["Expected Revenue at Risk"].sum() * retention_rate, 2
                ),
            }
        )
    decision_summary = {
        "priority_segment": "High risk · month-to-month",
        "recommended_action": "Offer a one-year contract migration with a targeted retention incentive.",
        "target_customers": int(len(priority_segment)),
        "average_churn_probability": round(float(priority_segment["Churn Probability"].mean()), 4),
        "expected_revenue_at_risk": round(
            float(priority_segment["Expected Revenue at Risk"].sum()), 2
        ),
        "scenarios": scenarios,
        "assumption": "Scenario rates are illustrative incremental retention uplift among the target segment; protected revenue equals expected revenue at risk multiplied by the uplift.",
    }
    (OUTPUT_DIR / "retention_decision_summary.json").write_text(
        json.dumps(decision_summary, indent=2) + "\n", encoding="utf-8"
    )

    print("Retention opportunity model completed")
    print(f"Test ROC AUC: {metrics['roc_auc']:.3f}")
    print(f"Test average precision: {metrics['average_precision']:.3f}")
    print(f"Active customers scored: {len(opportunity):,}")
    print("\nTop model drivers:")
    print(drivers[["feature", "coefficient", "effect"]].head(5).to_string(index=False))
    print("\nTop recommended action segments by expected revenue at risk:")
    print(action_summary.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
