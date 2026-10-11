-- Run from psql at the repository root. This replaces the raw landing table
-- with the version in data/telco.csv and leaves the analytical model untouched.

TRUNCATE TABLE churn_analytics.raw_telco_customer;

\copy churn_analytics.raw_telco_customer FROM 'data/telco.csv' WITH (FORMAT csv, HEADER true)
