
from pathlib import Path
import base64, csv, hashlib, json, random, sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]
for folder in ['data/raw','data/clean','analysis','sql','docs/charts','docs/screenshots','docs/recordings','tests']:
    (ROOT/folder).mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.edgecolor':'#d5dcd9','axes.labelcolor':'#42554e','xtick.color':'#42554e','ytick.color':'#42554e','figure.facecolor':'#fafbf8','axes.facecolor':'#fafbf8','axes.titleweight':'bold','axes.titlelocation':'left','axes.titlepad':20,'font.size':11,'savefig.dpi':170})
def write_csv(df,path): df.to_csv(ROOT/path,index=False,lineterminator='\n')
def export(fig,name):
    fig.text(.01,.012,'Synthetic portfolio study | Reproduce: python scripts/build.py',fontsize=8,color='#667770')
    fig.savefig(ROOT/f'docs/charts/{name}.png',bbox_inches='tight')
    fig.savefig(ROOT/f'docs/charts/{name}.svg',bbox_inches='tight')
    plt.close(fig)
def query(name,sql):
    (ROOT/f'sql/{name}.sql').write_text(sql.strip()+'\n',encoding='utf-8')
    out=pd.read_sql_query(sql,db)
    write_csv(out,f'analysis/{name}.csv')
    return out
