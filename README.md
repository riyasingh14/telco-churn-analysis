# Telco Customer Churn — Retention & Revenue Risk Analysis

An interactive dashboard and analysis identifying why telecom customers churn, which segments carry the most revenue risk, and where a retention strategy would have the highest impact.

**[Live dashboard →](https://telco-churn-analysis-six.vercel.app/)**

## Portfolio extension: SQL + Power BI

This repository now includes a compact end-to-end analytics layer alongside the Python analysis and static dashboard:

- **PostgreSQL star schema** with a customer-level churn fact table and reusable contract, payment, offer, geography, and churn-reason dimensions.
- **Repeatable SQL transformations** that load the supplied CSV and create analyst-facing KPI and segment-performance views.
- **Power BI build pack** with the data model, ready-to-create DAX measures, and a three-page dashboard specification.
- **Business definitions** for every KPI, including scope and interpretation caveats.

See the [data model](docs/data-model.md), [KPI definitions](docs/kpi-definitions.md), and [Power BI build guide](powerbi/README.md).

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
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python analysis/churn_analysis.py
```

Then open `dashboard/telco-churn-dashboard.html` in any browser — no server or build step required.

### SQL analytics layer

The SQL workflow is designed to be fast to reproduce locally with Docker Desktop and PostgreSQL 16:

```bash
docker compose up -d --wait
docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U analyst -d telco_churn -f /workspace/sql/00_schema.sql
docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U analyst -d telco_churn -f /workspace/sql/01_load_raw.sql
docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U analyst -d telco_churn -f /workspace/sql/02_transform.sql
```

The resulting PostgreSQL schema is `churn_analytics`. The two most useful views for ad hoc analysis are:

- `churn_analytics.vw_executive_kpis`
- `churn_analytics.vw_churn_segment_performance`

For the Power BI build steps, relationships, DAX measures, and report layout, follow [powerbi/README.md](powerbi/README.md).

### Retention opportunity model

The project also includes an explainable logistic-regression model that scores active customers, weights their risk by source CLTV, and exports a ranked intervention list:

```bash
.venv/bin/python analysis/retention_opportunity.py
```

It creates reproducible output files in `outputs/`, including model metrics, top drivers, customer-level expected revenue at risk, and a segment/action summary. See [the retention model notes](docs/retention-opportunity-model.md) for the methodology and limitations.

### Decision brief and responsible use

The live dashboard starts with a decision brief for the highest-priority segment, including low/base/high retention scenarios and explicit assumptions. A concise EU/GDPR note is included in the dashboard and expanded in [privacy-and-ethics.md](docs/privacy-and-ethics.md). The project is a public-data portfolio demonstration, not a production profiling or automated decision system.

## Business questions answered

1. Which customer segments have the highest churn rate?
2. Where is the greatest lifetime revenue at risk?
3. Which churn reasons indicate a pricing issue versus a service or competitor issue?
4. Which customer attributes should a retention team use to prioritise investigation?
5. Which active customers represent the highest estimated revenue at risk, and what should the retention team try first?

## Limitations

- All customers are based in California, so no genuine geographic comparison is possible.
- This is exploratory/descriptive analysis, not a predictive model — it identifies where churn concentrates, not which individual customers will churn next. A logical next step would be a classification model (e.g. logistic regression) trained on these features to score churn risk per customer.

---
*Built as a portfolio project. Not used in any production system.*
