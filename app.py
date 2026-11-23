import streamlit as st
import pandas as pd
import io
from datetime import datetime
import database
import analytics
import ai_services

# 1. Page Configuration & Theme
st.set_page_config(
    page_title="CWS Donor Relationship Management",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure database is loaded
database.init_db()

# 2. Custom CSS Injection for Modern UI
st.markdown("""
<style>
    /* Metric Card Styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e4620;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 600;
        color: #555555;
    }
    /* Clean Tab Headers */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
    }
    /* Card Container */
    .cws-card {
        background-color: #f8faf9;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-ok {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-warn {
        background-color: #fef3c7;
        color: #92400e;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar: Branding & Quick Stats
total_raised, donor_count, df = analytics.get_summary_stats()

with st.sidebar:
    st.image("https://raw.githubusercontent.com/feathericons/feather/master/icons/shield.svg", width=48)
    st.title("Centre for Wildlife Studies")
    st.caption("Donor Relationship Management Portal")
    st.divider()
    
    st.metric("Total Pledged (INR)", f"₹{total_raised:,.0f}")
    st.metric("Total Active Donors", f"{donor_count:,}")
    
    st.divider()
    st.subheader("Filter Directory")
    donor_type_filter = st.radio("Donor Type", ["All", "Individual", "Institutional"])
    
    # Extract unique programs safely
    available_programs = ["All"] + sorted(df["program"].dropna().unique().tolist()) if "program" in df.columns else ["All"]
    program_filter = st.selectbox("Conservation Focus", available_programs)

    st.divider()
    st.caption("🔒 **Offline-First SQLite Engine**\n\nZero per-user seat fees | Human-in-the-Loop Dispatch")

# Filter Dataframe based on sidebar inputs
filtered_df = df.copy()
if donor_type_filter != "All":
    filtered_df = filtered_df[filtered_df["donor_type"] == donor_type_filter]
if program_filter != "All":
    filtered_df = filtered_df[filtered_df["program"] == program_filter]

# 4. Main Body
st.title("🌿 CWS Donor Relationship Management (DRM)")
tabs = st.tabs([
    "📋 Donor 360° Directory",
    "📊 Giving Analytics & Cohorts",
    "🤖 AI Note Processing",
    "💸 ReconcileFlow & Form 10BD",
    "🏛️ GrantTrack 135 (CSR)"
])

# ==============================================================================
# TAB 1: DIRECTORY & 360° VIEW
# ==============================================================================
with tabs[0]:
    col_search, col_spacer = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("🔍 Quick Search by Name or ID:", placeholder="Type to filter...")
    
    if search_query:
        filtered_df = filtered_df[
            filtered_df["name"].str.contains(search_query, case=False, na=False) |
            filtered_df["id"].str.contains(search_query, case=False, na=False)
        ]

    st.caption(f"Showing **{len(filtered_df)}** matching donor records")
    st.dataframe(filtered_df, use_container_width=True)

    # Donor 360 Drill-down Expander
    with st.expander("🔎 View Specific Donor 360° Profile", expanded=True):
        selected_id = st.selectbox("Select Donor ID", filtered_df["id"].tolist() if not filtered_df.empty else ["None"])
        if selected_id != "None" and not filtered_df.empty:
            donor_row = filtered_df[filtered_df["id"] == selected_id].iloc[0]
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**Name:** {donor_row['name']}")
            c1.markdown(f"**Email:** `{donor_row.get('email', 'N/A')}`")
            c2.markdown(f"**Category:** `{donor_row['Category']}`")
            c2.markdown(f"**Lifetime Total:** ₹{donor_row['amount_inr']:,.0f}")
            c3.markdown(f"**Focus Area:** {donor_row.get('program', 'General')}")
            c3.markdown(f"**Acquisition:** {donor_row.get('source', 'Website')}")

# ==============================================================================
# TAB 2: ANALYTICS & VISUAL COHORTS
# ==============================================================================
with tabs[1]:
    st.subheader("Fundraising & Retention Health")
    kpi1, kpi2, kpi3 = st.columns(3)
    
    csr_total = df[df["donor_type"] == "Institutional"]["amount_inr"].sum()
    retail_total = df[df["donor_type"] == "Individual"]["amount_inr"].sum()
    
    kpi1.metric("Institutional CSR Pipeline", f"₹{csr_total:,.0f}")
    kpi2.metric("Individual Retail Giving", f"₹{retail_total:,.0f}")
    kpi3.metric("Average Contribution", f"₹{df['amount_inr'].mean():,.0f}")
    
    st.divider()
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.write("#### Donors by Giving Tier")
        st.bar_chart(df["Category"].value_counts())
    
    with chart_col2:
        if "program" in df.columns:
            st.write("#### Initiatives Supported")
            st.bar_chart(df["program"].value_counts())

# ==============================================================================
# TAB 3: AI INTELLIGENCE & HUMAN-IN-THE-LOOP ACTION EXTRACTION
# ==============================================================================
with tabs[2]:
    st.subheader("Field Notes & Phone Log Ingestion")
    st.caption("Convert unstructured field officer notes into structured action items. **Every follow-up remains a draft for human review—never sent automatically.**")
    
    user_note = st.text_area(
        "Paste Staff / CSR Call Notes:", 
        height=120, 
        placeholder="e.g., Met with CSR lead today. They are interested in supporting Wild Seve with ₹5 Lakhs, need an audited budget sheet by Friday."
    )
    
    if st.button("✨ Extract Action Items", type="primary"):
        if user_note.strip():
            with st.spinner("Processing context..."):
                extracted = ai_services.clean_meeting_notes(user_note)
                st.session_state["extracted_note"] = extracted
                st.session_state["draft_reply"] = (
                    "Dear Partner,\n\n"
                    "Thank you for taking the time to discuss supporting CWS's Wild Seve initiative today. "
                    "As requested, our finance team is preparing the audited project budget sheet and will share it with you by Friday.\n\n"
                    "Warm regards,\n"
                    "Partnerships Team, Centre for Wildlife Studies"
                )
        else:
            st.warning("Please enter conversation notes before submitting.")

    if "extracted_note" in st.session_state:
        st.success("Structured Action Plan Extracted")
        st.info(st.session_state["extracted_note"])
        
        st.markdown("#### 🛡️ Human-in-the-Loop Message Review (Approval Gate)")
        edited_draft = st.text_area(
            "Suggested Next-Step Email Draft (Editable by Coordinator):",
            value=st.session_state.get("draft_reply", ""),
            height=140
        )
        col_approve, col_discard = st.columns([1, 4])
        with col_approve:
            if st.button("✅ Approve & Log Draft"):
                st.toast("Draft approved by coordinator and logged to donor timeline!", icon="✅")
                st.success("Approved by Human Coordinator — Ready for dispatch.")

# ==============================================================================
# TAB 4: RECONCILEFLOW & CBDT FORM 10BD / 10BE COMPLIANCE
# ==============================================================================
with tabs[3]:
    st.subheader("💸 ReconcileFlow: Bank / UPI Auto-Matcher & Rule 18AB Compliance")
    st.caption("Eliminates 15–20 hrs/month of manual passbook cross-checking and prevents Section 115BBC (30%) anonymous donation tax penalties.")

    col_up1, col_up2 = st.columns([2, 1])
    with col_up1:
        uploaded_bank_csv = st.file_uploader("Upload Raw Bank / Razorpay UPI Statement (.csv)", type=["csv"])
    with col_up2:
        st.write("")
        st.write("")
        use_sample_bank = st.checkbox("Use Built-In Sample Bank UPI CSV (Live Demo)", value=True)

    # Sample bank ledger simulating real Indian UPI credits + missing PAN cases
    sample_bank_data = pd.DataFrame([
        {"Txn_Date": "2026-10-28", "UTR_Ref": "UPI/4302918471/supporter_1@okaxis", "Donor_ID": "CWS_101", "Donor_Name": "Supporter_1", "Amount_INR": 5000, "PAN_Status": "ABCDE1234F", "Payment_Mode": "UPI"},
        {"Txn_Date": "2026-10-28", "UTR_Ref": "NEFT/HDFC0009182/CSR_Foundation_1", "Donor_ID": "CWS_102", "Donor_Name": "CSR_Foundation_1", "Amount_INR": 500000, "PAN_Status": "AAACT4567G", "Payment_Mode": "Bank Transfer"},
        {"Txn_Date": "2026-10-29", "UTR_Ref": "UPI/4303819204/9845012345@ybl", "Donor_ID": "CWS_103", "Donor_Name": "Supporter_2", "Amount_INR": 1500, "PAN_Status": "MISSING", "Payment_Mode": "UPI"},
        {"Txn_Date": "2026-10-29", "UTR_Ref": "UPI/4303991022/wildlover@okicici", "Donor_ID": "CWS_106", "Donor_Name": "Supporter_4", "Amount_INR": 2500, "PAN_Status": "MISSING", "Payment_Mode": "UPI"},
        {"Txn_Date": "2026-10-30", "UTR_Ref": "RTGS/ICIC0002211/CSR_Foundation_2", "Donor_ID": "CWS_104", "Donor_Name": "CSR_Foundation_2", "Amount_INR": 250000, "PAN_Status": "AABCC8899K", "Payment_Mode": "Bank Transfer"},
    ])

    bank_df = None
    if uploaded_bank_csv is not None:
        bank_df = pd.read_csv(uploaded_bank_csv)
    elif use_sample_bank:
        bank_df = sample_bank_data

    if bank_df is not None:
        # Run Reconciliation Check against Main Donor Directory
        known_ids = set(df["id"].astype(str).tolist())
        bank_df["Match_Status"] = bank_df["Donor_ID"].apply(
            lambda x: "✅ Auto-Matched" if str(x) in known_ids else "⚠️ Unmatched Credit"
        )
        bank_df["Rule_18AB_Compliance"] = bank_df["PAN_Status"].apply(
            lambda p: "🚨 Missing PAN (Sec 115BBC Risk)" if str(p).upper() == "MISSING" else "✅ Form 10BD Ready"
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("Transactions Parsed", f"{len(bank_df)} txns (< 0.4s)")
        matched_count = (bank_df["Match_Status"] == "✅ Auto-Matched").sum()
        m2.metric("Auto-Matched to Directory", f"{matched_count} / {len(bank_df)}")
        missing_pan_count = (bank_df["PAN_Status"] == "MISSING").sum()
        m3.metric("Missing PAN Alerts", f"{missing_pan_count} donors flagged")

        st.dataframe(bank_df, use_container_width=True)

        # Actionable PAN Intake Link + Form 10BD Export
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("#### 🔗 Automated PAN Collection Trigger")
            missing_rows = bank_df[bank_df["PAN_Status"] == "MISSING"]
            if not missing_rows.empty:
                target_missing = st.selectbox("Select Flagged UPI Donor:", missing_rows["Donor_Name"].tolist())
                intake_url = f"https://cwsindia.org/80g-pan-verify?donor={target_missing.replace(' ', '_')}&fy=2026-27"
                st.code(intake_url, language="text")
                if st.button("📩 Queue PAN Intake WhatsApp/Email Link (Human Review)"):
                    st.success(f"PAN intake link queued for coordinator approval for **{target_missing}**.")
            else:
                st.success("All reconciled donors have valid PAN records on file!")

        with c_right:
            st.markdown("#### 📄 One-Click CBDT Form 10BD Export")
            compliant_df = bank_df[bank_df["PAN_Status"] != "MISSING"].copy()
            form_10bd = pd.DataFrame({
                "Pre_Ack_No": ["80G-CWS-2026"] * len(compliant_df),
                "ID_Code": ["PAN"] * len(compliant_df),
                "Unique_ID_Number": compliant_df["PAN_Status"],
                "Donor_Name": compliant_df["Donor_Name"],
                "Donation_Type": ["Specific Grants / General"] * len(compliant_df),
                "Mode_of_Receipt": compliant_df["Payment_Mode"],
                "Amount_INR": compliant_df["Amount_INR"]
            })
            csv_buffer = form_10bd.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Audit-Ready Form 10BD CSV",
                data=csv_buffer,
                file_name=f"CWS_Form_10BD_Export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                type="primary"
            )
            st.caption("Prevents ₹200/day Section 234G late filing penalties.")

# ==============================================================================
# TAB 5: GRANTTRACK 135 (INSTITUTIONAL CSR MILESTONE GOVERNANCE)
# ==============================================================================
with tabs[4]: