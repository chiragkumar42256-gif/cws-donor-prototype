import sqlite3
import pandas as pd
import os

def init_db():
    conn = sqlite3.connect("cws_donors.db")
    csv_file = "cws_donor_dataset.csv"
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        
        column_mapping = {
            "Donor_ID": "id",
            "Name": "name",
            "Donor_Type": "donor_type",
            "Primary_Interest": "program",
            "Lifetime_INR": "amount_inr",
            "Last_Contact": "last_contact",
            "Acquisition_Source": "source"
        }
        df = df.rename(columns=column_mapping)
        
        if "email" not in df.columns:
            df["email"] = df["name"].apply(lambda x: f"{str(x).lower().replace(' ', '_')}@example.com")
            
        df.to_sql("donors", conn, if_exists="replace", index=False)
        print(f"Database successfully loaded with {len(df)} donors from CSV!")
    else:
        print(f"Error: Could not find {csv_file}")

    conn.close()

if __name__ == "__main__":
    init_db()