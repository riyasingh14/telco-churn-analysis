# Analytical data model

The model uses a star schema. `fact_customer_churn` has one record per customer in the supplied quarterly snapshot; every dimension filters that fact table in one direction.

```mermaid
erDiagram
    DIM_GEOGRAPHY ||--o{ DIM_CUSTOMER : locates
    DIM_CUSTOMER ||--|| FACT_CUSTOMER_CHURN : describes
    DIM_CONTRACT ||--o{ FACT_CUSTOMER_CHURN : classifies
    DIM_PAYMENT ||--o{ FACT_CUSTOMER_CHURN : classifies
    DIM_OFFER ||--o{ FACT_CUSTOMER_CHURN : classifies
    DIM_CHURN_REASON ||--o{ FACT_CUSTOMER_CHURN : explains

    DIM_GEOGRAPHY {
      int geography_key PK
      text city
      text state
      text zip_code
    }
    DIM_CUSTOMER {
      text customer_id PK
      int geography_key FK
      int age
      boolean senior_citizen
    }
    DIM_CONTRACT {
      int contract_key PK
      text contract_type
    }
    DIM_PAYMENT {
      int payment_key PK
      text payment_method
      boolean paperless_billing
    }
    DIM_OFFER {
      int offer_key PK
      text offer_name
    }
    DIM_CHURN_REASON {
      int churn_reason_key PK
      text churn_category
      text churn_reason
    }
    FACT_CUSTOMER_CHURN {
      text customer_id PK, FK
      int contract_key FK
      int payment_key FK
      int offer_key FK
      int churn_reason_key FK
      boolean churned_flag
      numeric total_revenue
      int churn_score
      int cltv
    }
```

## Why this design

- It separates stable customer descriptors from measurable churn outcomes.
- It makes contract, payment, offer, and churn-reason filters reusable in Power BI.
- It makes the grain explicit, preventing accidental double-counting of customers.
- It can later accept additional quarterly snapshots by adding an extract-date dimension and a snapshot key to the fact table.
