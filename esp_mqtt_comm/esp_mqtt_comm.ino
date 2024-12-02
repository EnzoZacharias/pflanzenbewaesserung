#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>
#include <SPI.h>
#include <DHT.h>
#include <ArduinoJson.h>

// Pin Definitions
#define DHTPIN 27             // DHT11 Data Pin
#define DHTTYPE DHT11         // DHT11 Type
#define SOIL_MOISTURE_PIN 34  // Soil moisture sensor
#define LDR_PIN 35            // Light intensity (LDR)
#define WATER_LEVEL_PIN 33    // Water level sensor
#define RELAY_PIN 13          // Relay pin for pump
#define BUTTON_PIN 4          // Button pin for manual pump activation

// RGB LED 
#define RED_PIN 21
#define GREEN_PIN 19
#define BLUE_PIN 18

// WiFi and MQTT credentials
const char* ssid = "Fresels_Guest";
const char* password = "Fresels_Guest";
const char* mqtt_server = "abf5695669a8496cbb7cb383b743fdcc.s1.eu.hivemq.cloud";
const char* mqtt_username = "EnzoZacharias";
const char* mqtt_password = "ahNg13Q4XeHr";
const int mqtt_port = 8883;

// Secure client and MQTT client
WiFiClientSecure espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;

static const char *root_ca PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw
TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
cmNoIEdyb3VwMRUwEwYDVQQDEwxJU1JHIFJvb3QgWDEwHhcNMTUwNjA0MTEwNDM4
WhcNMzUwNjA0MTEwNDM4WjBPMQswCQYDVQQGEwJVUzEpMCcGA1UEChMgSW50ZXJu
ZXQgU2VjdXJpdHkgUmVzZWFyY2ggR3JvdXAxFTATBgNVBAMTDElTUkcgUm9vdCBY
MTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAK3oJHP0FDfzm54rVygc
h77ct984kIxuPOZXoHj3dcKi/vVqbvYATyjb3miGbESTtrFj/RQSa78f0uoxmyF+
0TM8ukj13Xnfs7j/EvEhmkvBioZxaUpmZmyPfjxwv60pIgbz5MDmgK7iS4+3mX6U
A5/TR5d8mUgjU+g4rk8Kb4Mu0UlXjIB0ttov0DiNewNwIRt18jA8+o+u3dpjq+sW
T8KOEUt+zwvo/7V3LvSye0rgTBIlDHCNAymg4VMk7BPZ7hm/ELNKjD+Jo2FR3qyH
B5T0Y3HsLuJvW5iB4YlcNHlsdu87kGJ55tukmi8mxdAQ4Q7e2RCOFvu396j3x+UC
B5iPNgiV5+I3lg02dZ77DnKxHZu8A/lJBdiB3QW0KtZB6awBdpUKD9jf1b0SHzUv
KBds0pjBqAlkd25HN7rOrFleaJ1/ctaJxQZBKT5ZPt0m9STJEadao0xAH0ahmbWn
OlFuhjuefXKnEgV4We0+UXgVCwOPjdAvBbI+e0ocS3MFEvzG6uBQE3xDk3SzynTn
jh8BCNAw1FtxNrQHusEwMFxIt4I7mKZ9YIqioymCzLq9gwQbooMDQaHWBfEbwrbw
qHyGO0aoSCqI3Haadr8faqU9GY/rOPNk3sgrDQoo//fb4hVC1CLQJ13hef4Y53CI
rU7m2Ys6xt0nUW7/vGT1M0NPAgMBAAGjQjBAMA4GA1UdDwEB/wQEAwIBBjAPBgNV
HRMBAf8EBTADAQH/MB0GA1UdDgQWBBR5tFnme7bl5AFzgAiIyBpY9umbbjANBgkq
hkiG9w0BAQsFAAOCAgEAVR9YqbyyqFDQDLHYGmkgJykIrGF1XIpu+ILlaS/V9lZL
ubhzEFnTIZd+50xx+7LSYK05qAvqFyFWhfFQDlnrzuBZ6brJFe+GnY+EgPbk6ZGQ
3BebYhtF8GaV0nxvwuo77x/Py9auJ/GpsMiu/X1+mvoiBOv/2X/qkSsisRcOj/KK
NFtY2PwByVS5uCbMiogziUwthDyC3+6WVwW6LLv3xLfHTjuCvjHIInNzktHCgKQ5
ORAzI4JMPJ+GslWYHb4phowim57iaztXOoJwTdwJx4nLCgdNbOhdjsnvzqvHu7Ur
TkXWStAmzOVyyghqpZXjFaH3pO3JLF+l+/+sKAIuvtd7u+Nxe5AW0wdeRlN8NwdC
jNPElpzVmbUq4JUagEiuTDkHzsxHpFKVK7q4+63SM1N95R1NbdWhscdCb+ZAJzVc
oyi3B43njTOQ5yOf+1CceWxG1bQVs5ZufpsMljq4Ui0/1lvh+wjChP4kqKOJ2qxq
4RgqsahDYVvTH9w7jXbyLeiNdd8XM2w9U/t7y0Ff/9yi0GE44Za4rF2LN9d11TPA
mRGunUHBcnWEvgJBQl9nJEiU0Zsnvgc/ubhPgXRR4Xq37Z0j4r7g1SgEEzwxA57d
emyPxgcYxn/eR44/KJ4EBs+lVDR3veyJm+kXQ99b21/+jh5Xos1AnX5iItreGCc=
-----END CERTIFICATE-----)EOF";

