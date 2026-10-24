# sections/simulations.py
import streamlit as st
import plotly.graph_objects as go

def render(filtered_df, aggregated_df):
    """
    Renders Section 4: Interactive What-If Scenario Simulator for Grid Decarbonization.
    """
    
    st.markdown("### 🔮 Interactive What-If Simulator: Exploring Decarbonization Pathways")
    st.info(
        "**Key Insight**: Energy policy and individual behavior directly shape grid outcomes. "
        "Use the controls below to simulate changes in electricity demand (sobriety) "
        "and renewable capacity expansion to estimate potential annual $CO_2$ emissions savings."
    )

    st.divider()

    if filtered_df.empty:
        st.warning("No data available for simulation under current filters.")
        return

    base_consumption_mw = filtered_df['Consommation (MW)'].mean() if 'Consommation (MW)' in filtered_df.columns else 0.0
    base_co2_rate = filtered_df['Taux de CO2 (g/kWh)'].mean() if 'Taux de CO2 (g/kWh)' in filtered_df.columns else 0.0

    HOURS_IN_YEAR = 8760
    base_annual_mwh = base_consumption_mw * HOURS_IN_YEAR
    base_annual_co2_tonnes = (base_annual_mwh * base_co2_rate) / 1000.0

    st.subheader("⚙️ Scenario Parameters")
    
    col_input1, col_input2 = st.columns(2)

    with col_input1:
        demand_change_pct = st.slider(
            "Overall Demand Reduction (%)",
            min_value=-30,
            max_value=30,
            value=-10,
            step=1,
            help="Simulate energy sobriety policies or electrification growth (negative values = reduction)."
        )

    with col_input2:
        renewable_boost_pct = st.slider(
            "Renewable Capacity Boost (%)",
            min_value=0,
            max_value=100,
            value=25,
            step=5,
            help="Simulate accelerated solar and wind development offsetting fossil generation."
        )

    simulated_annual_mwh = base_annual_mwh * (1 + (demand_change_pct / 100.0))

    solar_mean = filtered_df['Solaire (MW)'].mean() if 'Solaire (MW)' in filtered_df.columns else 0.0
    wind_mean = filtered_df['Eolien (MW)'].mean() if 'Eolien (MW)' in filtered_df.columns else 0.0
    
    current_renewable_mw = solar_mean + wind_mean
    boosted_renewable_mw = current_renewable_mw * (1 + (renewable_boost_pct / 100.0))
    additional_green_mw = boosted_renewable_mw - current_renewable_mw

    fossil_displacement_factor = 0.400
    emissions_offset_from_renewables = (additional_green_mw * HOURS_IN_YEAR) * fossil_displacement_factor

    simulated_co2_rate = max(5.0, base_co2_rate * (1 - (renewable_boost_pct / 200.0)))
    simulated_annual_co2_tonnes = max(0.0, ((simulated_annual_mwh * simulated_co2_rate) / 1000.0) - emissions_offset_from_renewables)
    
    co2_saved_tonnes = base_annual_co2_tonnes - simulated_annual_co2_tonnes

    st.markdown("#### 📊 Projected Annual Impact")
    m1, m2, m3 = st.columns(3)

    m1.metric(
        label="Projected Demand",
        value=f"{simulated_annual_mwh / 1e6:.2f} TWh/year",
        delta=f"{demand_change_pct}% vs baseline"
    )

    m2.metric(
        label="Projected Emissions",
        value=f"{simulated_annual_co2_tonnes / 1e6:.2f} Mt $CO_2$/year",
        delta=f"{(simulated_annual_co2_tonnes - base_annual_co2_tonnes) / 1e6:.2f} Mt",
        delta_color="inverse"
    )

    m3.metric(
        label="Est. Annual $CO_2$ Avoided",
        value=f"{max(0.0, co2_saved_tonnes) / 1e6:.2f} Mt $CO_2$",
        help="Estimated metric tonnes of carbon dioxide saved compared to baseline performance."
    )

    st.divider()

    st.subheader("📈 Baseline vs. Simulated Carbon Footprint")

    scenario_names = ["Historical Baseline", "Simulated Scenario"]
    emissions_values = [base_annual_co2_tonnes / 1e6, simulated_annual_co2_tonnes / 1e6]

    fig_sim = go.Figure(
        data=[
            go.Bar(
                x=scenario_names,
                y=emissions_values,
                marker_color=["#7f7f7f", "#2ca02c" if co2_saved_tonnes > 0 else "#d62728"],
                text=[f"{v:.2f} Mt" for v in emissions_values],
                textposition="auto",
            )
        ]
    )

    fig_sim.update_layout(
        title="Annual Grid CO_2 Footprint Comparison (Millions of Metric Tonnes)",
        yaxis_title="Annual CO_2 Emissions (Mt)",
        template="plotly_white",
        height=400
    )

    st.plotly_chart(fig_sim, use_container_width=True)