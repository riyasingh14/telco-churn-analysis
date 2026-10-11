-- PostgreSQL analytical model for the Telco Customer Churn portfolio project.
-- Grain of fact_customer_churn: one customer in the supplied quarterly extract.

CREATE SCHEMA IF NOT EXISTS churn_analytics;

CREATE TABLE IF NOT EXISTS churn_analytics.raw_telco_customer (
    customer_id TEXT PRIMARY KEY,
    gender TEXT, age INTEGER, under_30 TEXT, senior_citizen TEXT,
    married TEXT, dependents TEXT, number_of_dependents INTEGER,
    country TEXT, state TEXT, city TEXT, zip_code TEXT,
    latitude NUMERIC, longitude NUMERIC, population INTEGER, quarter TEXT,
    referred_a_friend TEXT, number_of_referrals INTEGER, tenure_in_months INTEGER,
    offer TEXT, phone_service TEXT, avg_monthly_long_distance_charges NUMERIC,
    multiple_lines TEXT, internet_service TEXT, internet_type TEXT,
    avg_monthly_gb_download INTEGER, online_security TEXT, online_backup TEXT,
    device_protection_plan TEXT, premium_tech_support TEXT, streaming_tv TEXT,
    streaming_movies TEXT, streaming_music TEXT, unlimited_data TEXT,
    contract TEXT, paperless_billing TEXT, payment_method TEXT,
    monthly_charge NUMERIC, total_charges NUMERIC, total_refunds NUMERIC,
    total_extra_data_charges NUMERIC, total_long_distance_charges NUMERIC,
    total_revenue NUMERIC, satisfaction_score INTEGER, customer_status TEXT,
    churn_label TEXT, churn_score INTEGER, cltv INTEGER, churn_category TEXT,
    churn_reason TEXT
);

CREATE TABLE IF NOT EXISTS churn_analytics.dim_geography (
    geography_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country TEXT NOT NULL, state TEXT NOT NULL, city TEXT NOT NULL,
    zip_code TEXT NOT NULL, latitude NUMERIC, longitude NUMERIC, population INTEGER,
    UNIQUE (country, state, city, zip_code)
);

CREATE TABLE IF NOT EXISTS churn_analytics.dim_customer (
    customer_id TEXT PRIMARY KEY,
    geography_key INTEGER NOT NULL REFERENCES churn_analytics.dim_geography,
    gender TEXT, age INTEGER, under_30 BOOLEAN, senior_citizen BOOLEAN,
    married BOOLEAN, dependents BOOLEAN, number_of_dependents INTEGER,
    referred_a_friend BOOLEAN, number_of_referrals INTEGER
);

CREATE TABLE IF NOT EXISTS churn_analytics.dim_contract (
    contract_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    contract_type TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS churn_analytics.dim_payment (
    payment_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    payment_method TEXT NOT NULL, paperless_billing BOOLEAN NOT NULL,
    UNIQUE (payment_method, paperless_billing)
);

CREATE TABLE IF NOT EXISTS churn_analytics.dim_offer (
    offer_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    offer_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS churn_analytics.dim_churn_reason (
    churn_reason_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    churn_category TEXT NOT NULL, churn_reason TEXT NOT NULL,
    UNIQUE (churn_category, churn_reason)
);

CREATE TABLE IF NOT EXISTS churn_analytics.fact_customer_churn (
    customer_id TEXT PRIMARY KEY REFERENCES churn_analytics.dim_customer,
    contract_key INTEGER NOT NULL REFERENCES churn_analytics.dim_contract,
    payment_key INTEGER NOT NULL REFERENCES churn_analytics.dim_payment,
    offer_key INTEGER NOT NULL REFERENCES churn_analytics.dim_offer,
    churn_reason_key INTEGER NOT NULL REFERENCES churn_analytics.dim_churn_reason,
    quarter TEXT NOT NULL, tenure_in_months INTEGER NOT NULL,
    internet_service BOOLEAN NOT NULL, internet_type TEXT NOT NULL,
    phone_service BOOLEAN NOT NULL, multiple_lines BOOLEAN NOT NULL,
    online_security BOOLEAN NOT NULL, online_backup BOOLEAN NOT NULL,
    device_protection_plan BOOLEAN NOT NULL, premium_tech_support BOOLEAN NOT NULL,
    streaming_tv BOOLEAN NOT NULL, streaming_movies BOOLEAN NOT NULL,
    streaming_music BOOLEAN NOT NULL, unlimited_data BOOLEAN NOT NULL,
    avg_monthly_gb_download INTEGER NOT NULL,
    monthly_charge NUMERIC NOT NULL, total_charges NUMERIC NOT NULL,
    total_refunds NUMERIC NOT NULL, total_extra_data_charges NUMERIC NOT NULL,
    total_long_distance_charges NUMERIC NOT NULL, total_revenue NUMERIC NOT NULL,
    satisfaction_score INTEGER NOT NULL, customer_status TEXT NOT NULL,
    churned_flag BOOLEAN NOT NULL, churn_score INTEGER NOT NULL, cltv INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_fact_churned_flag ON churn_analytics.fact_customer_churn (churned_flag);
CREATE INDEX IF NOT EXISTS ix_fact_contract_key ON churn_analytics.fact_customer_churn (contract_key);
CREATE INDEX IF NOT EXISTS ix_fact_payment_key ON churn_analytics.fact_customer_churn (payment_key);