// Variables
int soilMoistureValue, soilMoisturePercent, ldrValue, waterLevelValue;
float humidity, tempDHT, ldrPercent, waterLevelPercent;
volatile bool relayFlag = false;   // Flag für Relaisaktivierung
unsigned long relayActivationTime = 0;  // Zeit für Relaisaktivierung
void setRelayFlag();

// DHT Sensor Initialization
DHT dht(DHTPIN, DHTTYPE);

// MQTT callback function
void callback(char* topic, byte* payload, unsigned int length) {
  String incomingMessage = "";
  for (int i = 0; i < length; i++) incomingMessage += (char)payload[i];
  Serial.println("Message arrived [" + String(topic) + "] " + incomingMessage);

  // Check for manual watering
  if (String(topic) == "manuel_watering") {
    DynamicJsonDocument doc(256);
    DeserializationError error = deserializeJson(doc, incomingMessage);

    if (!error) {
      String action = doc["action"]; // "water"

      if (action == "water") {
        setReDlayFlag();
        Serial.println("Manual watering triggered.");
      } else {
        Serial.println("Manual watering can't be triggered.");
      }
    } else {
      Serial.println("Error parsing MQTT message.");
    }
  }
}
// MQTT reconnection function
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP8266Client-" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("connected");
      client.subscribe("manuel_watering"); // Subscribe to manual watering topic
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void readSoilMoisture() {
  soilMoistureValue = analogRead(SOIL_MOISTURE_PIN);
  soilMoisturePercent = map(soilMoistureValue, 3000, 900, 0, 100);
}

void readDHTSensor() {
  humidity = dht.readHumidity();
  tempDHT = dht.readTemperature();
}

void readLDR() {
  analogSetAttenuation(ADC_11db);  // Höherer Messbereich, verbessert Genauigkeit
  ldrValue = analogRead(LDR_PIN);
  ldrPercent = map(ldrValue, 0, 4095, 0, 100);
}

void readWaterLevel() {
  waterLevelValue = analogRead(WATER_LEVEL_PIN);
  waterLevelPercent = map(waterLevelValue, 0, 1900, 0, 100);
}
// Interrupt function to set relay flag
void IRAM_ATTR setRelayFlag() {
  relayFlag = true;
}

void setRGBColor(int r, int g, int b) {
  analogWrite(RED_PIN, r);
  analogWrite(GREEN_PIN, g);
  analogWrite(BLUE_PIN, b);
}

void updateRGBLED() {
  if (waterLevelPercent > 50) {
    setRGBColor(0, 255, 0);  // Grün für hoher Wasserstand
  } else if (waterLevelPercent > 25) {
    setRGBColor(255, 255, 0);  // Gelb für mittlerer Wasserstand
  } else {
    setRGBColor(255, 0, 0);  // Rot für niedriger Wasserstand
  }
}

