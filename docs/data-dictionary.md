# Data dictionary

| Table | Grain | Primary key | Clean rows |
|---|---|---|---|
| orders | One single-product order | order_id | 12,000 |
| products | One fictional product | product_id | 24 |
| customers | One fictional customer | customer_id | 1,400 |

All money columns ending in `_cents` store integer USD cents. DAX divides totals by 100 for display. Dates are ISO calendar dates. The model uses text month/year categories, not a marked date table.

| Fields | Definition |
|---|---|
| order_id, order_date | Unique single-line order and purchase date |
| customer_id, product_id | Foreign keys to the two dimensions |
| channel | Normalized Web, Store or Marketplace |
| quantity, returned_units, net_units | Purchased, returned, and retained unit counts |
| discount_pct, discount_band | Percent discount and sortable category label |
| list_price_cents, unit_cost_cents | Product unit selling price and unit inventory cost |
| gross_sales_cents | Quantity × unit list price |
| discount_cents | Gross sales × discount percentage |
| refund_cents | Returned units × discounted unit price |
| net_revenue_cents | Gross sales − discounts − refunds |
| net_cogs_cents | Retained units × unit cost; returned inventory is assumed fully recoverable |
| shipping_cents, return_handling_cents | Fulfillment cost per order; return handling applies to returned orders |
| contribution_cents | Net revenue − net COGS − shipping − return handling |
| month, year | Order-opening period, formatted YYYY-MM and YYYY |
| product, category | Fictional product label and merchandising category |
| region, segment | Fictional customer region and customer type |

Contribution margin = SUM(contribution_cents) / SUM(net_revenue_cents). Unit return rate = SUM(returned_units) / SUM(quantity). The repeat-customer SQL requires a later calendar-date order within 90 days and excludes incomplete follow-up. Contribution excludes tax, advertising and overhead.

[Machine-readable column profile](../analysis/data_dictionary.csv) lists inferred types, null counts and distinct counts. Both relationships are many-to-one and filter from dimension to fact.
