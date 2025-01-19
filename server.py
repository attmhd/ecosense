from fastapi import FastAPI, Form, HTTPException
import aiomysql
import uvicorn
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import numpy as np

# Initialize the FastAPI app
app = FastAPI()

# Load the trained model and scaler
trained_model = load_model('./model/dnn.h5')
scaler = StandardScaler()

# Load environment variables from .env file
load_dotenv()

# Database connection helper function
async def get_db_connection():
    """Establish a connection to the MySQL database."""
    return await aiomysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        db=os.getenv("DB_NAME", "ecosense")
    )

# Function to insert DHT11 data into the database
async def insert_ldr_data_to_db(temperature: float, humidity: float):
    """Insert the DHT11 data value into the database."""
    try:
        conn = await get_db_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT INTO dht11 (temperature, humidity) VALUES (%s, %s)", (temperature, humidity))
            await conn.commit()
    except aiomysql.MySQLError as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
    finally:
        conn.close()

# Function to get the latest temperature data from the database
async def get_latest_temperature_data():
    """Fetch the latest temperature data from the database."""
    try:
        conn = await get_db_connection()
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT temperature, timestamp FROM dht11 ORDER BY timestamp DESC LIMIT 1")
            result = await cursor.fetchone()
        conn.close()
        return result
    except aiomysql.MySQLError as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")

# Function to make a prediction for the next hour
def make_prediction(temperature: float, timestamp: str):
    """Make a prediction for the next hour based on the latest data."""

    timestamp_dt = timestamp
    new_data = pd.DataFrame([{
        'timestamp': timestamp_dt.timestamp(),
        'temperature': temperature
    }])
    X_new = new_data[['timestamp', 'temperature']].values
    scaler.fit(X_new)
    X_new_scaled = scaler.transform(X_new)
    predicted_temp = trained_model.predict(X_new_scaled)
    predicted_temp = np.round(predicted_temp, 2)
    new_timestamp = timestamp_dt + timedelta(hours=1)
    return {
        "predicted_temperature": float(predicted_temp[0]),
        "timestamp": new_timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }

async def get_latest_data():
    """Fetch the latest temperature and humidity data from the database."""
    try:
        conn = await get_db_connection()
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT temperature, humidity, timestamp FROM dht11 ORDER BY timestamp DESC LIMIT 1")
            result = await cursor.fetchone()
        conn.close()
        return result
    except aiomysql.MySQLError as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")

# Endpoint to get latest temperature & humidity data
@app.get("/latest_data")
async def fetch_latest_data():
    """Fetch the latest temperature and humidity data from the database."""
    latest_data = await get_latest_data()
    if not latest_data:
        raise HTTPException(status_code=404, detail="No temperature data found in the database.")
    return {"status": "success", **latest_data}

# Endpoint to insert LDR data
@app.post("/insert_data")
async def insert_data(temperature: float = Form(...), humidity: float = Form(...)):
    """Insert LDR data into the database and return a success message."""
    try:
        await insert_ldr_data_to_db(temperature, humidity)
        return {"message": "Data inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting data: {e}")

# Endpoint to run prediction for the next hour
@app.get("/predict_next_hour")
async def predict_next_hour():
    """Predict the temperature for the next hour based on the latest data."""
    latest_data = await get_latest_temperature_data()
    if not latest_data:
        raise HTTPException(status_code=404, detail="No temperature data found in the database.")
    temperature = latest_data['temperature']
    timestamp = latest_data['timestamp']
    prediction = make_prediction(temperature, timestamp)
    return {"status": "success", **prediction}

# Main execution (run the server)
if __name__ == "__main__":
    uvicorn.run(app, host="192.168.36.170", port=8000, reload=True)
