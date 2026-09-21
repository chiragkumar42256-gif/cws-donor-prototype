import streamlit as st
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

# Filter Dataframe based on sidebar inputs
filtered_df = df.copy()
if donor_type_filter != "All":
    filtered_df = filtered_df[filtered_df["donor_type"] == donor_type_filter]
if program_filter != "All":
    filtered_df = filtered_df[filtered_df["program"] == program_filter]

# 4. Main Body
st.title("🌿 CWS Donor Relationship Management (DRM)")
tabs = st.tabs(["📋 Donor 360° Directory", "📊 Giving Analytics & Cohorts", "🤖 AI Note Processing"])

# TAB 1: DIRECTORY & 360° VIEW
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
    st.dataframe(filtered_df, width="stretch")

    # Donor 360 Drill-down Expander
    with st.expander("🔎 View Specific Donor 360° Profile"):
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

# TAB 2: ANALYTICS & VISUAL COHORTS
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

# TAB 3: AI INTELLIGENCE & ACTION EXTRACTION
with tabs[2]:
    st.subheader("Field Notes & Phone Log Ingestion")
    st.caption("Convert unstructured field officer notes into actionable next steps using AI.")
    
    user_note = st.text_area(
        "Paste Staff / CSR Call Notes:", 
        height=130, 
        placeholder="e.g., Met with CSR lead today. They are interested in supporting Wild Seve with ₹5 Lakhs, need an audited budget sheet by Friday."
    )
    
    if st.button("✨ Extract Action Items", type="primary"):
        if user_note.strip():
            with st.spinner("Processing context..."):
                extracted = ai_services.clean_meeting_notes(user_note)
                st.success("Extracted Action Plan")
                st.info(extracted)
        else:
            st.warning("Please enter conversation notes before submitting.")