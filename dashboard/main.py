import streamlit as st
import streamlit_shadcn_ui as ui
import requests
import pandas as pd
import plotly.express as px

# Constants
API_BASE_URL = "http://127.0.0.1:8000"
ROWS_PER_PAGE = 5

# Set page configuration
st.set_page_config(layout="wide", page_title="Ecosense", page_icon="🌿")
st.title("Ecosense Dashboard")

# Utility function to fetch data from the API
def fetch_data(api_url):
    """Fetch data from the API."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None

def process_data(data):
    """Process the raw API data into a DataFrame."""
    if data and "data" in data:
        df = pd.DataFrame(data["data"])
        if {"temperature", "humidity", "timestamp"}.issubset(df.columns):
            df["Timestamp"] = pd.to_datetime(df["timestamp"])
            df = df[["Timestamp", "temperature", "humidity"]].rename(columns={"temperature": "Temperature", "humidity": "Humidity"})
            return df
    return None

def plot_interactive_chart(df):
    """Plot an interactive line chart for temperature and humidity."""
    fig = px.line(df, x='Timestamp', y=['Temperature', 'Humidity'], 
                  labels={'value': 'Measurement', 'variable': 'Parameter'},
                  title='Temperature and Humidity Over Time')
    st.plotly_chart(fig)

def display_latest_data():
    """Fetch and display the latest data."""
    latest_data = fetch_data(f"{API_BASE_URL}/latest_data")
    if latest_data:
        cols = st.columns(3)
        with cols[0]:
            ui.metric_card(title="Latest Humidity", content=f"{latest_data['humidity']}%", description="Latest humidity level", key="humidity_card")
        with cols[1]:
            ui.metric_card(title="Latest Temperature", content=f"{latest_data['temperature']}°C", description="Latest temperature level", key="temperature_card")
        with cols[2]:
            predicted_temp = fetch_data(f"{API_BASE_URL}/predict_next_hour")
            if predicted_temp:
                ui.metric_card(title="Predicted Temperature", content=f"{predicted_temp['predicted_temperature']:.2f}°C", description="Predicted temperature for the next hour", key="predicted_temp_card")
    else:
        st.error("Failed to fetch the latest data.")

def display_all_data():
    """Fetch, process, and display all data."""
    data = fetch_data(f"{API_BASE_URL}/all_data")
    df = process_data(data)
    if df is not None:
        st.subheader("All Temperature and Humidity Data")
        total_rows = len(df)
        total_pages = (total_rows + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE

        if 'page' not in st.session_state:
            st.session_state.page = 1

        df = df.sort_values(by="Timestamp", ascending=False)
        start_idx = (st.session_state.page - 1) * ROWS_PER_PAGE
        end_idx = start_idx + ROWS_PER_PAGE
        df_display = df.iloc[start_idx:end_idx].copy()
        df_display["Timestamp"] = df_display["Timestamp"].dt.strftime('%Y-%m-%d %H:%M:%S')
        ui.table(data=df_display, maxHeight=300)

        cols = st.columns([1, 2, 1])
        with cols[0]:
            if st.button("Previous"):
                if st.session_state.page > 1:
                    st.session_state.page -= 1
        with cols[2]:
            if st.button("Next"):
                if st.session_state.page < total_pages:
                    st.session_state.page += 1

        st.subheader("Interactive Chart")
        plot_interactive_chart(df)
    else:
        st.error("No data available to display.")


def main():
    display_latest_data()
    display_all_data()  

if __name__ == '__main__':
    main()