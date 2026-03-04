"""Streamlit app for Gazetted Rates Reckoner with Supabase integration"""
import streamlit as st
import pandas as pd
from supabase_client import SupabaseRatesClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Gazetted Rates Reckoner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    try:
        return SupabaseRatesClient()
    except ValueError as e:
        return None

db = init_supabase()

if db is None:
    st.error("❌ Database Connection Failed")
    st.info("""
    Please set the following environment variables in your `.env` file:
    - SUPABASE_URL
    - SUPABASE_KEY
    
    Then restart the Streamlit app.
    """)
    st.stop()

# App title
st.title("📊 Gazetted Rates Reckoner")
st.markdown("---")

# Sidebar navigation
page = st.sidebar.radio(
    "📑 Navigation",
    ["🧮 Calculator", "📋 View Data", "➕ Manage Rates", "⚙️ Admin Panel"],
    label_visibility="collapsed"
)

# ======================= PAGE 1: CALCULATOR =======================
if page == "🧮 Calculator":
    st.subheader("Rate Calculator")
    st.write("Select a service and calculate the total amount")
    
    # Get available years
    years = db.get_all_years()
    if not years:
        st.warning("⚠️ No rates available in database. Please upload data first.")
        st.stop()
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_year = st.selectbox("📅 Select Year", years, index=len(years)-1)
    
    # Load rates for selected year
    rates_df = db.get_rates_by_year(selected_year)
    
    if rates_df.empty:
        st.warning(f"⚠️ No rates found for {selected_year}")
    else:
        with col2:
            service_categories = sorted(rates_df["service_category"].unique())
            selected_category = st.selectbox("🏥 Service Category", service_categories)
        
        # Filter services by category
        services_in_category = sorted(rates_df[
            rates_df["service_category"] == selected_category
        ]["service_name"].unique())
        
        selected_service = st.selectbox("🔧 Select Service", services_in_category)
        
        # Get the rate
        rate_info = db.get_rate_by_service(
            selected_year,
            selected_category,
            selected_service
        )
        
        if rate_info:
            st.success(f"✅ Rate Found: ₹{rate_info['amount']} {rate_info['unit']}")
            
            # Display rate details
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💰 Amount", f"₹{rate_info['amount']}")
            with col2:
                st.metric("📦 Unit", rate_info['unit'])
            with col3:
                st.metric("🏷️ Type", rate_info['rate_type'])
            with col4:
                st.metric("📅 Year", selected_year)
            
            if rate_info['remarks']:
                st.info(f"📌 **Remarks:** {rate_info['remarks']}")
            
            st.markdown("---")
            
            # Calculation section
            st.subheader("💻 Calculate Total Amount")
            quantity = st.number_input(
                "Enter Quantity",
                value=1,
                min_value=1,
                step=1
            )
            
            # Calculate total
            total = rate_info['amount'] * quantity
            
            # Display result
            col1, col2 = st.columns([2, 1])
            with col1:
                st.metric("📊 Total Amount", f"₹{total:,.2f}", delta=f"{quantity} units")
            
            # Summary box
            st.markdown("""
            <div style="background-color:#e8f5e9; padding:20px; border-radius:10px; border-left:5px solid #4caf50;">
                <h3>✅ Calculation Summary</h3>
                <p><strong>Rate per unit:</strong> ₹{}</p>
                <p><strong>Quantity:</strong> {}</p>
                <p><strong>Total Amount:</strong> ₹{:,.2f}</p>
            </div>
            """.format(rate_info['amount'], quantity, total), unsafe_allow_html=True)

