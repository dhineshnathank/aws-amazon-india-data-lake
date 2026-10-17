CREATE VIEW amazon_india_db.vw_revenue_by_state_year AS
SELECT
  customer_state,
  order_year,
  COUNT(*) AS orders,
  ROUND(SUM(final_amount_inr) / 10000000, 2) AS revenue_cr
FROM amazon_india_db.amazon_india_curated
GROUP BY customer_state, order_year;

CREATE VIEW amazon_india_db.vw_state_revenue_total AS
SELECT
  customer_state,
  SUM(orders) AS orders,
  ROUND(SUM(revenue_cr), 2) AS revenue_cr,
  ROUND(100.0 * SUM(revenue_cr) / SUM(SUM(revenue_cr)) OVER (), 2) AS pct_of_total
FROM amazon_india_db.vw_revenue_by_state_year
GROUP BY customer_state;

CREATE VIEW amazon_india_db.vw_subcategory_revenue AS
SELECT
  subcategory,
  COUNT(*) AS orders,
  ROUND(SUM(final_amount_inr) / 10000000, 2) AS revenue_cr,
  ROUND(100.0 * SUM(final_amount_inr) / SUM(SUM(final_amount_inr)) OVER (), 2) AS pct_of_total
FROM amazon_india_db.amazon_india_curated
GROUP BY subcategory;
