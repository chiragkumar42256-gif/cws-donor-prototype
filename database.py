import sqlite3

def init_db():
    # This creates a real database file named cws_donors.db
    conn = sqlite3.connect("cws_donors.db")
    cur = conn.cursor()

    # Table 1: Donor records
    cur.execute("""
    CREATE TABLE IF NOT EXISTS donors (
        id TEXT PRIMARY KEY,
        name TEXT,
        donor_type TEXT,
        email TEXT,
        program TEXT,
        amount_inr REAL
    )
    """)

    # Add starter donors if table is empty
    cur.execute("SELECT COUNT(*) FROM donors")
    if cur.fetchone()[0] == 0:
        sample_data = [
            ("D101", "Aarav Sharma", "Individual", "aarav@email.com", "Wild Seve", 5000),
            ("D102", "Titan CSR Foundation", "Institutional", "csr@titan.com", "Wild Shaale", 500000),
            ("D103", "Ananya Iyer", "Individual", "ananya@email.com", "Wild Seve", 2500),
            ("D104", "Infosys Foundation", "Institutional", "grants@infosys.com", "Wild Seve", 1200000),
            ("D105", "Rohan Mehta", "Individual", "rohan@email.com", "Wild Shaale", 15000)
        ]
        cur.executemany("INSERT INTO donors VALUES (?,?,?,?,?,?)", sample_data)

    conn.commit()
    conn.close()
    print("Database is ready and filled with data!")

if __name__ == "__main__":
    init_db()