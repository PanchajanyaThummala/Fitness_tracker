import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import bcrypt
import re

# Database setup
DB_FILE = 'exercise_log.db'

# Function to create a database connection
def create_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

# Function to create the users and exercises tables
def create_tables():
    conn = create_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
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

# Function to validate password
def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""

# Function to register a new user
def register_user(username, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = create_connection()
    with conn:
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
    conn.close()

# Function to authenticate a user
def authenticate_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
        return True
    return False

# Function to load existing data for a specific user, optionally filtered by date
def load_data(username, selected_date=None):
    conn = create_connection()
    if selected_date:
        data = pd.read_sql_query("SELECT * FROM exercises WHERE username = ? AND date = ?", conn, params=(username, selected_date))
    else:
        data = pd.read_sql_query("SELECT * FROM exercises WHERE username = ?", conn, params=(username,))
    conn.close()
    return data

# Function to save data
def save_data(entry):
    conn = create_connection()
    with conn:
        conn.execute('''
            INSERT INTO exercises (username, date, exercise, set1_weight, set1_reps, set2_weight, set2_reps, set3_weight, set3_reps)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', entry)
    conn.close()

# Function to clear data for a specific user
def clear_data(username):
    conn = create_connection()
    with conn:
        conn.execute("DELETE FROM exercises WHERE username = ?", (username,))
    conn.close()

# Create the tables if they don't exist
create_tables()

# Streamlit app layout
st.set_page_config(page_title="FITRACK", layout="wide")
st.title("🏋️ FIT TRACK")

# User authentication
if 'username' not in st.session_state:
    st.session_state.username = None

# Registration and Login
if st.session_state.username is None:
    st.sidebar.header("User Registration / Login")
    option = st.sidebar.selectbox("Choose an option", ["Login", "Register"])

    if option == "Register":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        
        # Display password rules
        st.sidebar.markdown("""
        **Password Rules:**
        - At least 8 characters long
        - At least one uppercase letter (A-Z)
        - At least one lowercase letter (a-z)
        - At least one digit (0-9)
        - At least one special character (e.g., @, #, $, etc.)
        """)

        if st.sidebar.button("Register"):
            is_valid, message = validate_password(password)
            if not is_valid:
                st.error(message)
            else:
                try:
                    register_user(username, password)
                    st.success("User registered successfully!")
                except Exception as e:
                    st.error("Error: Username may already exist.")
    else:
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if authenticate_user(username, password):
                st.session_state.username = username
                st.success("Logged in successfully!")
                # No need for st.experimental_rerun() here
            else:
                st.error("Invalid username or password.")
else:
    # If the user is logged in, show the logging interface
    st.sidebar.header(f"Welcome, {st.session_state.username}!")

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.username = None
        st.success("Logged out successfully!")
        # No need for st.experimental_rerun() here

    # Sidebar for inputs
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
                st.session_state.username,
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
        clear_data(st.session_state.username)
        st.success("All entries cleared successfully!")

    # Display logged exercises
    st.subheader("📊 Logged Exercises")
    selected_date = st.sidebar.date_input("Filter by Date", datetime.today())
    data = load_data(st.session_state.username, selected_date.strftime("%Y-%m-%d"))  # Format date for SQL query

    # Add S.No column that resets for each date
    if not data.empty:
        data['S.No'] = data.groupby('date').cumcount() + 1  # Create S.No column
        data = data[['S.No', 'date', 'exercise', 'set1_weight', 'set1_reps', 'set2_weight', 'set2_reps', 'set3_weight', 'set3_reps']]  # Reorder columns
        st.dataframe(data, use_container_width=True)  # Display the DataFrame
    else:
        st.write("No entries found for the selected date. Please log your exercises.")

# Create the tables if they don't exist
create_tables()
