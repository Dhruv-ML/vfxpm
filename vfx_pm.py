import pandas as pd
import altair as alt
import streamlit as st
from PIL import Image

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="VFX Project Manager Talent Dashboard", layout="wide")

# ----------------------------
# Sidebar logo
# ----------------------------
logo = Image.open("Collavion.jpg")
st.sidebar.image(logo, width=140)

# ----------------------------
# Load dataset
# ----------------------------
vfx = pd.read_csv("VFX PM.csv", encoding="latin1")

# ----------------------------
# Clean / rename columns
# ----------------------------
vfx.columns = [col.strip() for col in vfx.columns]

vfx = vfx.rename(columns={
    "Lat Name": "Last Name",
    "Production/ Project Manager Experience": "PM Experience",
    "VFX/Film Experience": "VFX Experience",
    "Studio Name": "Studio",
    "Current Level": "Level"
})

# ----------------------------
# Preprocess
# ----------------------------
vfx["PM Experience"] = pd.to_numeric(vfx["PM Experience"], errors="coerce")
vfx["VFX Experience"] = pd.to_numeric(vfx["VFX Experience"], errors="coerce")

vfx["LinkedIn"] = vfx["LinkedIn"].fillna("No LinkedIn available")
vfx["Language Proficiency"] = vfx["Language Proficiency"].fillna("Not specified")
vfx["Pronoun"] = vfx["Pronoun"].fillna("Not specified")
vfx["Level"] = vfx["Level"].fillna("Not specified")
vfx["Studio"] = vfx["Studio"].fillna("Not specified")
vfx["City"] = vfx["City"].fillna("Not specified")
vfx["Province"] = vfx["Province"].fillna("Not specified")

vfx = vfx.dropna(subset=["PM Experience", "VFX Experience"])

# ----------------------------
# Sidebar filters
# ----------------------------
st.sidebar.header("🎛 Filter Talent Pool")

province_sorted = sorted(vfx["Province"].dropna().unique())
city_sorted = sorted(vfx["City"].dropna().unique())
language_sorted = sorted(vfx["Language Proficiency"].dropna().unique())

selected_province = st.sidebar.selectbox("Province", ["All"] + province_sorted)

if selected_province != "All":
    city_options = sorted(
        vfx[vfx["Province"] == selected_province]["City"].dropna().unique()
    )
else:
    city_options = city_sorted

selected_city = st.sidebar.selectbox("City", ["All"] + city_options)

selected_language = st.sidebar.selectbox(
    "Language Proficiency",
    ["All"] + language_sorted
)

selected_pm_exp = st.sidebar.slider(
    "Project Manager Experience",
    min_value=int(vfx["PM Experience"].min()),
    max_value=int(vfx["PM Experience"].max()),
    value=int(vfx["PM Experience"].min())
)

selected_vfx_exp = st.sidebar.slider(
    "VFX Experience",
    min_value=int(vfx["VFX Experience"].min()),
    max_value=int(vfx["VFX Experience"].max()),
    value=int(vfx["VFX Experience"].min())
)

# ----------------------------
# Apply sidebar filters
# ----------------------------
filtered_df = vfx.copy()

if selected_province != "All":
    filtered_df = filtered_df[filtered_df["Province"] == selected_province]

if selected_city != "All":
    filtered_df = filtered_df[filtered_df["City"] == selected_city]

if selected_language != "All":
    filtered_df = filtered_df[filtered_df["Language Proficiency"] == selected_language]

filtered_df = filtered_df[filtered_df["PM Experience"] >= selected_pm_exp]
filtered_df = filtered_df[filtered_df["VFX Experience"] >= selected_vfx_exp]

# ----------------------------
# Axis domains with padding
# ----------------------------
x_min = float(vfx["PM Experience"].min())
x_max = float(vfx["PM Experience"].max())
y_min = float(vfx["VFX Experience"].min())
y_max = float(vfx["VFX Experience"].max())

