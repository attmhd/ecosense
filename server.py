from fastapi import FastAPI, Form, HTTPException
import mysql.connector
import uvicorn

# Initialize the FastAPI app
app = FastAPI()

# Database connection helper function
def get_db_connection():
    """Establish a connection to the MySQL database."""
    return mysql.connector.connect(
        host="localhost",       # Replace with your MySQL host (e.g., localhost or an IP address)
        user="root",            # Replace with your MySQL username
        password="",            # Replace with your MySQL password
        database="ecosense"     # Replace with the name of your MySQL database
    )

# Function to insert DHT11 data into the database
def insert_ldr_data_to_db(temperature: float, humidity: float):
    """Insert the DHT11 data value into the database."""
    try:
        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert data into the dht11 table using parameterized queries (%s for all types)
        cursor.execute("INSERT INTO dht11 (temperature, humidity) VALUES (%s, %s)", (temperature, humidity))
        conn.commit()  # Commit the transaction
    except mysql.connector.Error as err:
        # Raise an HTTP exception if a MySQL error occurs
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
    finally:
        # Ensure the connection is closed even if an error occurs
        cursor.close()
        conn.close()

# Endpoint to insert LDR data
@app.post("/insert_data")
async def insert_data(temperature: float = Form(...), humidity: float = Form(...)):
    """Insert LDR data into the database and return a success message."""
    try:
        insert_ldr_data_to_db(temperature, humidity)  # Insert data into the DB
        return {"message": "Data inserted successfully"}  # Return success response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting data: {e}")  # Handle errors

# Main execution (run the server)
if __name__ == "__main__":
    # Run the app on a custom host and port
    uvicorn.run(app, host="192.168.36.170", port=8000, reload=True)  # Change the host and port as needed
