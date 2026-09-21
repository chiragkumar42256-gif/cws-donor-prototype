import streamlit as st
import database
import analytics
import ai_services

# Initialize database
database.init_db()

st.set_page_config(page_title="CWS Donor System", layout="wide")
st.title("🌿 CWS Donor Relationship Management (DRM)")

tab1, tab2, tab3 = st.tabs(["📋 Donor Directory", "📊 Giving Analytics", "🤖 AI Note Assistant"])

with tab1:
    st.subheader("All Donors")
    total, count, df = analytics.get_summary_stats()
    
    dtype = st.selectbox("Filter by Category:", ["All", "Individual", "Institutional"])
    if dtype != "All":
        display_df = df[df["donor_type"] == dtype]
    else:
        display_df = df

    st.dataframe(display_df, width="stretch")

with tab2:
    st.subheader("Fundraising Overview")
    total, count, df = analytics.get_summary_stats()
    
    col1, col2 = st.columns(2)
    col1.metric("Total Funds Raised", f"₹{total:,.0f}")
    col2.metric("Total Donors Registered", count)
    
    st.write("### Donor Categories")
    st.bar_chart(df["Category"].value_counts())

with tab3:
    st.subheader("Paste Meeting / Call Notes")
    user_note = st.text_area("What did the donor say on the call?")
    if st.button("Generate Summary & Next Action"):
        if user_note:
            summary = ai_services.clean_meeting_notes(user_note)
            st.success("Action Item Extracted:")
            st.write(summary)
        else:
            st.warning("Please type some notes first.")