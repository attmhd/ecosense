#include <DHT.h>

// Define the pin used for the DHT11 sensor
#define DHTPIN 2 // Digital pin connected to the DHT11

// Select the sensor type: DHT11
#define DHTTYPE DHT11

// Initialize the DHT object
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Start the DHT sensor
  dht.begin();
}

void loop() {
  // Wait a few seconds between readings
  delay(2000);

  // Read temperature and humidity
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Check if the readings failed
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT11 sensor!");
    return;
  }

  // Send temperature as text
  Serial.print("Temperature: ");
  Serial.print(temperature, 2);  // Print with 2 decimal places
  Serial.print(" °C, ");
  
  // Convert temperature to byte array and send using Serial.write()
  byte tempByte[4];
  memcpy(tempByte, &temperature, sizeof(temperature));
  for (int i = 0; i < sizeof(temperature); i++) {
    Serial.write(tempByte[i]);
  }

  // Send humidity as text
  Serial.print("Humidity: ");
  Serial.print(humidity, 2);  // Print with 2 decimal places
  Serial.println(" %");

  // Convert humidity to byte array and send using Serial.write()
  byte humidityByte[4];
  memcpy(humidityByte, &humidity, sizeof(humidity));
  for (int i = 0; i < sizeof(humidity); i++) {
    Serial.write(humidityByte[i]);
  }
}
