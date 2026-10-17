# Amazon India Serverless Data Lake on AWS

An event-driven data pipeline that turns raw Amazon India e-commerce sales data (about 1.12M orders, 2015-2025) into query-ready Parquet tables and reporting views, using only AWS serverless services.

## Architecture

```
Raw CSV upload (S3: raw/amazon_india/)
        |
        v
S3 event trigger --> AWS Lambda (amazon-india-refresh)
        |
        v
AWS Glue Crawler (schema detection)
        |
        v
Glue Data Catalog (amazon_db.amazon_india)
        |
        v
Athena CTAS --> Curated Parquet table
(partitioned by order_year, duplicates removed)
        |
        v
Athena reporting views
```

## Services Used

- **Amazon S3:** raw and curated data lake storage
- **AWS Lambda:** event-driven orchestration (Python, boto3)
- **AWS Glue:** crawler and Data Catalog for schema discovery
- **Amazon Athena:** SQL transformations and reporting views
- **AWS IAM:** least-privilege roles and inline policies

## How It Works

1. A new CSV uploaded to `raw/amazon_india/` triggers the Lambda function.
2. Lambda starts the Glue crawler and waits for it to finish.
3. Lambda drops and rebuilds the curated table with an Athena CTAS query that casts column types, removes duplicate rows, and writes Snappy-compressed Parquet partitioned by `order_year`.
4. Reporting views sit on top of the curated table.

## Reporting Views

- `vw_revenue_by_state_year`: orders and revenue (Rs Cr) by state and year
- `vw_state_revenue_total`: total revenue and share by state
- `vw_subcategory_revenue`: total revenue and share by product subcategory

## Repository Structure

```
lambda/lambda_function.py   Lambda orchestration code
sql/views.sql               Athena view definitions
docs/                       Screenshots and notes
```

## Setup Notes

- Region: ap-south-1 (Mumbai)
- Lambda timeout: 15 minutes
- Lambda role needs `glue:StartCrawler` and `glue:GetCrawler` on the crawler, plus Athena and S3 access

## Dataset

Amazon India e-commerce transactions: 37 columns covering product, customer, pricing, delivery, festival sale and return details.

## Results

Top states by revenue, queried from the Athena reporting view:

![Athena query results](docs/athena-results.png)