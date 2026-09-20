# Telco Customer Churn — Retention & Revenue Risk Analysis

An interactive dashboard and analysis identifying why telecom customers churn, which segments carry the most revenue risk, and where a retention strategy would have the highest impact.

**[Live dashboard →]([https://telco-churn-analysis-six.vercel.app/])**

---

## Business question

Telecom companies lose customers constantly, but not all churn is equal. Before a business spends money on retention (discounts, outreach, offers), it needs to know: **which customers are leaving, why, and how much revenue is actually at stake.** This project answers that using a real 7,043-customer dataset.

## Data source

[IBM Telco Customer Churn dataset](https://www.kaggle.com/datasets/yeanzc/telco-customer-churn-ibm-dataset) — 7,043 customers, 50 fields covering contract terms, services, billing, satisfaction, and (for churned customers) the specific reason they left. All customers are based in California.

## Method

1. **Data quality check** — verified no duplicate customer records; confirmed that all nulls were structural, not missing data (e.g. `Churn Reason` is blank because a customer hasn't churned, not because the field wasn't captured).
2. **Segmentation** — grouped customers by contract type, internet service type, and payment method to see where churn concentrates.
3. **Revenue impact** — calculated total lifetime revenue tied to churned customers, and compared spend/tenure/satisfaction between churned and retained customers.
4. **Root cause** — used the dataset's `Churn Category` and `Churn Reason` fields to separate price-driven churn from competitive and service-quality churn.
5. **Dashboard** — built an interactive, cross-filterable dashboard so the findings below can be explored and re-cut by anyone reviewing the project, not just read as static numbers.

Full analysis code: [`analysis/churn_analysis.py`](analysis/churn_analysis.py)

## Key findings

**1. Contract length is the strongest churn driver in the dataset.**
Month-to-month customers churn at **45.8%**, one-year contract customers at **10.7%**, two-year at **2.5%** — an 18x gap between the extremes. This is a stronger signal than any service or demographic variable tested.

**2. Churned customers were high-value, not marginal.**
Customers who churned paid more per month on average (**$74.44 vs $61.27**) but stayed less than half as long (**18.0 vs 37.6 months**) and reported dramatically lower satisfaction (**1.74 vs 3.79 out of 5**). Total lifetime revenue tied to churned customers: **$3.68M**. This isn't low-value customers self-selecting out — it's a retention failure among customers worth keeping.

**3. Price is not the main reason customers leave.**
Only 78 of 1,869 churned customers cited price. The dominant reasons were competitor offers (841 customers) and dissatisfaction with service/support attitude (314 customers). A retention strategy built primarily around discounting would miss the majority of the actual problem.

## Recommendation

Prioritize retention efforts on **month-to-month customers in their first 12–18 months** — this is where churn risk is highest and where a modest incentive to move to a longer contract has the clearest ROI, given the 18x churn-rate gap between contract types. Separately, the "attitude of support/service" churn category (314 customers) points to a service-quality issue that a discount won't fix.

## Tools used

- **Python (pandas)** — data quality checks, segmentation, aggregation
- **HTML/CSS/JavaScript (Chart.js)** — interactive dashboard with cross-filtering and light/dark mode
- *(If rebuilt in Power BI: DAX measures for churn rate and revenue-at-risk, native cross-filtering, Power Query for the data quality steps)*

## Dashboard features

- KPI cards that recompute live based on all active filters
- Two charts (churn rate by contract, revenue at risk by contract) sharing one consistent color scheme
- A third, independent chart (churn rate by payment method) that combines with the contract filter rather than duplicating it — credit card customers churn at 14.5% vs. 36.9% for mailed check, a second real driver distinct from contract length
- Clicking a bar or legend item on any of the three charts cross-filters the KPIs, the other charts, and the detail table simultaneously
- Filter bar: internet type, payment method, promotional offer, churn status
- Full paginated customer-level detail table
- Light and dark mode

## Project structure

```
telco-churn-project/
├── README.md
├── data/
│   └── telco.csv                  # raw dataset
├── analysis/
│   └── churn_analysis.py          # reproducible analysis, run this first
└── dashboard/
    └── telco-churn-dashboard.html # interactive dashboard, open in any browser
```

## How to run

```bash
pip install pandas
cd analysis
python churn_analysis.py
```

Then open `dashboard/telco-churn-dashboard.html` in any browser — no server or build step required.

## Limitations

- All customers are based in California, so no genuine geographic comparison is possible.
- This is exploratory/descriptive analysis, not a predictive model — it identifies where churn concentrates, not which individual customers will churn next. A logical next step would be a classification model (e.g. logistic regression) trained on these features to score churn risk per customer.

---
*Built as a portfolio project. Not used in any production system.*
