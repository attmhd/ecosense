#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>

#define REDPIN D5
#define YELLOWPIN D6
#define GREENPIN D7

// Replace with your WiFi SSID and Password
const char* ssid = "rosify";
const char* password = "12345678";

// Server URL (the IP address of the Python server)
const String serverName = "http://192.168.36.170:8000/insert_data";

// Create a WiFiClient object
WiFiClient client;

// DHT Sensor setup
#define DHTPIN D2          // Pin where the DHT11 data pin is connected
#define DHTTYPE DHT11      // Defining the sensor type as DHT11
DHT dht(DHTPIN, DHTTYPE);  // Initialize the DHT sensor

// Function to connect to WiFi
void connectToWiFi() {
  WiFi.begin(ssid, password);

  // Wait until connected to WiFi
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");
}

// Function to read temperature and humidity from the DHT11 sensor
void readDHT11Sensor(float &temperature, float &humidity) {
  humidity = dht.readHumidity();
  temperature = dht.readTemperature();  // Default is Celsius

  // Check if the readings failed and handle it
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
}

// Function to send data to the server
void sendDataToServer(float temperature, float humidity) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(client, serverName); // Initialize the connection to the server
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    // Prepare the POST data
    String postData = "temperature=" + String(temperature, 2) + "&humidity=" + String(humidity, 2);  // Send data with 2 decimal places

    // Send the POST request
    int httpResponseCode = http.POST(postData);

    // Check the server response
    if (httpResponseCode > 0) {
      Serial.println("Data sent successfully, HTTP Response Code: " + String(httpResponseCode));
    } else {
      Serial.println("Error sending data, HTTP Response Code: " + String(httpResponseCode));
    }

    http.end(); // Close the HTTP connection
  } else {
    Serial.println("Error in WiFi connection");
  }
}

void setup() {
  Serial.begin(9600);
  
  // Connect to WiFi
  connectToWiFi();

  // LED
  pinMode(REDPIN, OUTPUT);
  pinMode(YELLOWPIN, OUTPUT);
  pinMode(GREENPIN, OUTPUT);

  // Initialize the DHT sensor
  dht.begin();
}

void loop() {
  // Read temperature and humidity from the DHT11 sensor
  float temperature = 0;
  float humidity = 0;
  readDHT11Sensor(temperature, humidity);

  // Output the temperature and humidity values
  Serial.print("Temperature: ");
  Serial.print(temperature, 2);  // Print temperature with 2 decimal places
  Serial.print(" °C, Humidity: ");
  Serial.print(humidity, 2);  // Print humidity with 2 decimal places
  Serial.println(" %");

  if (temperature > 50) {
    digitalWrite(REDPIN, HIGH);
    digitalWrite(YELLOWPIN, LOW);
    digitalWrite(GREENPIN, LOW);
  } else if (temperature > 30 && temperature < 50) {
    digitalWrite(YELLOWPIN, HIGH);
    digitalWrite(REDPIN, LOW);
    digitalWrite(GREENPIN, LOW);
  } else if (temperature < 30) {
    digitalWrite(GREENPIN, HIGH);
    digitalWrite(YELLOWPIN, LOW);
    digitalWrite(REDPIN, LOW);
  } else {
    digitalWrite(GREENPIN, LOW);
    digitalWrite(YELLOWPIN, LOW);
    digitalWrite(REDPIN, LOW);
  }

  // Send data to the server
  sendDataToServer(temperature, humidity);

  // Wait for 5 seconds before sending data again
  delay(5000);
  digitalWrite(REDPIN, LOW);
}
