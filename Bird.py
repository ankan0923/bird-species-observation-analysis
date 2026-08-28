import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Bird Species Observation Analysis",

    page_icon="🐦",
    layout="wide")

# ==================================================
# LOAD DATA
# ==================================================

@st.cache_data
def load_data():
    df = pd.read_csv("Bird_Observation_Cleaned.csv")

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df


df = load_data()

# ==================================================
# CUSTOM STYLE
# ==================================================

st.markdown("""
<style>

.stApp {
    background-color: #0B1412;
    color: #F1FAF6;
}

.block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background-color: #101C19;
    border-right: 1px solid #263B35;
}

[data-testid="stSidebar"] * {
    color: #F1FAF6;
}

h1, h2, h3 {
    color: #F1FAF6;
}

[data-testid="stMetric"] {
    background-color: #13211D;
    border: 1px solid #263B35;
    padding: 18px;
    border-radius: 15px;
}

[data-testid="stMetricLabel"] {
    color: #9CB8AE;
}

[data-testid="stMetricValue"] {
    color: #52B788;
    font-weight: 700;
}

button[data-baseweb="tab"] {
    font-weight: 600;
    color: #9CB8AE;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #52B788;
    border-bottom: 3px solid #52B788;
}

.hero-box {
    background: linear-gradient(135deg, #13211D, #183128);
    border: 1px solid #2A9D8F;
    padding: 28px 32px;
    border-radius: 20px;
    margin-bottom: 18px;
}

.hero-title {
    font-size: 38px;
    font-weight: 800;
    color: #F1FAF6;
}

.hero-subtitle {
    font-size: 16px;
    color: #9CB8AE;
    margin-top: 8px;
}

.insight-box {
    background-color: #13211D;
    border-left: 5px solid #E9C46A;
    padding: 16px;
    border-radius: 10px;
    color: #F1FAF6;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================

st.markdown("""
<div class="hero-box">
    <div class="hero-title">Bird Species Observation Analysis</div>
    <div class="hero-subtitle">
        Explore biodiversity, habitat patterns, species behavior,
        environmental conditions and conservation indicators
        across Forest and Grassland ecosystems.
    </div>
</div>
""", unsafe_allow_html=True)

# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.markdown("## 🎛 Dashboard Filters")

habitat_options = sorted(df["Habitat"].dropna().unique())

selected_habitat = st.sidebar.multiselect(
    "Habitat",
    habitat_options,
    default=habitat_options
)

admin_options = sorted(df["Admin_Unit_Code"].dropna().unique())

selected_admin = st.sidebar.multiselect(
    "Administrative Unit",
    admin_options,
    default=admin_options
)

species_options = sorted(df["Common_Name"].dropna().unique())

selected_species = st.sidebar.multiselect(
    "Species",
    species_options
)

if "Month_Name" in df.columns:
    month_order = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ]

    available_months = [
        x for x in month_order
        if x in df["Month_Name"].dropna().unique()
    ]

    selected_month = st.sidebar.multiselect(
        "Month",
        available_months,
        default=available_months
    )
else:
    selected_month = []

# ==================================================
# APPLY FILTERS
# ==================================================

filtered_df = df.copy()

if selected_habitat:
    filtered_df = filtered_df[
        filtered_df["Habitat"].isin(selected_habitat)
    ]

if selected_admin:
    filtered_df = filtered_df[
        filtered_df["Admin_Unit_Code"].isin(selected_admin)
    ]

if selected_species:
    filtered_df = filtered_df[
        filtered_df["Common_Name"].isin(selected_species)
    ]

if selected_month and "Month_Name" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["Month_Name"].isin(selected_month)
    ]

# ==================================================
# KPIs
# ==================================================

total_observations = len(filtered_df)
unique_species = filtered_df["Scientific_Name"].nunique()
total_habitats = filtered_df["Habitat"].nunique()
total_admin_units = filtered_df["Admin_Unit_Code"].nunique()
total_plots = filtered_df["Plot_Name"].nunique()

st.caption(
    f"Showing {total_observations:,} observations "
    f"from {len(df):,} total records."
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("OBSERVATIONS", f"{total_observations:,}")
c2.metric("UNIQUE SPECIES", unique_species)
c3.metric("HABITATS", total_habitats)
c4.metric("ADMIN UNITS", total_admin_units)
c5.metric("PLOTS", total_plots)

st.markdown("---")

# ==================================================
# TABS
# ==================================================

tab1, tab2, tab3 = st.tabs([
    "Overview",
    "Species & Habitat",
    "Environment & Behavior"
])

habitat_colors = {
    "Forest": "#52A2B4",
    "Grassland": "#E9C46A"
}

plot_bg = "#0B1412"
grid_color = "#263B35"
text_color = "#F1FAF6"

# ==================================================
# TAB 1 - OVERVIEW
# ==================================================

with tab1:

    st.header("Overview")

    # -----------------------------
    # Habitat Share
    # -----------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Observation Share by Habitat")

        habitat_obs = (
            filtered_df
            .groupby("Habitat")
            .size()
            .reset_index(name="Observations")
        )

        fig = px.pie(
            habitat_obs,
            names="Habitat",
            values="Observations",
            hole=0.55,
            color="Habitat",
            color_discrete_map=habitat_colors
        )

        fig.update_layout(
            paper_bgcolor=plot_bg,
            font_color=text_color,
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Habitat Richness
    # -----------------------------

    with col2:

        st.subheader("Species Richness by Habitat")

        richness = (
            filtered_df
            .groupby("Habitat")["Scientific_Name"]
            .nunique()
            .reset_index(name="Unique_Species")
        )

        fig = px.bar(
            richness,
            x="Habitat",
            y="Unique_Species",
            color="Habitat",
            text="Unique_Species",
            color_discrete_map=habitat_colors
        )

        fig.update_layout(
            paper_bgcolor=plot_bg,
            plot_bgcolor=plot_bg,
            font_color=text_color,
            showlegend=False,
            height=400,
            yaxis_gridcolor=grid_color
        )

        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Top Species
    # -----------------------------

    col3, col4 = st.columns(2)

    with col3:

        st.subheader("Top 10 Most Observed Species")

        top_species = (
            filtered_df["Common_Name"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        top_species.columns = [
            "Common_Name",
            "Observations"
        ]

        top_species = top_species.sort_values(
            "Observations"
        )

        fig = px.bar(
            top_species,
            x="Observations",
            y="Common_Name",
            orientation="h",
            text="Observations"
        )

        fig.update_traces(
            marker_color="#2A9D8F"
        )

        fig.update_layout(
            paper_bgcolor=plot_bg,
            plot_bgcolor=plot_bg,
            font_color=text_color,
            height=480,
            xaxis_gridcolor=grid_color,
            yaxis_title=""
        )

        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Admin Units
    # -----------------------------

    with col4:

        st.subheader("Observation Volume by Administrative Unit")

        admin_obs = (
            filtered_df
            .groupby("Admin_Unit_Code")
            .size()
            .reset_index(name="Observations")
            .sort_values("Observations")
        )

        fig = px.bar(
            admin_obs,
            x="Observations",
            y="Admin_Unit_Code",
            orientation="h",
            text="Observations"
        )

        fig.update_traces(
            marker_color="#52B788"
        )

        fig.update_layout(
            paper_bgcolor=plot_bg,
            plot_bgcolor=plot_bg,
            font_color=text_color,
            height=480,
            xaxis_gridcolor=grid_color,
            yaxis_title=""
        )

        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Monthly Trend
    # -----------------------------

    if "Month_Name" in filtered_df.columns:

        st.subheader("Monthly Observation Trend")

        month_order = [
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ]

        monthly = (
            filtered_df
            .groupby("Month_Name")
            .size()
            .reset_index(name="Observations")
        )

        monthly["Month_Name"] = pd.Categorical(
            monthly["Month_Name"],
            categories=month_order,
            ordered=True
        )

        monthly = monthly.sort_values("Month_Name")

        fig = px.line(
            monthly,
            x="Month_Name",
            y="Observations",
            markers=True
        )

        fig.update_traces(
            line_color="#E9C46A"
        )

        fig.update_layout(
            paper_bgcolor=plot_bg,
            plot_bgcolor=plot_bg,
            font_color=text_color,
            yaxis_gridcolor=grid_color
        )

        st.plotly_chart(fig, use_container_width=True)

# ==================================================
# TAB 2 - SPECIES & HABITAT
# ==================================================

with tab2:

    st.header("Species & Habitat Analysis")

    # -----------------------------
    # Forest vs Grassland
    # -----------------------------

    st.subheader("Top Species: Forest vs Grassland")

    habitat_species = (
        filtered_df
        .groupby(["Common_Name", "Habitat"])
        .size()
        .reset_index(name="Observations")
    )

    top_names = (
        filtered_df["Common_Name"]
        .value_counts()
        .head(10)
        .index
    )

    habitat_species = habitat_species[
        habitat_species["Common_Name"].isin(top_names)
    ]

    fig = px.bar(
        habitat_species,
        x="Common_Name",
        y="Observations",
        color="Habitat",
        barmode="group",
        color_discrete_map=habitat_colors
    )

    fig.update_layout(
        paper_bgcolor=plot_bg,
        plot_bgcolor=plot_bg,
        font_color=text_color,
        xaxis_tickangle=-40,
        yaxis_gridcolor=grid_color
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Species Profile
    # -----------------------------

    st.subheader("Species Profile")

    species_selected = st.selectbox(
        "Select a species",
        sorted(filtered_df["Common_Name"].dropna().unique())
    )

    species_df = filtered_df[
        filtered_df["Common_Name"] == species_selected
    ]

    p1, p2, p3, p4 = st.columns(4)

    p1.metric("Observations", len(species_df))
    p2.metric("Habitats", species_df["Habitat"].nunique())
    p3.metric("Admin Units", species_df["Admin_Unit_Code"].nunique())
    p4.metric("Plots", species_df["Plot_Name"].nunique())

    species_habitat = (
        species_df["Habitat"]
        .value_counts()
        .reset_index()
    )

    species_habitat.columns = [
        "Habitat",
        "Observations"
    ]

    fig = px.pie(
        species_habitat,
        names="Habitat",
        values="Observations",
        hole=0.55,
        color="Habitat",
        color_discrete_map=habitat_colors
    )

    fig.update_layout(
        paper_bgcolor=plot_bg,
        font_color=text_color
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # ID Method + Sex
    # -----------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Identification Method")

        id_method = (
            filtered_df["ID_Method"]
            .value_counts()
            .reset_index()
        )

        id_method.columns = [
            "ID_Method",
            "Observations"
        ]

        fig = px.bar(
            id_method,
            x="Observations",
            y="ID_Method",
            orientation="h"
        )

        fig.update_traces(
            marker_color="#2A9D8F"
        )

        fig.update_layout(
            paper_bgcolor=plot_bg,
            plot_bgcolor=plot_bg,
            font_color=text_color,
            xaxis_gridcolor=grid_color
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        st.subheader("Sex Distribution")

        sex_data = (
            filtered_df["Sex"]
            .value_counts()
            .reset_index()
        )

        sex_data.columns = [
            "Sex",
            "Observations"
        ]

        fig = px.pie(
            sex_data,
            names="Sex",
            values="Observations",
            hole=0.5
        )

        fig.update_layout(
            paper_bgcolor=plot_bg,
            font_color=text_color
        )

        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Distance
    # -----------------------------

    st.subheader("Observation Distance")

    distance_data = (
        filtered_df["Distance"]
        .value_counts()
        .reset_index()
    )

    distance_data.columns = [
        "Distance",
        "Observations"
    ]

    fig = px.bar(
        distance_data,
        x="Distance",
        y="Observations",
        text="Observations"
    )

    fig.update_traces(
        marker_color="#52B788"
    )

    fig.update_layout(
        paper_bgcolor=plot_bg,
        plot_bgcolor=plot_bg,
        font_color=text_color,
        xaxis_tickangle=-30,
        yaxis_gridcolor=grid_color
    )

    st.plotly_chart(fig, use_container_width=True)

# ==================================================
# TAB 3 - ENVIRONMENT & BEHAVIOR
# ==================================================

with tab3:

    st.header("Environment & Behavior")

    # -----------------------------
    # Temperature + Humidity
    # -----------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Temperature Distribution")

        fig = px.histogram(
            filtered_df,
            x="Temperature",
            color="Habitat",
            nbins=25,
            color_discrete_map=habitat_colors
        )

        fig.update_layout(
            paper_bgcolor=plot_bg,
            plot_bgcolor=plot_bg,
            font_color=text_color,
            yaxis_gridcolor=grid_color
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        st.subheader("Humidity Distribution")

        fig = px.histogram(
            filtered_df,
            x="Humidity",
            color="Habitat",
            nbins=25,
            color_discrete_map=habitat_colors
        )

        fig.update_layout(
            paper_bgcolor=plot_bg,
            plot_bgcolor=plot_bg,
            font_color=text_color,
            yaxis_gridcolor=grid_color
        )

        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Temp vs Humidity
    # -----------------------------

    st.subheader("Temperature vs Humidity")

    fig = px.scatter(
        filtered_df,
        x="Temperature",
        y="Humidity",
        color="Habitat",
        opacity=0.55,
        color_discrete_map=habitat_colors,
        hover_data=[
            "Common_Name",
            "Admin_Unit_Code"
        ]
    )

    fig.update_layout(
        paper_bgcolor=plot_bg,
        plot_bgcolor=plot_bg,
        font_color=text_color,
        xaxis_gridcolor=grid_color,
        yaxis_gridcolor=grid_color
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Sky + Wind
    # -----------------------------

    col3, col4 = st.columns(2)

    with col3:

        st.subheader("Sky Conditions")

        sky_data = (
            filtered_df["Sky"]
            .value_counts()
            .head(8)
            .reset_index()
        )

        sky_data.columns = [
            "Sky",
            "Observations"
        ]

        fig = px.bar(
            sky_data,
            x="Observations",
            y="Sky",
            orientation="h"
        )

        fig.update_traces(
            marker_color="#2A9D8F"
        )

        fig.update_layout(
            paper_bgcolor=plot_bg,
            plot_bgcolor=plot_bg,
            font_color=text_color,
            xaxis_gridcolor=grid_color
        )

        st.plotly_chart(fig, use_container_width=True)

    with col4:

        st.subheader("Wind Conditions")

        wind_data = (
            filtered_df["Wind"]
            .value_counts()
            .head(8)
            .reset_index()
        )

        wind_data.columns = [
            "Wind",
            "Observations"
        ]

        fig = px.bar(
            wind_data,
            x="Observations",
            y="Wind",
            orientation="h"
        )

        fig.update_traces(
            marker_color="#E9C46A"
        )

        fig.update_layout(
            paper_bgcolor=plot_bg,
            plot_bgcolor=plot_bg,
            font_color=text_color,
            xaxis_gridcolor=grid_color
        )

        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Disturbance
    # -----------------------------

    st.subheader("Disturbance vs Species Richness")

    disturbance = (
        filtered_df
        .groupby("Disturbance")
        .agg(
            Observations=("Scientific_Name", "size"),
            Species_Richness=("Scientific_Name", "nunique")
        )
        .reset_index()
    )

    fig = px.bar(
        disturbance,
        x="Disturbance",
        y="Species_Richness",
        text="Species_Richness"
    )

    fig.update_traces(
        marker_color="#E76F32"
    )

    fig.update_layout(
        paper_bgcolor=plot_bg,
        plot_bgcolor=plot_bg,
        font_color=text_color,
        xaxis_tickangle=-30,
        yaxis_gridcolor=grid_color
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Flyover Behavior
    # -----------------------------

    if "Flyover_Observed" in filtered_df.columns:

        st.subheader("Flyover Behavior by Habitat")

        flyover = (
            filtered_df
            .groupby(
                ["Habitat", "Flyover_Observed"]
            )
            .size()
            .reset_index(name="Observations")
        )

        fig = px.bar(
            flyover,
            x="Habitat",
            y="Observations",
            color="Flyover_Observed",
            barmode="group"
        )

        fig.update_layout(
            paper_bgcolor=plot_bg,
            plot_bgcolor=plot_bg,
            font_color=text_color,
            yaxis_gridcolor=grid_color
        )

        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Conservation Indicators
    # -----------------------------

    st.subheader("Conservation Indicators")

    if "PIF_Watchlist_Status" in filtered_df.columns:

        pif_data = (
            filtered_df["PIF_Watchlist_Status"]
            .astype(str)
            .value_counts()
            .reset_index()
        )

        pif_data.columns = [
            "Status",
            "Observations"
        ]

        fig = px.pie(
            pif_data,
            names="Status",
            values="Observations",
            hole=0.55
        )

        fig.update_layout(
            paper_bgcolor=plot_bg,
            font_color=text_color
        )

        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Interpretation
    # -----------------------------

    st.markdown("""
    <div class="insight-box">

    💡 <b>Interpretation Note</b><br><br>
    High observation counts under a particular environmental condition
    should not automatically be interpreted as bird preference.
    Observation frequency may also depend on survey effort,
    number of visits, observer differences, habitat availability
    and detectability.

    </div>
    """, unsafe_allow_html=True)