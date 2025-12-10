import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# USER LOGIN SYSTEM (simple local validation)
# ---------------------------------------------------

USER_DB = {
    "sachin": "78143",
    "guest": "guest321"
}

def login():
    st.title("🔐 CSR Dashboard Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    login_btn = st.button("Login")

    if login_btn:
        if username in USER_DB and USER_DB[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# ---------------------------------------------------
# MAIN CSR DASHBOARD
# ---------------------------------------------------

def dashboard():
    st.set_page_config(page_title="CSR Dashboard", layout="wide")

    username = st.session_state.get("username", "")
    st.sidebar.success(f"👋 Logged in as **{username}**")

    # ✅ Only Sachin can download anything
    can_download = (username == "sachin")

    # 🔒 For admin: hide ALL dataframe toolbars + built-in CSV buttons
    if not can_download:
        hide_toolbar_css = """
            <style>
                /* Hide the little icon toolbar (eye, download, search, fullscreen) */
                [data-testid="stElementToolbar"] {
                    display: none !important;
                }

                /* Hide any CSV download buttons created by Streamlit */
                button[title="Download as CSV"],
                button[aria-label="Download as CSV"] {
                    display: none !important;
                }
            </style>
        """
        st.markdown(hide_toolbar_css, unsafe_allow_html=True)

    # Logout
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    @st.cache_data
    def load_data():
        return pd.read_csv("merged_csr_data.csv")

    df = load_data()

    # Sidebar filters
    st.sidebar.header("📊 CSR Dashboard Filters")
    companies = sorted(df["Company"].unique())
    selected_company = st.sidebar.selectbox("Select Company", companies)

    filtered = df[df["Company"] == selected_company]

    years = sorted(filtered["Year"].unique())
    selected_years = st.sidebar.multiselect(
        "Select Year(s)", years, default=years
    )

    filtered = filtered[filtered["Year"].isin(selected_years)]

    # KPIs
    total_spent = filtered["Amount_Spent_Cr"].sum()
    total_projects = filtered["Project"].nunique()
    total_states = filtered["State"].nunique()

    st.markdown(f"## 🏢 {selected_company}")

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Spent (Cr)", f"{total_spent:,.2f}")
    col2.metric("📁 Projects", total_projects)
    col3.metric("🌍 States Covered", total_states)

    st.divider()

    # Chart toolbar configuration
    if can_download:
        chart_config = {"displaylogo": False}
    else:
        chart_config = {
            "displaylogo": False,
            "modeBarButtonsToRemove": ["toImage"]  # hide plotly download image
        }

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "📈 Year-wise Spend",
        "🏭 Sector-wise",
        "🗺️ State-wise Spend (with sectors)"
    ])

    # ------------------- TAB 1 -------------------
    with tab1:
        yearly = (
            filtered.groupby("Year")["Amount_Spent_Cr"]
            .sum()
            .reset_index()
            .sort_values("Year")
        )

        fig1 = px.bar(
            yearly,
            x="Year",
            y="Amount_Spent_Cr",
            title="Year-wise CSR Spend",
            text_auto=True,
            color_discrete_sequence=["#ffa600"]
        )

        fig1.update_yaxes(dtick=50)
        st.plotly_chart(fig1, use_container_width=True, config=chart_config)

    # ------------------- TAB 2 -------------------
    with tab2:
        sector = (
            filtered.groupby("Sector")["Amount_Spent_Cr"]
            .sum()
            .reset_index()
            .sort_values("Amount_Spent_Cr", ascending=False)
        )
        fig2 = px.bar(
            sector,
            x="Sector",
            y="Amount_Spent_Cr",
            title="Sector-wise CSR Spend",
            text_auto=True,
            color_discrete_sequence=["#bc5090"],
        )
        st.plotly_chart(fig2, use_container_width=True, config=chart_config)

    # ------------------- TAB 3 -------------------
    with tab3:
        if {"State", "Sector"}.issubset(filtered.columns):
            state_agg = (
                filtered
                .groupby("State")
                .agg(
                    Amount_Spent_Cr=("Amount_Spent_Cr", "sum"),
                    Sectors_List=("Sector", lambda x: ", ".join(sorted(x.dropna().unique())))
                )
                .reset_index()
                .sort_values("Amount_Spent_Cr", ascending=False)
            )

            fig3 = px.bar(
                state_agg,
                x="State",
                y="Amount_Spent_Cr",
                title="State-wise CSR Spend",
                text_auto=True,
                color_discrete_sequence=["#FF6B45"],
                hover_data={
                    "State": True,
                    "Amount_Spent_Cr": ':.2f',
                    "Sectors_List": True,
                },
            )

            fig3.update_layout(showlegend=False)
            fig3.update_yaxes(dtick=20)

            st.plotly_chart(fig3, use_container_width=True, config=chart_config)

    st.divider()

    # Data Table
    st.subheader("📋 Filtered Data")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    # ✅ Explicit CSV download button – only for Sachin
    if can_download:
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name=f"{selected_company}_CSR_Data.csv",
            mime="text/csv",
        )

# ---------------------------------------------------
# APP FLOW CONTROL
# ---------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    dashboard()
else:
    login()

