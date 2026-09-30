"""Web interface for the elastic-sphere target-strength calculator."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ts_elastic_spheres.backscatter import target_strength
from ts_elastic_spheres.materials import MATERIALS


# ==============================================================
# Page configuration
# ==============================================================

st.set_page_config(
    page_title="Elastic Sphere TS Calculator",
    page_icon="🔊",
    layout="wide",
)

st.title("Elastic Sphere Target Strength Calculator")

st.write(
    "Calculate and compare the theoretical broadband target strength "
    "of elastic spheres."
)


# ==============================================================
# Session state
# ==============================================================

if "results" not in st.session_state:
    st.session_state.results = []


# ==============================================================
# Sphere parameters
# ==============================================================

st.sidebar.header("Sphere")

material_options = list(MATERIALS.keys()) + ["Custom"]

material_selection = st.sidebar.selectbox(
    "Material",
    material_options,
)


# ==============================================================
# Material properties
# ==============================================================

if material_selection == "Custom":

    material_name = st.sidebar.text_input(
        "Material name",
        value="Custom",
    )

    rho_sphere = st.sidebar.number_input(
        "Sphere density (kg/m³)",
        min_value=1.0,
        value=7800.0,
        step=100.0,
    )

    c_compressional = st.sidebar.number_input(
        "Compressional sound speed, cₚ (m/s)",
        min_value=1.0,
        value=5900.0,
        step=100.0,
    )

    c_shear = st.sidebar.number_input(
        "Shear sound speed, cₛ (m/s)",
        min_value=1.0,
        value=3200.0,
        step=100.0,
    )

else:

    material_name = material_selection
    material = MATERIALS[material_name]

    rho_sphere = material["density"]
    c_compressional = material["c_compressional"]
    c_shear = material["c_shear"]

    st.sidebar.markdown(
        f"""
        **Material properties**

        ρ = **{rho_sphere:g} kg/m³**  
        cₚ = **{c_compressional:g} m/s**  
        cₛ = **{c_shear:g} m/s**
        """
    )



# ==============================================================
# Sphere diameter
# ==============================================================

diameter_mm = st.sidebar.number_input(
    "Diameter (mm)",
    min_value=1.0,
    max_value=200.0,
    value=38.1,
    step=0.1,
)


# ==============================================================
# Frequency parameters
# ==============================================================

st.sidebar.header("Frequency")

f_start_khz = st.sidebar.number_input(
    "Start frequency (kHz)",
    min_value=1.0,
    max_value=1000.0,
    value=33.0,
    step=1.0,
)

f_end_khz = st.sidebar.number_input(
    "End frequency (kHz)",
    min_value=1.0,
    max_value=1000.0,
    value=260.0,
    step=1.0,
)

df_khz = st.sidebar.number_input(
    "Frequency resolution (kHz)",
    min_value=0.01,
    max_value=100.0,
    value=0.5,
    step=0.1,
)

# ==============================================================
# CW frequencies
# ==============================================================

show_cw = st.sidebar.checkbox(
    "Show CW frequencies",
    value=False,
)

cw_frequency_text = st.sidebar.text_input(
    "CW frequencies (kHz)",
    value="38, 70, 120, 200, 333",
    disabled=not show_cw,
)

cw_frequencies = []

if show_cw:
    try:
        cw_frequencies = [
            float(f.strip())
            for f in cw_frequency_text.split(",")
            if f.strip()
        ]
    except ValueError:
        st.sidebar.error(
            "CW frequencies must be comma-separated numbers."
        )

# ==============================================================
# Water properties
# ==============================================================

st.sidebar.header("Water")

rho_water = st.sidebar.number_input(
    "Water density (kg/m³)",
    min_value=900.0,
    max_value=1200.0,
    value=1027.0,
    step=1.0,
)

c_water = st.sidebar.number_input(
    "Sound speed (m/s)",
    min_value=1300.0,
    max_value=1700.0,
    value=1500.0,
    step=1.0,
)


# ==============================================================
# Buttons
# ==============================================================

calculate_button = st.sidebar.button(
    "Calculate TS",
    type="primary",
    use_container_width=True,
)

clear_button = st.sidebar.button(
    "Clear results",
    use_container_width=True,
    disabled=len(st.session_state.results) == 0,
)


# ==============================================================
# Clear results
# ==============================================================

if clear_button:

    st.session_state.results = []

    st.rerun()


# ==============================================================
# Calculate TS
# ==============================================================

if calculate_button:

    if f_end_khz <= f_start_khz:

        st.sidebar.error(
            "End frequency must be greater than start frequency."
        )

    else:

        radius = diameter_mm * 1e-3 / 2.0

        f_start = f_start_khz * 1e3
        f_end = f_end_khz * 1e3
        df = df_khz * 1e3

        frequencies = np.arange(
            f_start,
            f_end + 0.5 * df,
            df,
        )

        expansion_order = (
            int(radius * 2.0 * np.pi * f_end / c_water) + 20
        )

        TS = np.empty(len(frequencies))

        progress = st.sidebar.progress(0)

        for ii, frequency in enumerate(frequencies):

            TS[ii] = target_strength(
                radius,
                frequency,
                rho_water,
                c_water,
                rho_sphere,
                c_compressional,
                c_shear,
                expansion_order=expansion_order,
            )

            progress.progress(
                (ii + 1) / len(frequencies)
            )

        progress.empty()


        # ======================================================
        # Store result
        # ======================================================

        result = {
            "material": material_name,
            "diameter_mm": diameter_mm,
            "frequencies": frequencies,
            "TS": TS,
            "rho_water": rho_water,
            "c_water": c_water,
            "rho_sphere": rho_sphere,
            "c_compressional": c_compressional,
            "c_shear": c_shear,
            "expansion_order": expansion_order,
        }

        st.session_state.results.append(result)


# ==============================================================
# No results
# ==============================================================

if not st.session_state.results:

    st.info(
        "Select the sphere and acoustic parameters in the sidebar, "
        "then click **Calculate TS**."
    )

    st.stop()


# ==============================================================
# Plot
# ==============================================================

st.subheader("Target Strength")

fig = go.Figure()

for result in st.session_state.results:

    label = (
        f'{result["diameter_mm"]:.1f} mm '
        f'{result["material"]}'
    )

    fig.add_trace(
        go.Scatter(
            x=result["frequencies"] / 1e3,
            y=result["TS"],
            mode="lines",
            name=label,
        )
    )

# ==============================================================
# CW frequency markers
# ==============================================================

if show_cw:

    for frequency in cw_frequencies:

        fig.add_vline(
            x=frequency,
            line_width=1.5,
            line_dash="dash",
            line_color="gray",
        )

        fig.add_annotation(
            x=frequency,
            y=1.0,
            yref="paper",
            text=f"{frequency:g} kHz",
            showarrow=False,
            yanchor="bottom",
            textangle=-90,
            font=dict(size=13),
        )

# ==============================================================
# Plot formatting
# ==============================================================

fig.update_layout(
    xaxis_title="Frequency (kHz)",
    yaxis_title="TS (dB re 1 m²)",
    hovermode="x",
    autosize=True,
    margin=dict(l=20, r=20, t=30, b=20),
    font=dict(size=14),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
        font=dict(size=13),
        title=None,
    ),
)

fig.update_xaxes(
    showgrid=True,
    title_font=dict(size=16),
    tickfont=dict(size=13),
)

fig.update_yaxes(
    showgrid=True,
    title_font=dict(size=16),
    tickfont=dict(size=13),
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"responsive": True},
)

# ==============================================================
# Calculated spheres
# ==============================================================

st.subheader("Calculated spheres")

for ii, result in enumerate(st.session_state.results):

    col1, col2, col3, col4 = st.columns(
        [2, 3, 3, 1]
    )

    col1.write(
        f'**{result["diameter_mm"]:.1f} mm**'
    )

    col2.write(
        result["material"]
    )

    col3.write(
        f'{result["frequencies"][0] / 1e3:g}–'
        f'{result["frequencies"][-1] / 1e3:g} kHz'
    )

    if col4.button(
        "Remove",
        key=f"remove_{ii}",
    ):

        st.session_state.results.pop(ii)

        st.rerun()


# ==============================================================
# Calculation details
# ==============================================================

with st.expander(
    "Calculation details"
):

    for ii, result in enumerate(
        st.session_state.results,
        start=1,
    ):

        st.markdown(
            f'### {result["diameter_mm"]:.1f} mm '
            f'{result["material"]}'
        )

        st.write(
            f'**Sphere density:** '
            f'{result["rho_sphere"]:.1f} kg/m³'
        )

        st.write(
            f'**Compressional sound speed:** '
            f'{result["c_compressional"]:.1f} m/s'
        )

        st.write(
            f'**Shear sound speed:** '
            f'{result["c_shear"]:.1f} m/s'
        )

        st.write(
            f'**Water density:** '
            f'{result["rho_water"]:.1f} kg/m³'
        )

        st.write(
            f'**Water sound speed:** '
            f'{result["c_water"]:.1f} m/s'
        )

        st.write(
            f'**Expansion order:** '
            f'{result["expansion_order"]}'
        )

        if ii < len(st.session_state.results):

            st.divider()


# ==============================================================
# Calculated data
# ==============================================================

with st.expander(
    "Calculated data"
):

    for result in st.session_state.results:

        st.markdown(
            f'**{result["diameter_mm"]:.1f} mm '
            f'{result["material"]}**'
        )

        result_table = pd.DataFrame(
            {
                "Frequency (kHz)":
                    result["frequencies"] / 1e3,

                "TS (dB)":
                    result["TS"],
            }
        )

        st.dataframe(
            result_table,
            use_container_width=True,
            hide_index=True,
        )


# ==============================================================
# Download all results
# ==============================================================

data_frames = []

for result in st.session_state.results:

    df_result = pd.DataFrame(
        {
            "Frequency (kHz)":
                result["frequencies"] / 1e3,

            "TS (dB)":
                result["TS"],

            "Diameter (mm)":
                result["diameter_mm"],

            "Material":
                result["material"],

            "Sphere density (kg/m³)":
                result["rho_sphere"],

            "Compressional speed (m/s)":
                result["c_compressional"],

            "Shear speed (m/s)":
                result["c_shear"],
        }
    )

    data_frames.append(
        df_result
    )


combined_results = pd.concat(
    data_frames,
    ignore_index=True,
)

csv = combined_results.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    "Download results as CSV",
    data=csv,
    file_name="elastic_sphere_TS.csv",
    mime="text/csv",
)