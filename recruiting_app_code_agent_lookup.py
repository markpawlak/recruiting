import streamlit as st
import pandas as pd

# 1. App Configuration - Optimized for Mobile
st.set_page_config(
    page_title="Wendy's Recruit Tracker",
    page_icon="📱",
    layout="centered"
)

# Custom CSS for high-contrast mobile readability
st.markdown("""
    <style>
    .agent-card {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 20px;
    }
    .metric-label { font-size: 14px; color: #555; }
    .metric-value { font-size: 20px; font-weight: bold; color: #000; }
    </style>
    """, unsafe_index=True)

# 2. Data Loading Function
@st.cache_data
def load_data():
    # Loading the combined file created in the previous step
    df = pd.read_csv('Combined_Recruits.csv')
    
    # Ensure numeric types for calculations
    df['LTM Sales Volume'] = pd.to_numeric(df['LTM Sales Volume'], errors='coerce')
    df['Units'] = pd.to_numeric(df['Units'], errors='coerce')
    
    # Function to back-calculate Previous Year Volume from the Growth % string
    def calculate_prev_year_volume(current_vol, growth_str):
        try:
            if pd.isna(growth_str) or growth_str == "0%":
                return current_vol
            # Convert string like "445%" or "1,374%" to float 4.45 or 13.74
            clean_growth = float(str(growth_str).replace('%', '').replace(',', '')) / 100
            # Formula: Current / (1 + Growth Rate)
            return current_vol / (1 + clean_growth)
        except:
            return 0

    # Apply calculations and create search field
    df['Prev Year Vol'] = df.apply(lambda x: calculate_prev_year_volume(x['LTM Sales Volume'], x['LTM Sales Volume % Growth']), axis=1)
    df['Full Name'] = df['First Name'].fillna('') + " " + df['Last Name'].fillna('')
    
    return df

# Initialize data
try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading CSV: {e}. Please ensure 'Combined_Recruits.csv' is in the repository.")
    st.stop()

# 3. Mobile Header UI
st.title("📱 Recruit Directory")
st.write("Enter an agent's name to view their production profile.")

# 4. Search Bar
search_input = st.text_input("Search Agents", placeholder="Start typing a name...")

# 5. Result Display Logic
if search_input:
    # Search across the "Full Name" column 
    results = df[df['Full Name'].str.contains(search_input, case=False, na=False)]
    
    if not results.empty:
        st.success(f"Found {len(results)} agent(s)")
        
        for index, row in results.iterrows():
            with st.container():
                # Agent Header [cite: 1]
                st.subheader(f"👤 {row['Full Name']}")
                
                # Office Info [cite: 1, 19]
                st.markdown(f"**Office:** {row['Current Office']} — *{row['Office City']}*")
                
                # Geographic Info [cite: 13]
                st.markdown(f"**Primary Market:** {row['Most Transacted City']}")
                
                # Performance Metrics [cite: 11, 17, 12]
                m1, m2 = st.columns(2)
                with m1:
                    st.metric("LTM Sales Volume", f"${row['LTM Sales Volume']:,.0f}")
                    st.metric("Prev. Year Volume", f"${row['Prev Year Vol']:,.0f}")
                
                with m2:
                    st.metric("LTM Units", f"{row['Units']}")
                    st.metric("Volume Growth", f"{row['LTM Sales Volume % Growth']}")

                # Interactive Contact Links 
                c1, c2 = st.columns(2)
                if pd.notna(row['Phone']) and str(row['Phone']).lower() != 'none':
                    c1.markdown(f"📞 [**Call Agent**](tel:{row['Phone']})")
                
                if pd.notna(row['Email']):
                    c2.markdown(f"📧 [**Email Agent**](mailto:{row['Email']})")
                
                st.divider()
    else:
        st.warning("No recruits found matching that name.")
else:
    # Display quick stats for Wendy when the search is empty
    st.info("💡 Pro-tip: You can search by first or last name.")
    st.write(f"Total Database Size: {len(df)} Recruits")