void showSensorValues(bool debugMode = false){
  if(debugMode){
    // Ausgabe der Sensorwerte und Variablen
    
    Serial.println("---------- Sensor Values ----------");
    
    // Sensorwerte:
    Serial.print("Soil Moisture Value: ");
    Serial.println(soilMoistureValue);
    
    Serial.print("Soil Moisture Percentage: ");
    Serial.println(soilMoisturePercent);
    
    Serial.print("LDR Value: ");
    Serial.println(ldrValue);
    
    Serial.print("Water Level Value: ");
    Serial.println(waterLevelValue);
    
    Serial.print("Humidity: ");
    Serial.println(humidity, 2);  // 2 Dezimalstellen für die Luftfeuchtigkeit
    
    Serial.print("Temperature (DHT): ");
    Serial.println(tempDHT, 2);  // 2 Dezimalstellen für die Temperatur
    
    Serial.print("LDR Percentage: ");
    Serial.println(ldrPercent, 2);  // 2 Dezimalstellen für den LDR-Prozentwert
    
    Serial.print("Water Level Percentage: ");
    Serial.println(waterLevelPercent, 2);  // 2 Dezimalstellen für den Wasserstand-Prozentwert
    
    // Relais-Status und Zeit:
    Serial.print("Relay Flag: ");
    Serial.println(relayFlag ? "Activated" : "Deactivated");
    
    Serial.print("Relay Activation Time: ");
    Serial.println(relayActivationTime);
    
    Serial.println("------------------------------------");
  }
}


void setup() {
  Serial.begin(115200);
  Serial.print("\nVerbinde mit ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  client.setCallback(callback);

  // Initialize DHT11 and relay
  dht.begin();
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  // Analog pins setup
  pinMode(SOIL_MOISTURE_PIN, INPUT);
  pinMode(LDR_PIN, INPUT);
  pinMode(WATER_LEVEL_PIN, INPUT);
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  // Setup Button Pin and Interrupt
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), setRelayFlag, FALLING);
  
    while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  espClient.setCACert(root_ca);
  client.setServer(mqtt_server, mqtt_port);
  delay(1000);

  readSoilMoisture();
  readDHTSensor();
  readLDR();
  readWaterLevel();
  updateRGBLED();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();

  if (relayFlag) {
    digitalWrite(RELAY_PIN, HIGH);  // Relais einschalten
    if (relayActivationTime == 0) {
      relayActivationTime = millis();  // Zeit für die Relais-Aktivierung setzen
      relayFlag = false;
    }
  }

  if(relayActivationTime != 0){
    // Serial.println("Pumpe Restdauer (ms): "+ String((now - relayActivationTime)));
    if (now - relayActivationTime >= 2000) {
      digitalWrite(RELAY_PIN, LOW);  // Relais ausschalten
      delay(1000);
      relayActivationTime = 0;  // Relais-Aktivierungszeit zurücksetzen
      relayFlag = false;  // Relais-Flag zurücksetzen
    }
  }
  

  // Sensoren alle 60 Sekunden auslesen
  if (now - lastMsg > 60000) {
    lastMsg = now;

    readSoilMoisture();
    readDHTSensor();
    readLDR();
    readWaterLevel();
    updateRGBLED();
    showSensorValues();

    if(soilMoisturePercent < 35){
      relayFlag = true;
    }

    // Prepare and publish payload
    String payload = "{\"Temperature\":" + String(tempDHT) + 
                     ",\"Humidity\":" + String(humidity) + 
                     ",\"SoilMoisture\":" + String(soilMoisturePercent) + 
                     ",\"LightIntensity\":" + String(ldrPercent) + 
                     ",\"WaterLevel\":" + String(waterLevelPercent) + "}";
    publishMessage("plant_watering", payload, false);
  }
}

// Publish MQTT message
void publishMessage(const char* topic, String payload, boolean retained) {
  if (client.publish(topic, payload.c_str(), retained)) 
    Serial.println("Message published [" + String(topic) + "]: " + payload);
}