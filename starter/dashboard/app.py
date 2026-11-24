"""Milestone 4: Streamlit dashboard. Run: streamlit run starter/dashboard/app.py"""
import os, pandas as pd, plotly.express as px, streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="Gift and Bliss Supplies", layout="wide")

@st.cache_data
def q(sql: str) -> pd.DataFrame:
    return pd.read_sql(sql, create_engine(os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg2://")))

st.title("Gift and Bliss Supplies - Sales Overview")
year = st.sidebar.selectbox("Year", [2022, 2023, 2024, 2025], index=3)

# Cleaning rules from Milestones 1-2: drop cancelled and test orders, merge South-2 into South
VALID = """FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE LOWER(o.status) <> 'cancelled' AND c.name <> 'QA Tester'"""
REGION = "CASE WHEN o.region = 'South-2' THEN 'South' ELSE o.region END"

monthly = q(f"SELECT date_trunc('month', o.order_date)::date AS month, SUM(oi.sales) AS sales {VALID} "
            f"AND EXTRACT(YEAR FROM o.order_date) = {year} GROUP BY 1 ORDER BY 1")
st.plotly_chart(px.line(monthly, x="month", y="sales", title=f"Monthly sales in {year} (INR)", labels={"sales": "Sales (INR)"}), use_container_width=True)

col1, col2 = st.columns(2)
cat = q(
        f"SELECT p.category, ROUND(100*SUM(oi.profit)/SUM(oi.sales), 2) AS profit_ratio_pct "
        f"FROM orders o JOIN customers c ON c.customer_id=o.customer_id JOIN order_items oi ON oi.order_id=o.order_id "
        f"JOIN products p ON p.product_id=oi.product_id "
        f"WHERE LOWER(o.status) <> 'cancelled' AND c.name <> 'QA Tester' AND oi.profit IS NOT NULL "
        f"AND EXTRACT(YEAR FROM o.order_date) = {year} GROUP BY p.category ORDER BY 2 DESC")
col1.plotly_chart(px.bar(cat, x="category", y="profit_ratio_pct", title=f"Profit ratio by category, {year} (%)", labels={"profit_ratio_pct": "Profit ratio (%)"}), use_container_width=True)

reg = q(f"SELECT {REGION} AS region, SUM(oi.sales) AS sales {VALID} AND EXTRACT(YEAR FROM o.order_date) = {year} GROUP BY 1")
tgt = q(f"SELECT CASE WHEN region = 'South-2' THEN 'South' ELSE region END AS region, SUM(sales_target) AS target FROM region_targets WHERE year = {year} GROUP BY 1")
rt = reg.merge(tgt, on="region", how="left").melt(id_vars="region", value_vars=["sales", "target"], var_name="measure", value_name="inr")
col2.plotly_chart(px.bar(rt, x="region", y="inr", color="measure", barmode="group", title=f"Sales vs target by region, {year} (INR)", labels={"inr": "INR"}), use_container_width=True)

ret = q(f"SELECT r.reason, COUNT(*) AS returns FROM returns r JOIN orders o ON o.order_id = r.order_id "
        f"WHERE EXTRACT(YEAR FROM o.order_date) = {year} GROUP BY r.reason ORDER BY 2 DESC")
st.plotly_chart(px.bar(ret, x="reason", y="returns", title=f"Returns by reason, {year} (number of orders)", labels={"returns": "Returned orders"}), use_container_width=True)

st.caption("Built on the Gift and Bliss Supplies project by Instrovate Technologies (cvfine.com)")
