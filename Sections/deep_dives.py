# sections/deep_dives.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render(filtered_df, aggregated_df):
    """
    Renders Section 2: Deep Dive into Carbon Intensity vs. Power Consumption.
    """
    
    st.markdown("### ⚡ Deep Dive: The Hidden Carbon Cost of Electricity Demand")
    st.info(
        "**Key Insight**: While overall power consumption fluctuates seasonally, the carbon intensity "
        "(g/kWh) of the grid can experience sharp spikes during peak winter periods or times of nuclear plant maintenance, "
        "forcing temporary reliance on fossil-fuel backup sources."
    )

    st.divider()

    st.subheader("📊 Grid Demand vs. Carbon Intensity Trends")

    if filtered_df.empty or aggregated_df.empty:
        st.warning("No data available for the selected filters.")
        return

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if 'Consommation (MW)' in aggregated_df.columns:
        fig.add_trace(
            go.Scatter(
                x=aggregated_df['periode'],
                y=aggregated_df['Consommation (MW)'],
                name="Grid Consumption (MW)",
                line=dict(color="#1f77b4", width=2)
            ),
            secondary_y=False,
        )

    if 'Taux de CO2 (g/kWh)' in aggregated_df.columns:
        fig.add_trace(
            go.Scatter(
                x=aggregated_df['periode'],
                y=aggregated_df['Taux de CO2 (g/kWh)'],
                name="Carbon Intensity (g/kWh)",
                line=dict(color="#d62728", width=2, dash="dot")
            ),
            secondary_y=True,
        )

    fig.update_layout(
        title="Relationship Between Total Electricity Demand and Carbon Emissions",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_xaxes(title_text="Time Period")
    fig.update_yaxes(title_text="<b>Power Consumption</b> (MW)", secondary_y=False)
    fig.update_yaxes(title_text="<b>Carbon Intensity</b> (g/kWh)", secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)


    with st.expander("💡 Click to view comments about the chart"):
        st.markdown("""
        #### Key Observations :
        * This graph shows that the Carbon emmissions are very dependent ont he production method more than the consumption itself.
        In fact, the peak of carbon emmissions in 2022 is due to a maintenance of nuclear plants in France, while the power consumption was low.

        """)






    st.subheader("❄️ Winter Peak Season Demand Trend (Nov 1st – May 1st)")
    
    if filtered_df.empty or 'datetime' not in filtered_df.columns:
        st.warning("No datetime data available to perform winter analysis.")
        return

    df_winter = filtered_df.copy()
    df_winter['Consommation (MW)'] = pd.to_numeric(df_winter['Consommation (MW)'], errors='coerce')
    df_winter = df_winter.dropna(subset=['datetime', 'Consommation (MW)'])

    
    def assign_winter_season(row):
        date = row['datetime']
        month = date.month
        year = date.year
        
        if month in [11, 12]:
            return f"{year}-{year + 1}"
        elif month in [1, 2, 3, 4]:
            return f"{year - 1}-{year}"
        elif month == 5 and date.day == 1:
            return f"{year - 1}-{year}"
        else:
            return None

    df_winter['Winter_Season'] = df_winter.apply(assign_winter_season, axis=1)
    
    df_winter = df_winter.dropna(subset=['Winter_Season'])

    if df_winter.empty:
        st.info("No winter season data (Nov 1st - May 1st) found in the selected range.")
        return

    df_winter['Date_Day'] = df_winter['datetime'].dt.date
    daily_winter = df_winter.groupby(['Winter_Season', 'Date_Day'])['Consommation (MW)'].mean().reset_index()

    seasonal_winter_avg = daily_winter.groupby('Winter_Season')['Consommation (MW)'].mean().reset_index()
    seasonal_winter_avg.columns = ['Winter Season', 'Average Daily Consumption (MW)']

    seasonal_winter_avg = seasonal_winter_avg.sort_values('Winter Season')

    fig_winter = px.line(
        seasonal_winter_avg,
        x='Winter Season',
        y='Average Daily Consumption (MW)',
        markers=True,
        title="Average Daily Grid Consumption During Winter Period (Nov 1st – May 1st)",
        labels={
            'Winter Season': 'Winter Season (Nov–May)',
            'Average Daily Consumption (MW)': 'Average Daily Power Demand (MW)'
        },
        template='plotly_white'
    )

    fig_winter.update_traces(
        line=dict(color='#d62728', width=3),
        marker=dict(size=8, color='#8c564b')
    )

    fig_winter.update_layout(
        hovermode="x unified",
        yaxis=dict(title="<b>Average Daily Demand</b> (MW)")
    )

    st.plotly_chart(fig_winter, use_container_width=True)

    with st.expander("💡 Click to view Winter Season Analysis"):
        st.markdown("""
        #### Key Observations & Energy Insights:
        * The main purpose of this graph is to show decreasing tendency of power consumption during the winter period.
        * **Why ?** : Winters are getting **warmer** and **shorter**.
        * **What it means** : Every consumption that is related to winter will decrease as the winters tend to disappear.
        * If we push this to an extreme scenario, with no winter and only summers, nuclear production will never be high and
        over-heating problems will happen way more frequently, forcing some facilities to stop for a while. On the other hand,
        Solar energy will have no stop to its production, and people will no longer need to heat their homes or have any other
        consumption need related to winter and cold temperaturres.
        """)