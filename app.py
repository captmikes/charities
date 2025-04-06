import streamlit as st
import pandas as pd
import math

# --- Page Configuration ---
st.set_page_config(
    page_title="CharityCard.World",
    page_icon="❤️",
    layout="wide",
)

# --- Data Loading ---
@st.cache_data
def load_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
        df.fillna("N/A", inplace=True)
        for col in ['Organisation_Name', 'Short_Description', 'Website_URL',
                    'Contact_Name', 'Phone', 'Email', 'Category_Focus']:
            if col in df.columns:
                df[col] = df[col].astype(str)
        return df
    except FileNotFoundError:
        st.error(f"Error: File '{csv_path}' not found.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# --- Load the dataset ---
DATA_FILE = 'charities.csv'
df = load_data(DATA_FILE)

# --- UI Layout ---
st.title("CharityCard.World")
st.write("Find and explore charitable organizations easily.")

if df is not None:
    # --- Filters / Search ---
    st.subheader("Search & Filter")
    search_term = st.text_input("Search (name, description, etc.)")
    
    causes = sorted(list(df['Category'].unique()))
    selected_causes = st.multiselect("Cause", causes, default=[])

    countries = sorted(list(df['Country'].unique()))
    selected_countries = st.multiselect("Country", countries, default=[])

    # --- Apply Filters ---
    df_filtered = df.copy()

    # Text Search
    if search_term:
        search_cols = ['Organisation_Name', 'Short_Description', 'Category_Focus']
        term = search_term.lower()
        df_filtered = df_filtered[
            df_filtered[search_cols].apply(
                lambda row: row.str.lower().str.contains(term, na=False).any(), axis=1
            )
        ]

    # Cause Filter
    if selected_causes:
        df_filtered = df_filtered[df_filtered['Category'].isin(selected_causes)]

    # Country Filter
    if selected_countries:
        df_filtered = df_filtered[df_filtered['Country'].isin(selected_countries)]

    # --- Display Title & Count ---
    total_orgs = len(df_filtered)
    st.subheader(f"All Charities ({total_orgs})")

    # --- Pagination Setup ---
    items_per_page = 10
    total_pages = max(1, math.ceil(total_orgs / items_per_page))
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_data = df_filtered.iloc[start_idx:end_idx]

    # --- Display in 'Tiles' (2 columns x 5 rows = 10 tiles per page) ---
    if not page_data.empty:
        # Break page_data into chunks of 2 for 2-column layout
        for i in range(0, len(page_data), 2):
            cols = st.columns(2)
            for col_index, item_index in enumerate(range(i, min(i+2, len(page_data)))):
                row = page_data.iloc[item_index]
                with cols[col_index]:
                    st.markdown(f"### {row.get('Organisation_Name', 'No Name')}")
                    st.write(f"**Category**: {row.get('Category', 'N/A')}")
                    st.write(f"**Country**: {row.get('Country', 'N/A')}")
                    st.write(f"**Notes**: {row.get('Short_Description', 'N/A')}")
                    website = row.get('Website_URL', 'N/A')
                    if website.lower().startswith('http'):
                        st.markdown(f"[Website]({website})")
                    else:
                        st.write(f"Website: {website}")
                    email = row.get('Email', 'N/A')
                    phone = row.get('Phone', 'N/A')
                    st.write(f"**Email**: {email}")
                    st.write(f"**Phone**: {phone}")
                    st.markdown("---")
    else:
        st.warning("No organisations match your current filters.")

    # --- Pagination Footer (e.g., "<1, 2, 3, ...>") ---
    st.write(f"Page {page} of {total_pages}")

    # --- Optional: Show Raw Data ---
    with st.expander("Show Raw Filtered Data Table"):
        st.dataframe(df_filtered, use_container_width=True)

else:
    st.warning("Could not load charity data. Check the CSV file.")

st.markdown("---")
st.info("Edit `charities.csv` to add or modify data.")
