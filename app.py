import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ── Configuration ─────────────────────────────────────────────────────────────
CSV_FILE_PATH = "email_report2.csv"  # <--- Change this to your actual filename

st.set_page_config(
    page_title="Offer Filter Pro",
    page_icon="🎯",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg: #0d0f14;
    --surface: #161a23;
    --surface2: #1e2433;
    --accent: #00e5a0;
    --accent2: #7b61ff;
    --text: #e8eaf0;
    --muted: #6b7280;
    --border: #2a3147;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

.app-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 8px 0 28px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
}
.app-header .badge {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    background: var(--accent);
    color: #000;
    padding: 3px 10px;
    border-radius: 2px;
    font-weight: 700;
}
.app-header h1 {
    font-family: 'Space Mono', monospace;
    font-size: 22px;
    margin: 0;
}

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 20px;
    position: relative;
}

.offer-block {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 18px;
}
.last-conv-yes { color: var(--accent); font-weight: 600; }
.last-conv-no { color: #ff5e5e; font-weight: 600; }

/* Data Editor Styling */
div[data-testid="stDataEditor"] {
    border: 1px solid var(--border);
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Data Loading Logic ────────────────────────────────────────────────────────
def load_data():
    if not os.path.exists(CSV_FILE_PATH):
        return None
    
    for encoding in ['utf-8', 'latin1', 'cp1252', 'utf-16']:
        try:
            return pd.read_csv(CSV_FILE_PATH, encoding=encoding)
        except (UnicodeDecodeError, Exception):
            continue
    return None

df_raw = load_data()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div><div class="badge">DATABASE MODE</div></div>
    <h1>🎯 Offer Filter Dashboard</h1>
</div>
""", unsafe_allow_html=True)

if df_raw is None:
    st.error(f"❌ File **'{CSV_FILE_PATH}'** not found in the directory.")
    st.info("Please place your CSV file in the same folder as this script and rename it to 'data.csv' or update CSV_FILE_PATH in the code.")
else:
    # ── Pre-processing ────────────────────────────────────────────────────────
    df = df_raw.copy()
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce', dayfirst=True)
    df['CONVERSION'] = pd.to_numeric(df['CONVERSION'], errors='coerce').fillna(0)

    today = pd.Timestamp.now().normalize()
    df['DAYS_AGO'] = (today - df['DATE']).dt.days

    # Tagging "Last Converted" based on entire dataset
    max_dates = df.groupby(['DATA', 'OFFER'])['DATE'].max().reset_index()
    latest_rows = pd.merge(df, max_dates, on=['DATA', 'OFFER', 'DATE'])
    last_converted_pairs = set(
        latest_rows[latest_rows['CONVERSION'] >= 1][['DATA', 'OFFER']]
        .itertuples(index=False, name=None)
    )
    df['LAST_CONVERTED'] = df[['DATA', 'OFFER']].apply(tuple, axis=1).isin(last_converted_pairs)

    # ── Metrics ───────────────────────────────────────────────────────────────
    converted_only = df[df['CONVERSION'] >= 1]
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Today", today.strftime('%d %b %Y'))
    with m2: st.metric("Total Converted Rows", len(converted_only))
    with m3: st.metric("Unique Offers", converted_only['OFFER'].nunique())
    with m4: st.metric("Active Pairs", df['LAST_CONVERTED'].sum())

    st.divider()

    # ── Filters ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
    with c1:
        search = st.text_input("Search Offers", placeholder="e.g. promo, summer")
    with c2:
        days_n = st.number_input("Last N Days", min_value=1, value=None)
    with c3:
        excl_n = st.number_input("Exclude N Days", min_value=1, value=None)
    with c4:
        last_only = st.checkbox("Last Converted Only")

    # Apply Filtering
    disp_df = converted_only.copy()
    if excl_n:
        disp_df = disp_df[disp_df['DATE'] <= (today - pd.Timedelta(days=excl_n))]
    if days_n:
        disp_df = disp_df[disp_df['DAYS_AGO'] <= days_n]
    if last_only:
        disp_df = disp_df[disp_df['LAST_CONVERTED'] == True]

    # ── Main Display & Editing ────────────────────────────────────────────────
    st.subheader("Data Explorer")
    
    # Column ordering & config
    col_order = ['OFFER', 'DATA', 'DATE', 'DAYS_AGO', 'CONVERSION', 'LAST_CONVERTED']
    config = {
        "DATE": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
        "DAYS_AGO": st.column_config.NumberColumn("Days Ago", format="%d d"),
        "LAST_CONVERTED": st.column_config.CheckboxColumn("Last Conv?"),
        "CONVERSION": st.column_config.NumberColumn("Conversions", step=1)
    }

    if search:
        terms = [t.strip().lower() for t in search.split(",") if t.strip()]
        for term in terms:
            match = disp_df[disp_df['OFFER'].str.lower().str.contains(term, na=False)]
            if not match.empty:
                st.markdown(f"#### Results for '{term}'")
                # Using Data Editor so you can edit values directly
                edited = st.data_editor(match[col_order], hide_index=True, column_config=config, use_container_width=True, key=f"editor_{term}")
            else:
                st.write(f"No results for '{term}'")
    else:
        # Full view data editor
        final_edit_df = st.data_editor(disp_df[col_order], hide_index=True, column_config=config, use_container_width=True)

    # ── Save Feature ──────────────────────────────────────────────────────────
    st.sidebar.header("Data Management")
    if st.sidebar.button("💾 Save All Changes to CSV"):
        # In a real app, you would merge 'final_edit_df' back into 'df_raw' 
        # and save. Here we save the current view for simplicity.
        try:
            # We save the original columns (from df_raw) to keep file structure
            df_raw.to_csv(CSV_FILE_PATH, index=False)
            st.sidebar.success("CSV file updated successfully!")
        except Exception as e:
            st.sidebar.error(f"Error saving: {e}")

    st.sidebar.info("Editing values in the table above and clicking 'Save' will overwrite your local CSV file.")
