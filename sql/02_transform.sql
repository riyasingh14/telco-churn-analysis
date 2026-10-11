-- Rebuild dimensions, fact table, and analyst-facing views from the raw extract.
-- The source is a single snapshot, so the fact table has one row per customer.

BEGIN;

TRUNCATE TABLE churn_analytics.fact_customer_churn,
               churn_analytics.dim_customer,
               churn_analytics.dim_geography,
               churn_analytics.dim_contract,
               churn_analytics.dim_payment,
               churn_analytics.dim_offer,
               churn_analytics.dim_churn_reason RESTART IDENTITY CASCADE;

INSERT INTO churn_analytics.dim_geography
    (country, state, city, zip_code, latitude, longitude, population)
SELECT DISTINCT country, state, city, zip_code, latitude, longitude, population
FROM churn_analytics.raw_telco_customer;

INSERT INTO churn_analytics.dim_customer
    (customer_id, geography_key, gender, age, under_30, senior_citizen, married,
     dependents, number_of_dependents, referred_a_friend, number_of_referrals)
SELECT r.customer_id, g.geography_key, r.gender, r.age,
       r.under_30 = 'Yes', r.senior_citizen = 'Yes', r.married = 'Yes',
       r.dependents = 'Yes', r.number_of_dependents, r.referred_a_friend = 'Yes',
       r.number_of_referrals
FROM churn_analytics.raw_telco_customer r
JOIN churn_analytics.dim_geography g
  ON (g.country, g.state, g.city, g.zip_code) = (r.country, r.state, r.city, r.zip_code);

INSERT INTO churn_analytics.dim_contract (contract_type)
SELECT DISTINCT contract FROM churn_analytics.raw_telco_customer;

INSERT INTO churn_analytics.dim_payment (payment_method, paperless_billing)
SELECT DISTINCT payment_method, paperless_billing = 'Yes'
FROM churn_analytics.raw_telco_customer;

INSERT INTO churn_analytics.dim_offer (offer_name)
SELECT DISTINCT COALESCE(NULLIF(offer, ''), 'No offer')
FROM churn_analytics.raw_telco_customer;

INSERT INTO churn_analytics.dim_churn_reason (churn_category, churn_reason)
SELECT DISTINCT COALESCE(NULLIF(churn_category, ''), 'Not churned'),
       COALESCE(NULLIF(churn_reason, ''), 'Not applicable')
FROM churn_analytics.raw_telco_customer;

INSERT INTO churn_analytics.fact_customer_churn
    (customer_id, contract_key, payment_key, offer_key, churn_reason_key, quarter,
     tenure_in_months, internet_service, internet_type, phone_service, multiple_lines,
     online_security, online_backup, device_protection_plan, premium_tech_support,
     streaming_tv, streaming_movies, streaming_music, unlimited_data,
     avg_monthly_gb_download, monthly_charge, total_charges, total_refunds,
     total_extra_data_charges, total_long_distance_charges, total_revenue,
     satisfaction_score, customer_status, churned_flag, churn_score, cltv)
SELECT r.customer_id, c.contract_key, p.payment_key, o.offer_key, cr.churn_reason_key,
       r.quarter, r.tenure_in_months, r.internet_service = 'Yes',
       COALESCE(NULLIF(r.internet_type, ''), 'No internet'), r.phone_service = 'Yes',
       r.multiple_lines = 'Yes', r.online_security = 'Yes', r.online_backup = 'Yes',
       r.device_protection_plan = 'Yes', r.premium_tech_support = 'Yes',
       r.streaming_tv = 'Yes', r.streaming_movies = 'Yes', r.streaming_music = 'Yes',
       r.unlimited_data = 'Yes', r.avg_monthly_gb_download, r.monthly_charge,
       r.total_charges, r.total_refunds, r.total_extra_data_charges,
       r.total_long_distance_charges, r.total_revenue, r.satisfaction_score,
       r.customer_status, r.churn_label = 'Yes', r.churn_score, r.cltv
FROM churn_analytics.raw_telco_customer r
JOIN churn_analytics.dim_contract c ON c.contract_type = r.contract
JOIN churn_analytics.dim_payment p
  ON (p.payment_method, p.paperless_billing) = (r.payment_method, r.paperless_billing = 'Yes')
JOIN churn_analytics.dim_offer o ON o.offer_name = COALESCE(NULLIF(r.offer, ''), 'No offer')
JOIN churn_analytics.dim_churn_reason cr
  ON (cr.churn_category, cr.churn_reason) = (
      COALESCE(NULLIF(r.churn_category, ''), 'Not churned'),
      COALESCE(NULLIF(r.churn_reason, ''), 'Not applicable')
  );

CREATE OR REPLACE VIEW churn_analytics.vw_churn_segment_performance AS
SELECT c.contract_type, p.payment_method, f.internet_type,
       COUNT(*) AS customers,
       COUNT(*) FILTER (WHERE f.churned_flag) AS churned_customers,
       ROUND(100.0 * COUNT(*) FILTER (WHERE f.churned_flag) / COUNT(*), 1) AS churn_rate_pct,
       ROUND(SUM(f.total_revenue) FILTER (WHERE f.churned_flag), 2) AS revenue_at_risk,
       ROUND(AVG(f.satisfaction_score) FILTER (WHERE f.churned_flag), 2) AS churned_customer_satisfaction
FROM churn_analytics.fact_customer_churn f
JOIN churn_analytics.dim_contract c USING (contract_key)
JOIN churn_analytics.dim_payment p USING (payment_key)
GROUP BY c.contract_type, p.payment_method, f.internet_type;

CREATE OR REPLACE VIEW churn_analytics.vw_executive_kpis AS
SELECT COUNT(*) AS customers,
       COUNT(*) FILTER (WHERE churned_flag) AS churned_customers,
       ROUND(100.0 * COUNT(*) FILTER (WHERE churned_flag) / COUNT(*), 1) AS churn_rate_pct,
       ROUND(SUM(total_revenue) FILTER (WHERE churned_flag), 2) AS revenue_at_risk,
       ROUND(AVG(satisfaction_score) FILTER (WHERE churned_flag), 2) AS churned_customer_satisfaction
FROM churn_analytics.fact_customer_churn;

COMMIT;
