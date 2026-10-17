import boto3
import time

ATHENA = boto3.client("athena")
GLUE = boto3.client("glue")
S3 = boto3.resource("s3")
BUCKET = "dhinesh-de-raw-482913"
CURATED_PREFIX = "curated/amazon_india/"
OUTPUT = f"s3://{BUCKET}/athena-results/"
DB = "amazon_india_db"
CRAWLER = "amazon-india-crawler"

CTAS = """
CREATE TABLE amazon_india_db.amazon_india_curated
WITH (
  format = 'PARQUET',
  parquet_compression = 'SNAPPY',
  external_location = 's3://dhinesh-de-raw-482913/curated/amazon_india/',
  partitioned_by = ARRAY['order_year']
) AS
SELECT
  transaction_id, order_date, customer_id, product_id, product_name,
  category, subcategory, brand,
  TRY_CAST(original_price_inr AS double) AS original_price_inr,
  TRY_CAST(discount_percent AS double) AS discount_percent,
  TRY_CAST(discounted_price_inr AS double) AS discounted_price_inr,
  TRY_CAST(quantity AS integer) AS quantity,
  TRY_CAST(subtotal_inr AS double) AS subtotal_inr,
  TRY_CAST(delivery_charges AS double) AS delivery_charges,
  TRY_CAST(final_amount_inr AS double) AS final_amount_inr,
  customer_city, customer_state, customer_tier, payment_method,
  TRY_CAST(delivery_days AS integer) AS delivery_days,
  is_prime_member, is_festival_sale, festival_name, return_status,
  order_month, order_quarter,
  TRY_CAST(order_year AS integer) AS order_year
FROM amazon_db.amazon_india
WHERE NOT is_duplicate
"""


def run(sql):
    qid = ATHENA.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": DB},
        ResultConfiguration={"OutputLocation": OUTPUT},
    )["QueryExecutionId"]
    while True:
        status = ATHENA.get_query_execution(QueryExecutionId=qid)["QueryExecution"]["Status"]
        if status["State"] in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(3)
    if status["State"] != "SUCCEEDED":
        raise Exception(f"{status['State']}: {status.get('StateChangeReason')}")


def run_crawler():
    try:
        GLUE.start_crawler(Name=CRAWLER)
    except GLUE.exceptions.CrawlerRunningException:
        pass
    time.sleep(10)
    while GLUE.get_crawler(Name=CRAWLER)["Crawler"]["State"] != "READY":
        time.sleep(10)
    last = GLUE.get_crawler(Name=CRAWLER)["Crawler"].get("LastCrawl", {})
    if last.get("Status") != "SUCCEEDED":
        raise Exception(f"Crawler failed: {last.get('ErrorMessage')}")


def lambda_handler(event, context):
    run_crawler()
    run("DROP TABLE IF EXISTS amazon_india_curated")
    S3.Bucket(BUCKET).objects.filter(Prefix=CURATED_PREFIX).delete()
    run(CTAS)
    return {"status": "crawler ran and curated table refreshed"}