import sqlite3
import pandas as pd

def load_data():
    conn = sqlite3.connect("cws_donors.db")
    df = pd.read_sql_query("SELECT * FROM donors", conn)
    conn.close()
    return df

def get_summary_stats():
    df = load_data()
    total_raised = df["amount_inr"].sum()
    total_donors = len(df)
    
    # Categorize donors into simple groups
    def categorize(amount):
        if amount >= 100000:
            return "Major CSR Grant"
        elif amount >= 10000:
            return "Mid-Level Supporter"
        else:
            return "Retail Donor"

    df["Category"] = df["amount_inr"].apply(categorize)
    return total_raised, total_donors, df