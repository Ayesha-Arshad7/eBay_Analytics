import streamlit as st
import pandas as pd

st.title("eBay News Analytics Dashboard")

df = pd.read_csv("data/ebay_news.csv")

st.metric("Total Articles", len(df))

st.dataframe(df[["title", "media", "date"]])
