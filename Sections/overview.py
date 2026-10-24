# sections/overview.py
import streamlit as st
import plotly.express as px

def render(filtered_df, aggregated_df):
    """
    Renders Section 1: Overview & Global Trends of the Energy Mix.
    """
    
    st.markdown("### 🔍 Overview: Nuclear Dominance Meets the Rise of Renewables")
    st.info(
        "For more than 45 years, Nuclear energy has been the top 1 in electricity production in France."
        "But more recently, other sources of energy are gaining in size and reshaping the energy mix of France elecrticity production."
        "The 2 questions are HOW and WHY. Is it changing fast or slow ? Is it for the fun, or a necessity ?"
    )

    st.warning(
    "**Warning ! Keep this in mind !**: In this analysis, we are talking only about ELECTRICITY production and consumption in France and its different sources." \
    "Every other type of energy consumption, like cars using fuel, or buildings heated with gas instead of electricity, are NOT part of the data"
    )

    if not filtered_df.empty:
        avg_consumption = filtered_df['Consommation (MW)'].mean() if 'Consommation (MW)' in filtered_df.columns else 0.0
        avg_co2_rate = filtered_df['Taux de CO2 (g/kWh)'].mean() if 'Taux de CO2 (g/kWh)' in filtered_df.columns else 0.0
        
        wind_sum = filtered_df['Eolien (MW)'].sum() if 'Eolien (MW)' in filtered_df.columns else 0.0
        solar_sum = filtered_df['Solaire (MW)'].sum() if 'Solaire (MW)' in filtered_df.columns else 0.0
        renewable_volume = wind_sum + solar_sum
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Average Consumption", f"{avg_consumption:,.0f} MW", help="Average grid demand across the selected timeframe")
        metric_col2.metric("Average Carbon Intensity", f"{avg_co2_rate:.1f} g/kWh", help="Estimated CO2 emissions per kWh produced")
        metric_col3.metric("Renewable Output (Wind + Solar)", f"{renewable_volume:,.0f} MW cumulative", help="Combined wind and solar output over the selected period")
    
    st.divider()

    st.subheader("📈 Multi-Year Power Generation Mix (in MW)")
    
    generation_columns = [
        'Nucléaire (MW)', 'Hydraulique (MW)', 'Eolien (MW)', 
        'Solaire (MW)', 'Gaz (MW)', 'Bioénergies (MW)', 'Charbon (MW)', 'Fioul (MW)'
    ]
    
    available_columns = [col for col in generation_columns if col in aggregated_df.columns]
    
    if not available_columns:
        st.warning("No production source data available for visualization.")
        return

    long_format_df = aggregated_df.melt(
        id_vars=['periode'],
        value_vars=available_columns,
        var_name='Filière',
        value_name='Power (MW)'
    )

    column_translation_map = {
        'Nucléaire (MW)': 'Nuclear',
        'Hydraulique (MW)': 'Hydro',
        'Eolien (MW)': 'Wind',
        'Solaire (MW)': 'Solar',
        'Gaz (MW)': 'Gas',
        'Bioénergies (MW)': 'Bioenergy',
        'Charbon (MW)': 'Coal',
        'Fioul (MW)': 'Oil'
    }
    
    long_format_df['Source'] = long_format_df['Filière'].map(column_translation_map).fillna(long_format_df['Filière'])

    color_scheme = {
        'Nuclear': '#2ca02c',
        'Hydro': '#aec7e8',
        'Wind': '#1f77b4',
        'Solar': '#ff7f0e',
        'Gas': '#d62728',
        'Bioenergy': '#98df8a',
        'Coal': '#7f7f7f',
        'Oil': '#c49c94'
    }

    stacked_area_fig = px.area(
        long_format_df,
        x='periode',
        y='Power (MW)',
        color='Source',
        title="Electricity Production Breakdown by Energy Source",
        labels={'periode': 'Time Period', 'Power (MW)': 'Average Power (MW)', 'Source': 'Energy Source'},
        template='plotly_white',
        color_discrete_map=color_scheme
    )
    
    stacked_area_fig.update_layout(
        hovermode="x unified",
        legend_title_text="Energy Sources"
    )
    
    st.plotly_chart(stacked_area_fig, use_container_width=True)



    with st.expander("💡 Click to view comments about the chart"):
        st.markdown("""
        #### Key Observations :
        * **Energy mix** : Nuclear energy is clearly the first source of electricity produced in France by far.
        It is followed by Hydrolic, Wind, Solar and Gas.
        Bioenergy, Coal and Oil are negligeable in size compared to other sources.
        * **Summer/Winter** : There is a peak of production during the winter.
        Carefull, it is not only related to a high demand, but also to a high capacity of production.
        In fact, when people need electricity to heat their buildings, gas is used to produce more.
        Also, during the winter, it is way easier to cool down nuclear plants, while in summer, you cannot cool down as efficiently, so to avoid overheating, you must limit the production.
        Contrarily, in the winter, less sun exposure means less Solar production.
        * **Mix evolution** : one can notice that over the years, production with Coal and Oil is diminishing while production with Solar and Wind is increasing.
        """)