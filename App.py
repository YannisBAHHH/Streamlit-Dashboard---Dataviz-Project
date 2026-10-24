# app.py
import streamlit as st
import pandas as pd
from Sections import overview, deep_dives, trade, simulations

st.set_page_config(
    page_title="France Electricity Mix Dashboard",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Data Storytelling: Energy Transition in France")
st.caption("Source: RTE éCO2mix Consolidated Data (data.gouv.fr)")


@st.cache_data(show_spinner=True)
def load_data():
    df = pd.read_csv("data/eco2mix-national-cons-def.csv", sep=";")
    
    df = df.drop(columns=['Date', 'Heure'], errors='ignore')

    df['datetime'] = pd.to_datetime(df['Date et Heure'], errors='coerce')
    
    df['annee'] = df['datetime'].dt.year
    
    production_cols = [
        'Nucléaire (MW)', 'Eolien (MW)', 'Solaire (MW)', 
        'Hydraulique (MW)', 'Gaz (MW)', 'Charbon (MW)', 
        'Fioul (MW)', 'Bioénergies (MW)'
    ]

    other_metric_cols = ['Consommation (MW)', 'Taux de CO2 (g/kWh)']

    trade_cols = [
        'Ech. comm. Angleterre (MW)',
        'Ech. comm. Espagne (MW)',
        'Ech. comm. Italie (MW)',
        'Ech. comm. Suisse (MW)',
        'Ech. comm. Allemagne-Belgique (MW)',
        'Ech. physiques (MW)'
    ]


    all_numeric_columns = production_cols + other_metric_cols + trade_cols
    
    for col in all_numeric_columns:
        if col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = 0.0
            
    return df, production_cols



try:
    raw_df, production_columns = load_data()
except Exception as execution_error:
    st.error(f"Error loading dataset: {execution_error}. Please verify file path in 'data/' directory.")
    st.stop()

with st.sidebar:
    st.header("⚙️ Display Settings")
    
    available_years = sorted(raw_df['annee'].dropna().unique())
    if available_years:
        min_year, max_year = int(min(available_years)), int(max(available_years))
        selected_year_range = st.slider("Year Range", min_year, max_year, (min_year, max_year))
    else:
        st.error("No valid years found in the dataset.")
        st.stop()
        
    time_frequency = st.selectbox(
        "Time Aggregation Level",
        options=["Month", "Year", "Day"],
        index=0,
        help="Aggregates data over time to smooth out high-frequency fluctuations and optimize rendering."
    )

filtered_df = raw_df[
    (raw_df['annee'] >= selected_year_range[0]) & 
    (raw_df['annee'] <= selected_year_range[1])
].copy()

if time_frequency == "Month":
    filtered_df['periode'] = filtered_df['datetime'].dt.to_period("M").dt.to_timestamp()
elif time_frequency == "Year":
    filtered_df['periode'] = filtered_df['datetime'].dt.to_period("Y").dt.to_timestamp()
else:
    filtered_df['periode'] = filtered_df['datetime'].dt.date


trade_columns_list = [
    'Ech. comm. Angleterre (MW)',
    'Ech. comm. Espagne (MW)',
    'Ech. comm. Italie (MW)',
    'Ech. comm. Suisse (MW)',
    'Ech. comm. Allemagne-Belgique (MW)',
    'Ech. physiques (MW)'
]

numeric_cols = production_columns + ['Consommation (MW)', 'Taux de CO2 (g/kWh)'] + trade_columns_list
available_numeric_cols = [c for c in numeric_cols if c in filtered_df.columns]
aggregated_df = filtered_df.groupby('periode')[available_numeric_cols].mean().reset_index()



overview.render(filtered_df, aggregated_df)


st.divider()
deep_dives.render(filtered_df, aggregated_df)


st.divider()
trade.render(filtered_df, aggregated_df)


st.divider()
simulations.render(filtered_df, aggregated_df)