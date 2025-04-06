import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Charity Organisation Directory",
    page_icon="❤️",
    layout="wide",  # Use wide layout for better table display
)

# --- Data Loading ---
# Use caching to load data only once
@st.cache_data
def load_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
        # Basic cleaning: Fill missing values with 'N/A' for display
        df.fillna("N/A", inplace=True)
        # Ensure consistent types for columns expected to be strings
        for col in ['Organisation_Name', 'Short_Description', 'Website_URL', 'Contact_Name', 'Phone', 'Email']:
             if col in df.columns:
                  df[col] = df[col].astype(str)
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{csv_path}' was not found. Make sure it's in the same directory as the script.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return None

# Load the dataset
DATA_FILE = 'charities.csv'
df = load_data(DATA_FILE)

# --- App UI ---
st.title("❤️ Charity Organisation Directory")
st.write("Browse and filter the list of charitable organisations.")

if df is not None:
    # --- Sidebar Filters ---
    st.sidebar.header("Filters")

    # Text search (searches across multiple relevant fields)
    search_term = st.sidebar.text_input("Search by Name, Description, etc.")

    # Category Filter
    all_categories = sorted(df['Category'].unique())
    selected_categories = st.sidebar.multiselect("Filter by Category", all_categories, default=[])

    # Country Filter
    all_countries = sorted(df['Country'].unique())
    selected_countries = st.sidebar.multiselect("Filter by Country", all_countries, default=[])

    # --- Filtering Logic ---
    df_filtered = df.copy() # Start with the full dataframe

    # Apply text search filter
    if search_term:
        # Search in Organisation Name, Short Description, and Category Focus
        search_cols = ['Organisation_Name', 'Short_Description', 'Category_Focus']
        # Ensure search term is treated as lowercase for case-insensitive search
        term = search_term.lower()
        # Apply search across selected columns
        df_filtered = df_filtered[
            df_filtered[search_cols].apply(
                lambda row: row.str.lower().str.contains(term, na=False).any(), axis=1
            )
        ]

    # Apply category filter
    if selected_categories:
        df_filtered = df_filtered[df_filtered['Category'].isin(selected_categories)]

    # Apply country filter
    if selected_countries:
        df_filtered = df_filtered[df_filtered['Country'].isin(selected_countries)]

    # --- Display Results ---
    st.header(f"Displaying {len(df_filtered)} Organisations")

    if df_filtered.empty:
        st.warning("No organisations match your current filters.")
    else:
        # Define which columns to display initially (can be adjusted)
        columns_to_display = [
            'Organisation_Name',
            'Category',
            'Country',
            'Short_Description',
            'Website_URL',
            'Email',
            'Phone'
        ]
        # Filter the dataframe to only include columns that actually exist
        columns_to_display = [col for col in columns_to_display if col in df_filtered.columns]

        st.dataframe(
            df_filtered[columns_to_display],
            hide_index=True, # Don't show the pandas index
            use_container_width=True, # Use full width
            # Optional: Configure specific columns (e.g., make URL clickable)
            column_config={
                 "Website_URL": st.column_config.LinkColumn(
                    "Website",
                    help="Click to visit the organisation's website",
                    display_text="Visit 🔗" # Text to display in the cell
                 )
            }
        )

    # --- Optional: Show Raw Data ---
    with st.expander("Show Raw Filtered Data Table"):
         st.dataframe(df_filtered, use_container_width=True)

else:
    st.warning("Could not load charity data. Please check the `charities.csv` file.")

st.sidebar.markdown("---")
st.sidebar.info("Add more data by editing the `charities.csv` file.")
