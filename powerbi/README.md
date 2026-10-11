# Power BI dashboard build guide

This folder gives you the model and measures to create a polished Power BI file in roughly 30–45 minutes. The `.pbix` itself is not stored in Git because it is a binary working file; save your finished report as `powerbi/Telco_Churn_Analytics.pbix` locally.

## 1. Start the local database

From the repository root:

```bash
docker compose up -d --wait
docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U analyst -d telco_churn -f /workspace/sql/00_schema.sql
docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U analyst -d telco_churn -f /workspace/sql/01_load_raw.sql
docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U analyst -d telco_churn -f /workspace/sql/02_transform.sql
```

The database is intentionally local-only and uses development credentials. Do not use these credentials outside this portfolio project.

## 2. Connect Power BI Desktop

1. Select **Get data → PostgreSQL database**.
2. Server: `localhost:5432`; Database: `telco_churn`.
3. Use **Database** credentials: user `analyst`, password `telco_dev`.
4. Import these tables from the `churn_analytics` schema:
   - `fact_customer_churn`
   - `dim_customer`
   - `dim_geography`
   - `dim_contract`
   - `dim_payment`
   - `dim_offer`
   - `dim_churn_reason`
5. To add the retention-prioritisation page, first run `python analysis/retention_opportunity.py` and import `outputs/retention_intervention_list.csv` as a CSV. Relate `Retention Intervention List[Customer ID]` to `dim_customer[customer_id]`.
6. In Model view, create the relationships shown in [the data model](../docs/data-model.md). Use single-direction filtering from dimensions to fact.
7. Create the measures in [measure_definitions.dax](measure_definitions.dax), then save the file as `Telco_Churn_Analytics.pbix`.

## 3. Build three report pages

### Executive overview

- Cards: `Customers`, `Churned Customers`, `Churn Rate %`, `Revenue at Risk`.
- Clustered column chart: `Churn Rate %` by `dim_contract[contract_type]`.
- Bar chart: `Revenue at Risk` by `dim_churn_reason[churn_category]`.
- Slicers: contract type, payment method, internet type, offer name.
- Narrative card: recommendation to prioritise month-to-month customers.

### Churn drivers

- Matrix: contract type × payment method with `Customers`, `Churn Rate %`, and `Revenue at Risk`.
- Bar chart: `Churn Rate %` by payment method.
- Scatter chart: `Average Monthly Charge` vs `Average Tenure (Months)`; legend = churn status.
- Decomposition tree: `Revenue at Risk` by contract type, internet type, churn category.

### Customer action list

- Table: customer ID, city, contract type, tenure, churn score, CLTV, monthly charge, churn category.
- Sort by `Churn Score` descending, then `CLTV` descending.
- Apply a page filter of `fact_customer_churn[churned_flag] = TRUE` only if presenting actual churned-customer root causes; otherwise leave unfiltered for prospective prioritisation.

### Retention opportunity

- Cards: sum of `Expected Revenue at Risk`, average `Churn Probability`, and count of `Customer ID` from `Retention Intervention List`.
- Bar chart: expected revenue at risk by `Priority Segment`.
- Table: priority rank, customer ID, contract, churn probability, CLTV, expected revenue at risk, and recommended action.
- Use this wording in the subtitle: “Prioritisation aid from a historical portfolio model; validate interventions with an experiment.”

## Presentation standard

Use a single currency format, show percentages to one decimal place, label the extract as a California-based snapshot, and include the limitations from the root README on the final page.
