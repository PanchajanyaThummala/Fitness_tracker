import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Database setup
DB_FILE = 'exercise_log.db'

# Function to create a database connection
def create_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

# Function to create the exercises table
def create_table():
    conn = create_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                exercise TEXT,
                set1_weight REAL,
                set1_reps INTEGER,
                set2_weight REAL,
                set2_reps INTEGER,
                set3_weight REAL,
                set3_reps INTEGER
            )
        ''')
    conn.close()

# Function to load existing data
def load_data():
    conn = create_connection()
    data = pd.read_sql_query("SELECT * FROM exercises", conn)
    conn.close()
    return data

# Function to save data
def save_data(entry):
    conn = create_connection()
    with conn:
        conn.execute('''
            INSERT INTO exercises (date, exercise, set1_weight, set1_reps, set2_weight, set2_reps, set3_weight, set3_reps)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', entry)
    conn.close()

# Function to clear data
def clear_data():
    conn = create_connection()
    with conn:
        conn.execute("DELETE FROM exercises")
    conn.close()

# Create the table if it doesn't exist
create_table()

# Streamlit app layout
st.set_page_config(page_title="Exercise Log", layout="wide")
st.title("🏋️ Exercise Log")

# Sidebar for inputs
st.sidebar.header("Log Your Exercise")
date = st.sidebar.date_input("Select Date", datetime.today())
exercise = st.sidebar.selectbox("Select Exercise", [
    "Romanian Deadlifts (RDLs) - With Barbell",
    "Chest Supported T-Bar Rows",
    "Lat Pulldowns [Mag-Grip Handle]",
    "Leg Curls",
    "Smith Calf Raises",
    "Rope Crunches",
    "Pec Dec Flys",
    "Smith Bench Press [Low Incline]",
    "Dumbell Shoulder Press",
    "Cable Lateral Raises",
    "E-Z Bar Skull Crushers",
    "Close Grip Bench Press",
    "Leg Press (Close Stance)",
    "Bulgarian Split Squats",
    "Leg Extensions",
    "Leg Raises",
    "Decline Crunches",
    "Russian Twists",
    "Smith Shoulder Press",
    "Lateral Raises",
    "Tricep Pushdown",
    "Hammer Curls [Dumbell]",
    "Single Arm Tricep Overhead Extensions",
    "Single Arm Preacher Curls",
    "Dumbell Press [Low Decline]",
    "Dips (Parallel Bar)",
    "Single Arm Dumbell Rows",
    "Lat Pullovers (With Cable)",
    "Seated Facepulls",
    "Farmer Walks"
])

num_sets = st.sidebar.number_input("Number of Sets", min_value=1, max_value=3, value=1)

# Initialize lists to store weights and reps
weights = []
reps = []

# Input fields for weight and reps for each set
for i in range(int(num_sets)):
    weight = st.sidebar.number_input(f"Weight for Set {i + 1} (kg)", min_value=0.0, format="%.2f", key=f"weight_{i}")
    rep = st.sidebar.number_input(f"Reps for Set {i + 1}", min_value=0, key=f"reps_{i}")
    weights.append(weight)
    reps.append(rep)

# Button to log the exercise
if st.sidebar.button("Log Exercise"):
    if exercise:
        new_entry = (
            str(date),
            exercise,
            weights[0] if len(weights) > 0 else 0,
            reps[0] if len(reps) > 0 else 0,
            weights[1] if len(weights) > 1 else 0,
            reps[1] if len(reps) > 1 else 0,
            weights[2] if len(weights) > 2 else 0,
            reps[2] if len(reps) > 2 else 0,
        )
        save_data(new_entry)
        st.success("Exercise logged successfully!")
    else:
        st.error("Please select an exercise.")

# Clear data button
if st.sidebar.button("Clear All Entries"):
    clear_data()
    st.success("All entries cleared successfully!")

# Display logged exercises
st.subheader("📊 Logged Exercises")
data = load_data()
if not data.empty:
    st.dataframe(data, use_container_width=True)  # Display the DataFrame without index
else:
    st.write("No entries found. Please log your exercises.")

# Optional: Add charts or statistics here