x_range = x_max - x_min
y_range = y_max - y_min

x_padding = max(1, round(x_range * 0.10, 1))
y_padding = max(1, round(y_range * 0.10, 1))

x_domain = [x_min - x_padding, x_max + x_padding]
y_domain = [y_min - y_padding, y_max + y_padding]

# ----------------------------
# Interactive legend selection
# ----------------------------
level_select = alt.selection_point(
    fields=["Level"],
    bind="legend"
)

# ----------------------------
# Base chart (always visible)
# ----------------------------
base = alt.Chart(vfx).mark_point(opacity=0).encode(
    x=alt.X(
        "PM Experience:Q",
        title="PM Experience",
        scale=alt.Scale(domain=x_domain),
        axis=alt.Axis(tickMinStep=1, format="d")
    ),
    y=alt.Y(
        "VFX Experience:Q",
        title="VFX Experience",
        scale=alt.Scale(domain=y_domain),
        axis=alt.Axis(tickMinStep=1, format="d")
    )
).properties(
    width=850,
    height=500
)

# ----------------------------
# Scatter plot (Tableau 20 colors)
# ----------------------------
points = alt.Chart(filtered_df).mark_circle(size=90).encode(
    x=alt.X(
        "PM Experience:Q",
        title="PM Experience",
        scale=alt.Scale(domain=x_domain),
        axis=alt.Axis(tickMinStep=1, format="d")
    ),
    y=alt.Y(
        "VFX Experience:Q",
        title="VFX Experience",
        scale=alt.Scale(domain=y_domain),
        axis=alt.Axis(tickMinStep=1, format="d")
    ),
    color=alt.Color(
        "Level:N",
        title="Level",
        scale=alt.Scale(scheme="tableau20"),
        legend=alt.Legend(orient="right")
    ),
    opacity=alt.condition(level_select, alt.value(1), alt.value(0.15)),
    tooltip=[
        alt.Tooltip("First Name:N", title="First Name"),
        alt.Tooltip("Last Name:N", title="Last Name"),
        alt.Tooltip("Studio:N", title="Studio"),
        alt.Tooltip("City:N", title="City"),
        alt.Tooltip("Province:N", title="Province"),
        alt.Tooltip("Level:N", title="Level"),
        alt.Tooltip("Language Proficiency:N", title="Language"),
        alt.Tooltip("Pronoun:N", title="Pronoun"),
        alt.Tooltip("PM Experience:Q", title="PM Experience"),
        alt.Tooltip("VFX Experience:Q", title="VFX Experience"),
        alt.Tooltip("LinkedIn:N", title="LinkedIn")
    ]
).add_params(
    level_select
)

chart = (base + points).interactive()

# ----------------------------
# Main layout (Title + Subheading)
# ----------------------------
st.title("VFX Project Manager Talent Dashboard")

st.markdown(
    "<div style='color: #6c757d; font-size:16px; margin-bottom: 20px;'>"
    "A talent snapshot revealing where VFX Project Manager talent exists, "
    "how it is distributed, and how to access it effectively."
    "</div>",
    unsafe_allow_html=True
)

st.altair_chart(chart, use_container_width=True)

if filtered_df.empty:
    st.info("No candidates match the selected filters. The chart frame remains visible for reference.")

# ----------------------------
# Filtered candidate table
# ----------------------------
st.subheader(f"📋 Filtered Candidates ({len(filtered_df)} profiles)")

display_columns = [
    "First Name",
    "Last Name",
    "LinkedIn",
    "PM Experience",
    "VFX Experience",
    "Language Proficiency",
    "Level",
    "Studio",
    "City",
    "Province",
    "Pronoun"
]

if not filtered_df.empty:
    st.dataframe(filtered_df[display_columns], use_container_width=True)

    csv = filtered_df[display_columns].to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Filtered Data",
        csv,
        "filtered_vfx_talent.csv",
        "text/csv"
    )
else:
    st.warning("⚠️ No candidates match the selected filters.")
