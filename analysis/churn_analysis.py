"""
Telco Customer Churn — Exploratory Analysis
Dataset: IBM Telco Customer Churn (7,043 customers, California)
Source: https://www.kaggle.com/datasets/yeanzc/telco-customer-churn-ibm-dataset

Run:
    pip install pandas
    python churn_analysis.py

This script reproduces the headline findings used in the dashboard and
README. It is meant to be read, not just run — the point of a portfolio
project is being able to explain every line of this in an interview.
"""

import pandas as pd


def load_data(path: str = "../data/telco.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def data_quality_summary(df: pd.DataFrame) -> None:
    print("=" * 60)
    print("DATA QUALITY CHECK")
    print("=" * 60)
    print(f"Rows: {len(df):,} | Columns: {df.shape[1]}")
    print(f"Duplicate Customer IDs: {df['Customer ID'].duplicated().sum()}")

    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    print("\nColumns with nulls (and why they're expected):")
    print("  Offer            -> customer was not on a promotional offer")
    print("  Internet Type    -> customer has no internet service")
    print("  Churn Category   -> customer has not churned")
    print("  Churn Reason     -> customer has not churned")
    print(nulls)


def churn_overview(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("OVERALL CHURN RATE")
    print("=" * 60)
    churn_rate = (df["Churn Label"] == "Yes").mean() * 100
    print(f"Overall churn rate: {churn_rate:.1f}%")
    print(df["Customer Status"].value_counts())


def churn_by_contract(df: pd.DataFrame) -> pd.Series:
    print("\n" + "=" * 60)
    print("FINDING 1 — CHURN RATE BY CONTRACT TYPE")
    print("=" * 60)
    result = (
        df.groupby("Contract")["Churn Label"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .sort_values(ascending=False)
        .round(1)
    )
    print(result)
    spread = result.max() / result.min()
    print(f"\nMonth-to-Month customers churn at {spread:.1f}x the rate of Two Year customers.")
    return result


def revenue_at_risk(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("FINDING 2 — REVENUE AT RISK")
    print("=" * 60)
    churned = df[df["Churn Label"] == "Yes"]
    total_at_risk = churned["Total Revenue"].sum()
    print(f"Total lifetime revenue tied to churned customers: ${total_at_risk:,.0f}")

    comparison = df.groupby("Churn Label")[
        ["Monthly Charge", "Tenure in Months", "Satisfaction Score"]
    ].mean().round(2)
    print("\nChurned vs retained customers, side by side:")
    print(comparison)
    print(
        "\nChurned customers pay MORE per month on average but stay HALF as long "
        "and report far lower satisfaction — this isn't a low-value segment leaving,"
        " it's a high-value segment leaving unhappy."
    )


def churn_reasons(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("FINDING 3 — WHY CUSTOMERS ACTUALLY LEAVE")
    print("=" * 60)
    print(df["Churn Category"].value_counts())
    print("\nTop specific reasons:")
    print(df["Churn Reason"].value_counts().head(8))
    price_related = df["Churn Reason"].fillna("").str.contains("Price", case=False).sum()
    total_churned = (df["Churn Label"] == "Yes").sum()
    print(
        f"\nOnly {price_related} of {total_churned} churned customers cited price. "
        "The majority left over competitor offers or service/support attitude — "
        "a retention strategy built only around discounting would miss most of the problem."
    )


def payment_method_risk(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("SUPPORTING CUT — CHURN RATE BY PAYMENT METHOD")
    print("=" * 60)
    result = (
        df.groupby("Payment Method")["Churn Label"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .sort_values(ascending=False)
        .round(1)
    )
    print(result)


if __name__ == "__main__":
    df = load_data()
    data_quality_summary(df)
    churn_overview(df)
    churn_by_contract(df)
    revenue_at_risk(df)
    churn_reasons(df)
    payment_method_risk(df)