# ======================= PAGE 2: VIEW DATA =======================
elif page == "📋 View Data":
    st.subheader("View Gazetted Rates")
    
    years = db.get_all_years()
    if not years:
        st.warning("⚠️ No data available")
        st.stop()
    
    selected_year = st.selectbox("📅 Select Year to View", years, index=len(years)-1)
    
    rates_df = db.get_rates_by_year(selected_year)
    
    if rates_df.empty:
        st.info("ℹ️ No rates found for this year")
    else:
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Rates", len(rates_df))
        with col2:
            st.metric("🏢 Categories", rates_df["service_category"].nunique())
        with col3:
            st.metric("📈 Average Rate", f"₹{rates_df['amount'].mean():,.2f}")
        with col4:
            st.metric("💹 Max Rate", f"₹{rates_df['amount'].max():,.2f}")
        
        st.markdown("---")
        
        # Display data
        st.subheader(f"📋 Rates for {selected_year}")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            categories = sorted(rates_df["service_category"].unique())
            selected_filter = st.multiselect("🏥 Filter by Category", categories, default=categories)
        
        with col2:
            rate_types = sorted(rates_df["rate_type"].unique())
            selected_types = st.multiselect("🏷️ Filter by Type", rate_types, default=rate_types)
        
        # Apply filters
        filtered_df = rates_df[
            (rates_df["service_category"].isin(selected_filter)) &
            (rates_df["rate_type"].isin(selected_types))
        ].copy()
        
        # Display table
        display_df = filtered_df[['service_category', 'service_name', 'amount', 'unit', 'rate_type', 'remarks']].copy()
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Download options
        col1, col2 = st.columns(2)
        
        with col1:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                "📥 Download as CSV",
                csv,
                f"gazetted_rates_{selected_year}.csv",
                "text/csv"
            )
        
        with col2:
            excel_buffer = filtered_df.to_excel(index=False, engine='openpyxl')
            st.download_button(
                "📥 Download as Excel",
                excel_buffer,
                f"gazetted_rates_{selected_year}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ======================= PAGE 3: MANAGE RATES =======================
elif page == "➕ Manage Rates":
    st.subheader("Manage Rates")
    
    tab1, tab2 = st.tabs(["➕ Add Single Rate", "📦 Bulk Upload"])
    
    with tab1:
        st.write("Add a new rate to the database")
        
        with st.form(key="add_rate_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                year = st.number_input("📅 Year", min_value=2020, max_value=2100, value=2024)
                rate_type = st.selectbox("🏷️ Rate Type", ["standard", "special", "amended"])
            
            with col2:
                service_category = st.text_input("🏢 Service Category", placeholder="e.g., Hospital")
                service_name = st.text_input("🔧 Service Name", placeholder="e.g., General Consultation")
            
            col3, col4 = st.columns(2)
            
            with col3:
                amount = st.number_input("💰 Amount (₹)", min_value=0.0, step=0.01, value=100.0)
                unit = st.text_input("📦 Unit", value="per service")
            
            with col4:
                remarks = st.text_area("📝 Remarks (optional)", height=80)
            
            submit_button = st.form_submit_button("✅ Add Rate", use_container_width=True)
            
            if submit_button:
                if not service_category or not service_name:
                    st.error("❌ Please fill in all required fields")
                else:
                    if db.add_rate(
                        year=year,
                        rate_type=rate_type,
                        service_category=service_category,
                        service_name=service_name,
                        amount=amount,
                        unit=unit,
                        remarks=remarks,
                        created_by=st.session_state.get("user", "admin")
                    ):
                        st.success("✅ Rate added successfully!")
                        st.rerun()
    
    with tab2:
        st.write("Bulk upload rates from CSV file")
        st.info("📋 CSV should have columns: service_category, service_name, amount, unit, remarks")
        
        uploaded_file = st.file_uploader("Choose CSV file", type="csv")
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("📋 Preview:")
            st.dataframe(df.head(), use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                year = st.number_input("📅 Year for these rates", min_value=2020, max_value=2100, value=2024)
            
            with col2:
                rate_type = st.selectbox("🏷️ Rate Type", ["standard", "special", "amended"])
            
            if st.button("✅ Upload Rates", use_container_width=True):
                if db.bulk_upload_rates(
                    df=df,
                    year=year,
                    rate_type=rate_type,
                    created_by=st.session_state.get("user", "admin")
                ):
                    st.rerun()

# ======================= PAGE 4: ADMIN PANEL =======================
elif page == "⚙️ Admin Panel":
    st.subheader("Admin Panel")
    
    # Authentication
    password = st.text_input("🔐 Admin Password", type="password")
    admin_pass = os.getenv("ADMIN_PASSWORD", "admin123")
    
    if password != admin_pass:
        st.warning("⚠️ Please enter correct password to access admin panel")
        st.stop()
    
    st.success("✅ Admin access granted")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["✏️ Update Rate", "📝 Audit Log", "📊 Database Stats"])
    
    # ===== TAB 1: UPDATE RATE =====
    with tab1:
        st.write("Update existing rate and track changes")
        
        years = db.get_all_years()
        if not years:
            st.warning("⚠️ No rates available")
        else:
            selected_year = st.selectbox("📅 Select Year", years, key="update_year")
            
            rates_df = db.get_rates_by_year(selected_year)
            
            if not rates_df.empty:
                # Create selection label
                rates_df['display_label'] = rates_df['service_category'] + " - " + rates_df['service_name']
                
                rate_selection = st.selectbox(
                    "🔍 Select Rate to Update",
                    options=rates_df.index,
                    format_func=lambda x: rates_df.loc[x, 'display_label']
                )
                
                selected_rate = rates_df.loc[rate_selection]
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("💰 Current Amount", f"₹{selected_rate['amount']}")
                    new_amount = st.number_input(
                        "💰 New Amount",
                        value=float(selected_rate['amount']),
                        step=0.01
                    )
                
                with col2:
                    st.metric("⏰ Last Updated", selected_rate['updated_at'][:10])
                    remarks = st.text_area("📝 Update Remarks")
                
                if st.button("✅ Update Rate", use_container_width=True):
                    if db.update_rate(
                        rate_id=selected_rate['id'],
                        amount=new_amount,
                        remarks=remarks,
                        modified_by=st.session_state.get("user", "admin")
                    ):
                        st.success("✅ Rate updated successfully!")
                        st.rerun()
    
    # ===== TAB 2: AUDIT LOG =====
    with tab2:
        st.write("View audit history of rate changes")
        
        years = db.get_all_years()
        if not years:
            st.warning("⚠️ No rates available")
        else:
            selected_year = st.selectbox("📅 Select Year", years, key="audit_year")
            
            rates_df = db.get_rates_by_year(selected_year)
            
            if not rates_df.empty:
                rates_df['display_label'] = rates_df['service_category'] + " - " + rates_df['service_name']
                
                rate_selection = st.selectbox(
                    "🔍 Select Rate for Audit",
                    options=rates_df.index,
                    format_func=lambda x: rates_df.loc[x, 'display_label'],
                    key="audit_select"
                )
                
                selected_rate = rates_df.loc[rate_selection]
                audit_df = db.get_audit_history(selected_rate['id'])
                
                if not audit_df.empty:
                    st.subheader("📝 Audit History")
                    st.dataframe(audit_df, use_container_width=True, hide_index=True)
                else:
                    st.info("ℹ️ No audit history for this rate")
    
    # ===== TAB 3: DATABASE STATS =====
    with tab3:
        st.write("Database statistics and overview")
        
        all_years = db.get_all_years()
        
        if not all_years:
            st.warning("⚠️ No data in database")
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📅 Total Years", len(all_years))
            with col2:
                st.metric("🔢 Years Available", f"{min(all_years)} - {max(all_years)}")
            with col3:
                total_rates = sum(len(db.get_rates_by_year(year)) for year in all_years)
                st.metric("📊 Total Rates", total_rates)
            
            st.markdown("---")
            
            # Stats by year
            st.subheader("📈 Rates by Year")
            year_stats = []
            for year in all_years:
                count = len(db.get_rates_by_year(year))
                year_stats.append({"Year": year, "Number of Rates": count})
            
            if year_stats:
                stats_df = pd.DataFrame(year_stats)
                st.bar_chart(stats_df.set_index("Year"))
                st.dataframe(stats_df, use_container_width=True, hide_index=True)
