import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import seaborn as sns



# Set the title and favicon for the Browser's tab bar

st.set_page_config(
    page_title='Accuracy Dashboard',
    page_icon='b',
    layout="centered"
)

# Load and cache the data to avoid reloading it every time
@st.cache_data
def load_accuracy_data():
    """Load the Day 1 and Day 2 accuracy data."""
    DATA_FILENAME = Path(__file__).parent / 'data/data/combined_2.csv'
    accuracy_df = pd.read_csv(DATA_FILENAME)
    return accuracy_df

# Load the data
accuracy_df = load_accuracy_data()

# Title and introductory text
st.title("Day 1 and Day 2 Accuracy Comparison Dashboard")
st.write("Compare the changes in measures across Day 1 and Day 2 for each experimental group.")

# Select Measures and Groups
measures = accuracy_df['Measure'].unique()
selected_measures = st.multiselect("Select Measures to View", options=measures, default=measures)

groups = accuracy_df['Group'].unique()
selected_groups = st.multiselect("Select Groups to View", options=groups, default=groups)

# Filter data based on selections
filtered_df = accuracy_df[(accuracy_df['Measure'].isin(selected_measures)) & 
                          (accuracy_df['Group'].isin(selected_groups))]

# Plot for selected measures and groups
st.header("Measure Comparisons by Day")

# Define a Seaborn color palette and convert to hex for Plotly
seaborn_palette = sns.color_palette("Set2", len(groups))
color_sequence = [f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})" for r, g, b in seaborn_palette]

# Loop over selected measures to create a line graph for each
for measure in selected_measures:
    measure_data = filtered_df[filtered_df['Measure'] == measure]
    
    fig = px.line(
        measure_data, 
        x="Day", y="Mean", color="Group", 
        markers=True, title=f"{measure} Over Days by Group",
        labels={"Mean": f"Mean {measure}", "Day": "Day"},
        color_discrete_sequence=color_sequence  # Apply custom color sequence here
    )
    
    # Render the figure in Streamlit
    st.plotly_chart(fig)

# Adjust line width
    fig.update_traces(line=dict(width=4))  # Increase the width as needed

# Summary statistics and growth display
st.header("Summary of Day 1 and Day 2 Changes")


for group in selected_groups:
    day_1_data = filtered_df[(filtered_df['Group'] == group) & (filtered_df['Day'] == "Day 1")]
    day_2_data = filtered_df[(filtered_df['Group'] == group) & (filtered_df['Day'] == "Day 2")]

    with st.expander(f"{group} - Day 1 to Day 2 Comparison"):
        for measure in selected_measures:
            d1_mean = day_1_data[day_1_data['Measure'] == measure]['Mean'].values[0]
            d2_mean = day_2_data[day_2_data['Measure'] == measure]['Mean'].values[0]
            change = ((d2_mean - d1_mean) / d1_mean) * 100 if d1_mean != 0 else float('nan')
            st.metric(
                label=f"{measure} Change ({group})", 
                value=f"{d2_mean:.2f}", 
                delta=f"{change:.2f}%" if not pd.isna(change) else "N/A"
            )
