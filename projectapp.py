import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from pathlib import Path # ADDED THIS IMPORT

# Set the page title
st.title("Academic Performance Dashboard")

# 1. Load Data
# Use st.cache_data to load data once and improve performance
@st.cache_data
def load_data():
    # --- MODIFIED PATH LOGIC HERE ---
    # Get the directory of the current script (project.py)
    script_dir = Path(__file__).parent
    # Construct the path: <script_dir> / dataset / Academic.csv
    file_path = script_dir / 'dataset' / 'Academic.csv'
    # Make sure the file exists before attempting to read it
    if not file_path.exists():
        st.error(f"File not found: {file_path}. Please ensure 'Academic.csv' is inside a 'dataset' folder next to your script.")
        # Raise an exception or return an empty DataFrame to prevent further errors
        raise FileNotFoundError(f"Data file not found at: {file_path}")
    
    return pd.read_csv(file_path)
    # --- END MODIFIED PATH LOGIC ---

try:
    df = load_data()
except FileNotFoundError as e:
    st.stop() # Stop the app if data loading fails

# 2. Sidebar for Filtering
st.sidebar.header("Data Entry")

# Create the options list: 'All' + unique values from the 'Gender' column
gender_options = ['All'] + df['Gender'].unique().tolist()
gender = st.sidebar.selectbox("Select Gender", gender_options)

# 3. Filtering Logic
# Start with the original dataframe
filtered_df = df.copy()

# Apply the filter if 'All' is NOT selected
if gender != 'All':
    # This line filters the DataFrame based on the selected gender
    filtered_df = filtered_df[filtered_df['Gender'] == gender]

# 4. Display Filtered Data

st.write('Performance Analysis (Filtered Data)')
# Only display the filtered DataFrame
# The unfiltered df is no longer displayed, only the result of the filtering logic
st.dataframe(filtered_df)


avg_grade_by_year = (
    filtered_df
    .groupby("Year", as_index=False)["Grade_Average"]
    .mean()
)

fig_line = px.line(
    avg_grade_by_year,
    x="Year",
    y="Grade_Average",
    markers=True,
    title=f"Average Grade Over Year (Filtered: {gender})"
)

st.plotly_chart(fig_line, use_container_width=True)
st.subheader("1. Student Distribution by Course")

course_counts = filtered_df['Course_Chosen'].value_counts().reset_index()
course_counts.columns = ['Course_Chosen', 'Number of Students']

fig_bar = px.bar(
    course_counts, 
    x='Course_Chosen', 
    y='Number of Students',
    color='Course_Chosen',
    title=f"Count of Students by Course (Filtered: {gender})"
)
st.plotly_chart(fig_bar, use_container_width=True)
st.subheader("3. Attendance Distribution")
st.write("Histogram showing the frequency of different Attendance levels.")

if 'Attendance' in filtered_df.columns:
    # Ensure no NaN values affect the calculation of the mean and plotting
    attendance_data = filtered_df.dropna(subset=['Attendance'])

    fig_hist = px.histogram(
        attendance_data,
        x='Attendance',
        nbins=20, # Number of bars/bins
        color_discrete_sequence=['skyblue'], 
        title=f"Distribution of Attendance (Filtered: {gender})"
    )

    # Calculate and add vertical line for the mean attendance
    if not attendance_data.empty:
        mean_attendance = attendance_data['Attendance'].mean()
        fig_hist.add_vline(x=mean_attendance, line_dash="dash", line_color="red", 
                           annotation_text=f"Mean: {mean_attendance:.2f}", annotation_position="top right")

    st.plotly_chart(fig_hist, use_container_width=True)
else:
    st.warning("Attendance column not available for this visualization.")

# Note: The original code's indentation for the next subheader was incorrect, 
# causing it to only show if 'Attendance' was missing. I've corrected it.
st.subheader("5. Student Distribution by Residence and Region") 
st.write("Comparing the count of students based on their general residence location and regional type.")
residence_counts = df.groupby(['Residence', 'Residence_Type']).size().reset_index(name='Student_Count')

fig_residence = px.bar(
    residence_counts,
    x='Residence',
    y='Student_Count',
    color='Residence_Type',
    barmode='group', # This is key for grouping the bars side-by-side
    title='Student Count by General Residence Location and Residence Region',
    labels={'Residence': 'General Residence Location', 
            'Residence_Type': 'Residence Region', 
            'Student_Count': 'Number of Students'}
)

st.plotly_chart(fig_residence, use_container_width=True)

    



