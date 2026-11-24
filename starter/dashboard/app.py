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

# Example chart (raw data, NOT cleaned). Your job: apply the rules you found in M1-M2.
raw = q("SELECT date_trunc('month', order_date)::date AS month, sum(sales) AS sales "
        "FROM orders JOIN order_items USING(order_id) GROUP BY 1 ORDER BY 1")
st.plotly_chart(px.line(raw, x="month", y="sales", title="Monthly sales (INR) - uncleaned"), use_container_width=True)

# TODO 1: replace with cleaned numbers (exclude test and cancelled orders, merge South-2 into South)
# TODO 2: add at least 3 charts with titles and units (category profit ratio, region vs target, returns)
# TODO 3: add one filter (year or region) with st.sidebar


st.caption("Built on the Gift and Bliss Supplies project by Instrovate Technologies (cvfine.com)")