def finish(qa,findings):
    (ROOT/'analysis/quality_report.json').write_text(json.dumps(qa,indent=2)+'\n')
    (ROOT/'analysis/findings.md').write_text(findings,encoding='utf-8')
    import nbformat as nbf
    nb=nbf.v4.new_notebook()
    nb.metadata.kernelspec={'display_name':'Python 3','language':'python','name':'python3'}
    nb.cells=[nbf.v4.new_markdown_cell('# '+TITLE+'\n\nSynthetic data. This notebook executes the checked-in SQL against the rebuilt SQLite warehouse. See the decision memo for interpretation and limitations.'),nbf.v4.new_code_cell("from pathlib import Path\nimport sqlite3, pandas as pd\nroot=Path.cwd()\nif root.name=='analysis': root=root.parent\nconnection=sqlite3.connect(root/'analysis/warehouse.sqlite3')")]
    for f in sorted((ROOT/'sql').glob('*.sql')):
        nb.cells.extend([nbf.v4.new_markdown_cell('## '+f.stem.replace('_',' ').title()),nbf.v4.new_code_cell(f"pd.read_sql_query((root/'sql/{f.name}').read_text(),connection)")])
    nb.cells.append(nbf.v4.new_code_cell('connection.close()'))
    from nbclient import NotebookClient
    NotebookClient(nb,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
    nbf.write(nb,ROOT/'analysis/analysis.ipynb')
    manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['data/raw','data/clean'] for p in sorted((ROOT/folder).glob('*.csv'))}
    (ROOT/'analysis/data_sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
    db.close()

TITLE='Retail margin investigation'
rng=random.Random(81427)
products=pd.DataFrame([{'product_id':i+1,'category':cat,'product':f'{cat} {j+1:02d}','list_price_cents':price+500*j,'unit_cost_cents':int((price+500*j)*ratio)} for i,(cat,j,price,ratio) in enumerate((cat,j,price,ratio) for cat,price,ratio in [('Apparel',6500,.42),('Home',12000,.55),('Electronics',24000,.72),('Accessories',3500,.28)] for j in range(6))])
customers=pd.DataFrame([{'customer_id':i+1,'region':rng.choice(['North','South','East','West']),'segment':rng.choices(['Consumer','Small business'],[.85,.15])[0]} for i in range(1400)])
orders=[]
for i in range(12000):
    date=pd.Timestamp('2024-01-01')+pd.Timedelta(days=rng.randrange(731))
    p=products.iloc[rng.randrange(len(products))]
    discount=rng.choices([0,10,20,30],[.4,.3,.2,.1])[0]
    if p.category=='Electronics' and date.year==2025: discount=rng.choices([0,10,20,30],[.1,.2,.3,.4])[0]
    qty=rng.choices([1,2,3,4],[.6,.25,.1,.05])[0]
    returned=int(rng.random() < (.13 if p.category=='Apparel' else .04)+discount*.0015)
    orders.append({'order_id':f'O{i+1:06d}','order_date':date.strftime('%Y-%m-%d'),'customer_id':rng.randrange(1,1401),'product_id':int(p.product_id),'channel':rng.choice(['Web','Store','Marketplace']),'quantity':qty,'discount_pct':discount,'returned_units':rng.randint(1,qty) if returned else 0,'shipping_cents':rng.choice([450,650,950]),'return_handling_cents':800 if returned else 0})
raw=pd.DataFrame(orders)
raw.loc[:23,'channel']=' web '
invalid=raw.iloc[:12].copy();invalid['order_id']=[f'BAD{i:03d}' for i in range(12)];invalid['quantity']=-1
raw=pd.concat([raw,raw.iloc[100:220],invalid],ignore_index=True)
write_csv(raw,'data/raw/orders.csv');write_csv(products,'data/raw/products.csv');write_csv(customers,'data/raw/customers.csv')
dedup=raw.drop_duplicates('order_id',keep='first').copy()
reject=dedup[(dedup.quantity<=0)|(dedup.returned_units>dedup.quantity)].copy();reject['reason']='Invalid quantity or returned units'
write_csv(reject,'analysis/quarantine.csv')
clean=dedup.drop(reject.index).copy();clean['channel']=clean.channel.str.strip().str.title()
assert len(clean)==12000 and clean.order_id.is_unique
fact=clean.merge(products[['product_id','list_price_cents','unit_cost_cents']],on='product_id',validate='many_to_one')
fact['month']=fact.order_date.str[:7];fact['year']=fact.order_date.str[:4]
fact['discount_band']=fact.discount_pct.astype(str).str.zfill(2)+'%'
fact['net_units']=fact.quantity-fact.returned_units
fact['gross_sales_cents']=fact.quantity*fact.list_price_cents
fact['discount_cents']=fact.gross_sales_cents*fact.discount_pct//100
fact['refund_cents']=fact.returned_units*fact.list_price_cents*(100-fact.discount_pct)//100
fact['net_revenue_cents']=fact.gross_sales_cents-fact.discount_cents-fact.refund_cents
fact['net_cogs_cents']=fact.net_units*fact.unit_cost_cents
fact['contribution_cents']=fact.net_revenue_cents-fact.net_cogs_cents-fact.shipping_cents-fact.return_handling_cents
for name,df in [('orders',fact),('products',products),('customers',customers)]: write_csv(df,f'data/clean/{name}.csv')
db=sqlite3.connect(ROOT/'analysis/warehouse.sqlite3')
for name,df in [('orders',fact),('products',products),('customers',customers)]: df.to_sql(name,db,index=False,if_exists='replace')
kpi=query('01_yearly_bridge','''SELECT year,COUNT(*) orders,SUM(gross_sales_cents)/100.0 gross_sales,SUM(discount_cents)/100.0 discounts,SUM(refund_cents)/100.0 refunds,SUM(net_revenue_cents)/100.0 net_revenue,SUM(net_cogs_cents)/100.0 net_cogs,SUM(shipping_cents+return_handling_cents)/100.0 fulfillment,SUM(contribution_cents)/100.0 contribution,1.0*SUM(contribution_cents)/SUM(net_revenue_cents) contribution_margin,1.0*SUM(returned_units)/SUM(quantity) unit_return_rate FROM orders GROUP BY year ORDER BY year''')
monthly=query('02_monthly_trend','''SELECT month,SUM(net_revenue_cents)/100.0 net_revenue,SUM(contribution_cents)/100.0 contribution,1.0*SUM(contribution_cents)/SUM(net_revenue_cents) margin FROM orders GROUP BY month ORDER BY month''')
category=query('03_category_discount','''SELECT p.category,o.year,o.discount_band,COUNT(*) orders,SUM(o.net_revenue_cents)/100.0 revenue,SUM(o.contribution_cents)/100.0 contribution,1.0*SUM(o.contribution_cents)/NULLIF(SUM(o.net_revenue_cents),0) margin,1.0*SUM(o.returned_units)/SUM(o.quantity) unit_return_rate FROM orders o JOIN products p USING(product_id) GROUP BY p.category,o.year,o.discount_band ORDER BY p.category,o.year,o.discount_band''')
regions=query('04_region_contribution','''SELECT c.region,COUNT(*) orders,SUM(o.net_revenue_cents)/100.0 revenue,SUM(o.contribution_cents)/100.0 contribution,1.0*SUM(o.contribution_cents)/SUM(o.net_revenue_cents) margin FROM orders o JOIN customers c USING(customer_id) GROUP BY c.region ORDER BY contribution DESC''')
repeat=query('05_repeat_90_day','''WITH first_order AS (SELECT customer_id,MIN(order_date) first_date FROM orders GROUP BY customer_id),eligible AS (SELECT * FROM first_order WHERE date(first_date,'+90 days')<='2025-12-31'), flags AS (SELECT e.customer_id,substr(e.first_date,1,7) cohort_month,MAX(CASE WHEN o.order_date>e.first_date AND o.order_date<=date(e.first_date,'+90 days') THEN 1 ELSE 0 END) repeat_90 FROM eligible e JOIN orders o USING(customer_id) GROUP BY e.customer_id,e.first_date) SELECT cohort_month,COUNT(*) eligible_customers,SUM(repeat_90) repeat_customers,AVG(repeat_90) repeat_rate FROM flags GROUP BY cohort_month ORDER BY cohort_month''')
qa={'raw_orders':len(raw),'duplicate_rows_removed':120,'quarantined_orders':len(reject),'channel_values_normalized':24,'clean_orders':len(fact),'orphan_products':int((~fact.product_id.isin(products.product_id)).sum()),'orphan_customers':int((~fact.customer_id.isin(customers.customer_id)).sum()),'revenue_bridge_residual_cents':int((fact.gross_sales_cents-fact.discount_cents-fact.refund_cents-fact.net_revenue_cents).sum()),'currency':'USD','snapshot':'2026-02-01','seed':81427}
fig,axs=plt.subplots(2,1,figsize=(13,8),sharex=True,gridspec_kw={'height_ratios':[2,1]})
x=np.arange(len(monthly));axs[0].plot(x,monthly.net_revenue/1000,color='#1f6958',lw=2.8,label='Net revenue');axs[0].fill_between(x,monthly.contribution/1000,color='#bd7756',alpha=.8,label='Contribution');axs[0].set_title('Revenue alone hides margin erosion',fontsize=23);axs[0].set_ylabel('USD thousands');axs[0].legend(frameon=False,ncol=2)
axs[1].plot(x,monthly.margin*100,color='#bd7756',lw=2.5);axs[1].set_ylabel('Contribution margin %');axs[1].set_xticks(x[::3],monthly.month.iloc[::3]);axs[1].axvline(11.5,color='#99a69e',ls='--');fig.tight_layout(rect=(0,.04,1,1));export(fig,'01_revenue_margin')
fig,ax=plt.subplots(figsize=(12,6));p=category[category.year=='2025'].pivot(index='category',columns='discount_band',values='margin');im=ax.imshow(p.values*100,cmap='RdYlGn',vmin=-20,vmax=70,aspect='auto');ax.set_xticks(range(4),p.columns);ax.set_yticks(range(4),p.index);ax.set_title('2025 contribution margin by discount tier',fontsize=22)
for i in range(4):
    for j in range(4): ax.text(j,i,f'{p.iloc[i,j]*100:.1f}%',ha='center',va='center',fontsize=18,color='white' if p.iloc[i,j]>.50 else '#192e28')
fig.colorbar(im,ax=ax,label='Contribution / net revenue (%)');ax.set_xlabel('Discount tier; descriptive, not a causal estimate');fig.tight_layout(rect=(0,.04,1,1));export(fig,'02_discount_risk')
fig,ax=plt.subplots(figsize=(12,6));row=kpi.iloc[-1];labels=['Gross sales','Discounts','Refunds','Net COGS','Fulfillment','Contribution'];vals=[row.gross_sales,-row.discounts,-row.refunds,-row.net_cogs,-row.fulfillment,row.contribution];running=0
for i,v in enumerate(vals):
    base=0 if i in [0,5] else running+min(v,0)
    ax.bar(i,abs(v)/1000,bottom=base/1000,color='#1f6958' if i in [0,5] else '#bd7756',width=.65)
    ax.text(i,(base+abs(v))/1000+8,f'${v/1000:,.0f}k',ha='center',fontsize=10)
    if i<5: running+=v
ax.set_xticks(range(6),labels);ax.set_ylabel('USD thousands');ax.set_title('2025 gross sales to contribution bridge',fontsize=23);fig.tight_layout(rect=(0,.04,1,1));export(fig,'03_margin_bridge')
fig,ax=plt.subplots(figsize=(12,5));ax.bar(regions.region,regions.contribution/1000,color='#1f6958');ax.set_ylabel('USD thousands');ax.set_title('Contribution by customer region',fontsize=23);ax.bar_label(ax.containers[0],fmt='%.1f',padding=5);fig.tight_layout(rect=(0,.04,1,1));export(fig,'04_regions')
worst=category[(category.year=='2025')&(category.orders>=30)].sort_values('margin').iloc[0]
findings=f'''# Decision memo: retail margin

**Scope:** 12,000 synthetic, single-line orders across 2024–2025. Currency: USD. All return outcomes have a full 30-day observation window as of 2026-02-01. These are simulated findings, not employer results.

## What changed

Net revenue was ${kpi.iloc[0].net_revenue:,.0f} in 2024 and ${kpi.iloc[1].net_revenue:,.0f} in 2025. Contribution margin moved from {kpi.iloc[0].contribution_margin:.1%} to {kpi.iloc[1].contribution_margin:.1%}. The weakest sufficiently populated 2025 cell was **{worst['category']} at {worst.discount_band} discount**: {worst.margin:.1%} margin across {worst.orders:,} orders.

## Proposed decision

Review discount approval rules for negative-contribution category/tier combinations. Run a limited randomized discount test before changing pricing broadly; this observational comparison does not identify price elasticity or causal uplift. Monitor conversion, units, contribution per visitor and 30-day returns together.

## Method

Contribution = gross sales − discounts − refunds − net COGS − shipping − return handling. Returned inventory is assumed fully recoverable at unit cost; markdowns, damaged inventory, advertising, tax and overhead are excluded. This is contribution, not net profit. Rates are ratios of sums, not averages of group percentages. Orders have exactly one product line, so row count equals order count.

The 90-day repeat metric requires a later calendar-date order within 90 days. Customers with incomplete follow-up are excluded; same-day multiple orders do not count as repeat. Acquisition months with small eligible counts are unstable.

## Quality and reconciliation

Raw 12,132 rows → remove 120 exact duplicate order IDs → quarantine 12 negative-quantity rows → 12,000 valid orders. Normalize 24 channel labels. Both dimension joins are many-to-one; orphan counts and the revenue bridge residual equal zero. Quarantine and machine-readable QA are committed.

## Limits and next questions

Patterns are intentionally encoded in a seeded synthetic generator. They demonstrate workflow, not external business evidence. No claim of realized savings is supported. A production study would need payment timing, return dates, inventory recovery, customer acquisition costs and a pricing experiment.
'''
finish(qa,findings)
