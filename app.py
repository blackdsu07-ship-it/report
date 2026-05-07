import streamlit as st
import pandas as pd
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Offer Filter",
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
    --danger: #ff5e5e;
    --warn: #ffa947;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
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
    font-weight: 700;
    color: var(--text);
    margin: 0;
}

.metric-row {
    display: flex;
    gap: 14px;
    margin-bottom: 24px;
}
.metric-card {
    flex: 1;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.metric-label {
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 28px;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
    color: var(--accent);
}

.offer-block {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 18px;
}
.offer-title {
    font-family: 'Space Mono', monospace;
    font-size: 14px;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.offer-title .match-badge {
    font-size: 10px;
    background: var(--accent2);
    color: #fff;
    padding: 2px 8px;
    border-radius: 20px;
    font-weight: 400;
    letter-spacing: 0.5px;
}
.no-data {
    color: var(--muted);
    font-size: 13px;
    font-style: italic;
}
.last-conv-yes {
    color: var(--accent);
    font-weight: 600;
}
.last-conv-no {
    color: var(--danger);
    font-weight: 600;
}

div[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 10px !important;
    padding: 10px !important;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextInput"] textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 13px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,229,160,0.15) !important;
}
.stCheckbox label {
    color: var(--text) !important;
    font-size: 13px !important;
}
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    overflow: hidden;
}
div[data-testid="stDataFrame"] * {
    font-family: 'DM Sans', sans-serif !important;
}
.stAlert {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
label[data-testid="stWidgetLabel"] p {
    color: var(--muted) !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-family: 'Space Mono', monospace !important;
}
h3 { color: var(--text) !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div><div class="badge">ANALYTICS</div></div>
    <h1>🎯 Offer Filter Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# ── File upload ───────────────────────────────────────────────────────────────
file = st.file_uploader("Upload your CSV file", type=["csv"])

if file:
    df = pd.read_csv(file)

    # ── Data processing ──────────────────────────────────────────────────────
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce', dayfirst=True)
    df['CONVERSION'] = pd.to_numeric(df['CONVERSION'], errors='coerce')

    today = pd.Timestamp('2026-05-07')

    # "Days ago" column
    df['DAYS_AGO'] = (today - df['DATE']).dt.days

    # Base filter: conversion >= 1 only (date threshold is now a checkbox)
    filtered_conversion_data = df[df['CONVERSION'] >= 1].copy()

    # Find max date per DATA+OFFER pair across full df
    max_dates = df.groupby(['DATA', 'OFFER'])['DATE'].max().reset_index()
    latest = pd.merge(df, max_dates, on=['DATA', 'OFFER', 'DATE'])

    # Pairs where latest row has conversion >= 1  →  "last converted = YES"
    last_converted_pairs = set(
        latest[latest['CONVERSION'] >= 1][['DATA', 'OFFER']]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )

    # Add last-converted flag to filtered data
    filtered_conversion_data['LAST_CONVERTED'] = (
        filtered_conversion_data[['DATA', 'OFFER']]
        .apply(tuple, axis=1)
        .isin(last_converted_pairs)
    )

    keep_pairs = list(last_converted_pairs)
    final_filtered = filtered_conversion_data[
        filtered_conversion_data[['DATA', 'OFFER']].apply(tuple, axis=1).isin(keep_pairs)
    ]

    # ── Metrics row ──────────────────────────────────────────────────────────
    total_rows = len(final_filtered)
    unique_offers = final_filtered['OFFER'].nunique() if not final_filtered.empty else 0
    last_conv_count = int(final_filtered['LAST_CONVERTED'].sum()) if not final_filtered.empty else 0
    avg_days = round(final_filtered['DAYS_AGO'].mean(), 1) if not final_filtered.empty else "—"

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-label">Total Rows</div>
            <div class="metric-value">{total_rows}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Unique Offers</div>
            <div class="metric-value">{unique_offers}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Last Converted</div>
            <div class="metric-value">{last_conv_count}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Avg Days Ago</div>
            <div class="metric-value">{avg_days}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Filter controls ───────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        offer_input = st.text_input(
            "Search offers (partial name, comma-separated)",
            placeholder="e.g.  summer, promo2024, deal"
        )
    with col2:
        days_filter = st.number_input(
            "Last N days",
            min_value=1,
            max_value=365,
            value=None,
            step=1,
            placeholder="e.g. 5",
            help="Show only rows where DAYS_AGO <= N"
        )
    with col3:
        exclude_days = st.number_input(
            "Exclude last N days",
            min_value=1,
            max_value=365,
            value=None,
            step=1,
            placeholder="e.g. 10",
            help="Exclude rows from the most recent N days (DATE <= today − N)"
        )
    with col4:
        only_last_converted = st.checkbox("✅ Last Converted Only", value=False)

    # ── Apply filters ─────────────────────────────────────────────────────────
    display_df = final_filtered.copy()

    # Exclude last N days filter
    if exclude_days is not None:
        date_threshold = today - pd.Timedelta(days=int(exclude_days))
        display_df = display_df[display_df['DATE'] <= date_threshold]

    # Last N days filter
    if days_filter is not None:
        display_df = display_df[display_df['DAYS_AGO'] <= int(days_filter)]

    # Last converted filter
    if only_last_converted:
        display_df = display_df[display_df['LAST_CONVERTED'] == True]

    # ── Column order ──────────────────────────────────────────────────────────
    def style_df(df_in):
        cols = list(df_in.columns)
        priority = ['OFFER', 'DATA', 'DATE', 'DAYS_AGO', 'CONVERSION', 'LAST_CONVERTED']
        ordered = [c for c in priority if c in cols] + [c for c in cols if c not in priority]
        return df_in[ordered]

    col_config = {
        "DAYS_AGO": st.column_config.NumberColumn(
            "Days Ago",
            help="How many days before today the conversion happened",
            format="%d days",
        ),
        "DATE": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
        "LAST_CONVERTED": st.column_config.CheckboxColumn("Last Conv?"),
        "CONVERSION": st.column_config.NumberColumn("Conversion", format="%.0f"),
    }

    # ── Results ───────────────────────────────────────────────────────────────
    if offer_input:
        search_terms = [x.strip().lower() for x in offer_input.split(",") if x.strip()]

        for term in search_terms:
            matched = display_df[display_df['OFFER'].str.lower().str.contains(term, na=False)]
            matched_offers = matched['OFFER'].unique()

            st.markdown(f"""
            <div class="offer-block">
                <div class="offer-title">
                    🔍 "{term}"
                    <span class="match-badge">{len(matched_offers)} match{'es' if len(matched_offers) != 1 else ''}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if matched.empty:
                st.markdown('<p class="no-data">No results found for this search term.</p>', unsafe_allow_html=True)
            else:
                for offer_name in matched_offers:
                    offer_rows = matched[matched['OFFER'] == offer_name]
                    is_last = offer_rows['LAST_CONVERTED'].iloc[0]

                    badge_html = (
                        '<span class="last-conv-yes">● Last Converted</span>'
                        if is_last else
                        '<span class="last-conv-no">○ Not Last Converted</span>'
                    )

                    st.markdown(f"""
                    <div style="margin: 10px 0 4px; font-size:13px; font-family:'Space Mono',monospace;">
                        <strong style="color:#e8eaf0">{offer_name}</strong>&nbsp;&nbsp;{badge_html}
                    </div>
                    """, unsafe_allow_html=True)

                    st.dataframe(style_df(offer_rows), use_container_width=True,
                                 hide_index=True, column_config=col_config)
    else:
        st.subheader("All Filtered Data")
        if display_df.empty:
            st.info("No data matches the current filters.")
        else:
            st.dataframe(style_df(display_df), use_container_width=True,
                         hide_index=True, column_config=col_config)
else:
    st.markdown("""
    <div style="text-align:center; padding: 60px 20px; color: #6b7280;">
        <div style="font-size: 48px; margin-bottom: 12px;">📂</div>
        <div style="font-family: 'Space Mono', monospace; font-size: 14px; letter-spacing: 1px;">
            Upload a CSV to get started
        </div>
    </div>
    """, unsafe_allow_html=True)
