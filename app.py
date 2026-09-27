import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Lebanon Tourism Explorer",
    page_icon="🌍",
    layout="wide"
)

# ==========================================================
# LOAD DATA
# ==========================================================

df = pd.read_csv("tourism.csv")

# Clean column names
df.columns = df.columns.str.strip()

# ==========================================================
# TITLE AND CONTEXT
# ==========================================================

st.title("🌍 Lebanon Tourism Explorer")

st.write(
    """
    This interactive application explores tourism characteristics
    across towns and administrative areas in Lebanon. The dashboard
    uses the Tourism Index together with tourism infrastructure
    indicators such as hotels, restaurants, cafes, and guest houses.
    """
)

# ==========================================================
# CHECK REQUIRED COLUMNS
# ==========================================================

required_columns = [
    "refArea",
    "Town",
    "Tourism Index",
    "Total number of hotels",
    "Total number of restaurants",
    "Total number of cafes",
    "Total number of guest houses"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:

    st.error(
        "The following required columns are missing from the dataset:"
    )

    st.write(missing_columns)

    st.stop()

# ==========================================================
# CLEAN DATA
# ==========================================================
df["refArea"] = df["refArea"].astype(str).str.strip()
df["Town"] = df["Town"].astype(str).str.strip()

# Convert Town URLs into readable town names
df["Town"] = (
    df["Town"]
    .str.rstrip("/")
    .str.split("/")
    .str[-1]
    .str.replace("_", " ", regex=False)
)
df["refArea"] = (
    df["refArea"]
    .astype(str)
    .str.strip()
    .str.rstrip("/")
    .str.split("/")
    .str[-1]
    .str.replace("_", " ", regex=False)
)

# Convert numerical columns to numbers
numeric_columns = [
    "Tourism Index",
    "Total number of hotels",
    "Total number of restaurants",
    "Total number of cafes",
    "Total number of guest houses"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

# ==========================================================
# INTERACTION 1 — ADMINISTRATIVE AREA
# ==========================================================

st.sidebar.header("🔎 Explore the data")

areas = sorted(
    df["refArea"].dropna().unique()
)

selected_area = st.sidebar.selectbox(
    "1. Select an administrative area:",
    areas
)

# Filter according to area
area_data = df[
    df["refArea"] == selected_area
]

# ==========================================================
# INTERACTION 2 — TOWN
# LINKED TO AREA
# ==========================================================

towns = sorted(
    area_data["Town"].dropna().unique()
)

selected_town = st.sidebar.selectbox(
    "2. Select a town:",
    towns
)

# Final filtered dataset
town_data = area_data[
    area_data["Town"] == selected_town
]

# ==========================================================
# SELECTED LOCATION
# ==========================================================

st.subheader(
    f"📍 {selected_town}, {selected_area}"
)

st.write(
    "The visualizations below update according to your selections."
)

# ==========================================================
# KEY METRICS
# ==========================================================

if not town_data.empty:

    row = town_data.iloc[0]

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Tourism Index",
            f"{row['Tourism Index']:.2f}"
            if pd.notna(row["Tourism Index"])
            else "N/A"
        )

    with col2:
        st.metric(
            "Hotels",
            int(row["Total number of hotels"])
            if pd.notna(row["Total number of hotels"])
            else 0
        )

    with col3:
        st.metric(
            "Restaurants",
            int(row["Total number of restaurants"])
            if pd.notna(row["Total number of restaurants"])
            else 0
        )

    with col4:
        st.metric(
            "Cafes",
            int(row["Total number of cafes"])
            if pd.notna(row["Total number of cafes"])
            else 0
        )

    with col5:
        st.metric(
            "Guest Houses",
            int(row["Total number of guest houses"])
            if pd.notna(row["Total number of guest houses"])
            else 0
        )

# ==========================================================
# VISUALIZATION 1
# TOURISM INDEX ACROSS TOWNS
# ==========================================================

st.subheader(
    f"Tourism Index across towns in {selected_area}"
)

area_plot = area_data[
    ["Town", "Tourism Index"]
].dropna()

area_plot = (
    area_plot
    .groupby("Town", as_index=False)
    ["Tourism Index"]
    .mean()
    .sort_values(
        "Tourism Index",
        ascending=False
    )
)

fig1 = px.bar(
    area_plot,
    x="Town",
    y="Tourism Index",
    title=f"Tourism Index by Town — {selected_area}",
    labels={
        "Town": "Town",
        "Tourism Index": "Tourism Index"
    }
)

fig1.update_layout(
    xaxis_tickangle=-45
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# ==========================================================
# VISUALIZATION 2
# TOURISM INFRASTRUCTURE
# ==========================================================

st.subheader(
    f"Tourism Infrastructure in {selected_town}"
)

infrastructure = pd.DataFrame({
    "Facility": [
        "Hotels",
        "Restaurants",
        "Cafes",
        "Guest Houses"
    ],
    "Number": [
        row["Total number of hotels"],
        row["Total number of restaurants"],
        row["Total number of cafes"],
        row["Total number of guest houses"]
    ]
})

fig2 = px.bar(
    infrastructure,
    x="Facility",
    y="Number",
    title=f"Tourism Infrastructure — {selected_town}",
    labels={
        "Facility": "Tourism Facility",
        "Number": "Number of Facilities"
    },
    text="Number"
)

fig2.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ==========================================================
# INSIGHTS
# ==========================================================

st.subheader("💡 What can we learn?")

if not area_plot.empty:

    highest_town = area_plot.iloc[0]["Town"]
    highest_index = area_plot.iloc[0]["Tourism Index"]

    st.write(
        f"""
        - Within **{selected_area}**, **{highest_town}** has the
          highest Tourism Index in the displayed data
          ({highest_index:.2f}).
        - The infrastructure chart allows you to examine whether
          the selected town has hotels, restaurants, cafes, and
          guest houses that may support tourism activity.
        - Changing the administrative area automatically changes
          the available town choices, allowing a more focused
          exploration of the dataset.
        """
    )

# ==========================================================
# DESIGN JUSTIFICATION
# ==========================================================

st.subheader("🎨 Design Justification")

with st.expander("Why did I use these two interactions?"):

    st.markdown(
        f"""
        ### 1. Administrative Area Dropdown

        **User question:**  
        Which towns and tourism characteristics are found within
        a particular administrative area?

        **Why a dropdown?**  
        A dropdown was selected because the dataset contains
        multiple administrative areas. Showing every area at once
        would add unnecessary visual clutter. The dropdown allows
        the user to focus attention on one area at a time.

        **Course concept:**  
        This interaction supports **reducing clutter and focusing
        attention** by narrowing the analysis to one administrative
        area.

        ---

        ### 2. Linked Town Dropdown

        **User question:**  
        What is the tourism profile and infrastructure of a
        specific town within the selected administrative area?

        **Why a dropdown?**  
        A dropdown allows the user to select one town without
        displaying many town-level visualizations simultaneously.
        More importantly, the town options change according to the
        selected administrative area.

        **Course concept:**  
        This creates a **drill-down interaction**. The user first
        selects a broad geographic level and then moves to a more
        specific level. This provides context while reducing the
        amount of information shown at one time.
        """
    )

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")

st.caption(
    "Tourism Data Explorer | Built with Python, Pandas, Plotly and Streamlit"
)