SELECT month,SUM(net_revenue_cents)/100.0 net_revenue,SUM(contribution_cents)/100.0 contribution,1.0*SUM(contribution_cents)/SUM(net_revenue_cents) margin FROM orders GROUP BY month ORDER BY month
