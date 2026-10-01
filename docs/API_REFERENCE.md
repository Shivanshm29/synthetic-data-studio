# 📖 Synthetic Data Studio - API Reference

Base URL: `http://localhost:8000`

Interactive documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

---

## 1. Health Checks

### `GET /health`
Returns service uptime status.

**Response `200 OK`**:
```json
{
  "status": "healthy"
}
```

---

## 2. Dataset Discovery (DataScout)

### `POST /datascout/analyze`
Analyzes a user prompt, determines optimal dataset strategy, and searches Hugging Face and Kaggle for matches.

**Request Body**:
```json
{
  "prompt": "Customer churn and transactions dataset for banking"
}
```

**Response `200 OK`**:
```json
{
  "strategy": "Existing Dataset",
  "confidence": 0.95,
  "domain": "Finance",
  "industry": "General",
  "use_case": "Dataset Discovery",
  "existing_datasets": [
    {
      "name": "Bank Customer Churn Dataset",
      "description": "Historical banking customer demographics and churn labels.",
      "estimated_rows": 10000,
      "estimated_columns": 14,
      "license": "CC0: Public Domain",
      "format": "CSV",
      "download_source": "https://www.kaggle.com/datasets/...",
      "quality_score": 0.95,
      "similarity_score": 0.92,
      "source_platform": "kaggle",
      "dataset_id": "shrutimechlearn/churn-modelling"
    }
  ],
  "reasoning": "Found 3 verified public datasets on HuggingFace & Kaggle matching 'customer churn'."
}
```

---

### `POST /datascout/fetch`
Retrieves live sample rows from an existing public repository.

**Request Body**:
```json
{
  "source_platform": "kaggle",
  "dataset_id": "shrutimechlearn/churn-modelling",
  "limit": 50
}
```

**Response `200 OK`**:
```json
{
  "rows": [...],
  "count": 50,
  "columns": ["CustomerId", "Surname", "CreditScore", "Geography", "Gender", "Age", "Tenure", "Balance", "Exited"],
  "source_platform": "kaggle",
  "dataset_name": "churn-modelling",
  "truncated": false,
  "total_available": 10000,
  "requires_auth": false
}
```

---

## 3. Synthetic Generation

### `POST /generate/prompt`
Generates a structured synthetic dataset from an arbitrary text prompt.

**Request Body**:
```json
{
  "prompt": "E-commerce orders with customer email, total price, status, and shipping country",
  "rows": 100
}
```

**Response `200 OK`**:
```json
{
  "rows": [
    {
      "order_id": "ORD-948102",
      "customer_email": "jane.doe@example.com",
      "total_price": 149.99,
      "status": "Shipped",
      "shipping_country": "United States"
    }
  ],
  "count": 100
}
```

---

## 4. Gap Filling & Augmentation

### `POST /datascout/analyze-gaps`
Evaluates a partial dataset against the desired prompt to identify missing attributes or null distributions.

**Request Body**:
```json
{
  "prompt": "Retail customer transaction history with fraud flags",
  "existing_columns": ["customer_id", "transaction_amount", "timestamp"]
}
```

**Response `200 OK`**:
```json
{
  "missing_columns": ["is_fraud", "merchant_category", "card_type"],
  "recommended_strategies": {
    "is_fraud": "Boolean (imbalanced distribution)",
    "merchant_category": "Faker Commerce Category",
    "card_type": "Faker Credit Card Type"
  }
}
```

---

### `POST /datascout/fill-gaps`
Appends missing columns to existing tabular data.

**Request Body**:
```json
{
  "prompt": "Retail transactions with fraud labels",
  "rows": [
    {"customer_id": 101, "transaction_amount": 42.50}
  ]
}
```

---

## 5. RAG Vector Knowledge Base

### `GET /rag/templates`
Lists available production schema templates. Query parameter `?domain=Finance` filters by domain.

### `POST /rag/query`
Returns top-K vector-matched templates for a natural language query.

**Request Body**:
```json
{
  "prompt": "SaaS subscription recurring revenue",
  "top_k": 2
}
```
