import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="CWS Donor Prototype", layout="wide")
st.title("🌿 CWS Donor Relationship Prototype")
st.caption("Internal donor profile & relationship history tracker.")

csv_path = "cws_donor_dataset.csv"

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    
    donor_type = st.sidebar.radio("Filter Donor Type:", ["All", "Individual", "Institutional"])
    if donor_type != "All":
        df = df[df["Donor_Type"] == donor_type]
        
    search = st.text_input("Search donor by name or program:")
    if search:
        df = df[df["Name"].str.contains(search, case=False) | df["Primary_Interest"].str.contains(search, case=False)]
        
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No dataset found. Run python generate_data.py first.")