# sections/trade.py
import streamlit as st
import plotly.express as px

def render(filtered_df, aggregated_df):
    """
    Renders Section 3: European Electricity Grid Interconnections & Trade Flows.
    """
    
    st.markdown("### 🌐 European Grid Interconnection & Cross-Border Flows")
    st.info(
        "**Key Insight**: France acts as a central hub in the European power grid. "
        "Analyzing commercial exchanges with neighboring countries reveals how cross-border trade "
        "helps balance supply and demand while reinforcing regional energy security."
    )

    st.divider()

    trade_columns = [
        'Ech. comm. Angleterre (MW)',
        'Ech. comm. Espagne (MW)',
        'Ech. comm. Italie (MW)',
        'Ech. comm. Suisse (MW)',
        'Ech. comm. Allemagne-Belgique (MW)'
    ]
    
    available_trade_cols = [col for col in trade_columns if col in aggregated_df.columns]

    if not available_trade_cols:
        st.warning("No commercial trade data available for the selected time range.")
        return

    country_translation_map = {
        'Ech. comm. Angleterre (MW)': 'United Kingdom',
        'Ech. comm. Espagne (MW)': 'Spain',
        'Ech. comm. Italie (MW)': 'Italy',
        'Ech. comm. Suisse (MW)': 'Switzerland',
        'Ech. comm. Allemagne-Belgique (MW)': 'Germany & Belgium'
    }


    

    st.subheader("📈 Cross-Border Trade Dynamics Over Time")

    long_trade_df = aggregated_df.melt(
        id_vars=['periode'],
        value_vars=available_trade_cols,
        var_name='Border_Column',
        value_name='Flow_MW'
    )
    
    long_trade_df['Partner'] = long_trade_df['Border_Column'].map(country_translation_map)

    fig_trade_line = px.line(
        long_trade_df,
        x='periode',
        y='Flow_MW',
        color='Partner',
        title="Temporal Evolution of Interconnector Power Exchanges",
        labels={'periode': 'Time Period', 'Flow_MW': 'Exchange Volume (MW)', 'Partner': 'Border Interconnector'},
        template='plotly_white'
    )

    fig_trade_line.update_layout(hovermode="x unified")
    st.plotly_chart(fig_trade_line, use_container_width=True)



    with st.expander("💡 Click to view comments about the chart"):
            st.markdown("""
            Note : a negative value means an export (energy leaving France). A positive value means an import (energy entering France)
            #### Key Observations :
            * This graph proves that France is a huge exportating country in energy. The nuclear plant incident in 2022 is
            clearly visible here. 
            """)