#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>
#include <SPI.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <WiFiUdp.h>
#include <NTPClient.h>

// Pin Definitionen
#define DHTPIN 27             // DHT11 Daten-Pin
#define DHTTYPE DHT11         // DHT11 Sensortyp
#define SOIL_MOISTURE_PIN 34  // Bodenfeuchtigkeitssensor
#define LDR_PIN 35            // Lichtintensität (LDR)
#define WATER_LEVEL_PIN 33    // Wasserstandssensor
#define RELAY_PIN 13          // Relais-Pin für die Pumpe
#define BUTTON_PIN 4          // Taster-Pin für manuelle Pumpenaktivierung

// RGB LED
#define RED_PIN 21
#define GREEN_PIN 19
#define BLUE_PIN 18

// WLAN und MQTT Anmeldedaten
const char* ssid = "OnePlus Nord 2T";
const char* password = "123vier5sechs7";
const char* mqtt_server = "abf5695669a8496cbb7cb383b743fdcc.s1.eu.hivemq.cloud";
const char* mqtt_username = "EnzoZacharias";
const char* mqtt_password = "ahNg13Q4XeHr";
const int mqtt_port = 8883;

// Sicherer Client und MQTT Client
WiFiClientSecure espClient;
PubSubClient client(espClient);

// NTP-Client-Setup
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 3600, 60000);  // UTC+1 Zeitzone

// Zertifikat
static const char* root_ca PROGMEM = R"EOF(
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

// Variablen
int soilMoistureValue, soilMoisturePercent, ldrValue, waterLevelValue;
float humidity, tempDHT, ldrPercent, waterLevelPercent;
volatile bool relayFlag = false;  // Flag für Relaisaktivierung
unsigned long relayActivationTime = 0;
bool isNightMode = false;  // Nachtmodus überprüfen
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 500; // 500 ms Tasterprellen

// Intervalle
const unsigned long dayInterval = 60000;  // 60 Sekunden am Tag

// DHT Sensor Initialisierung
DHT dht(DHTPIN, DHTTYPE);

// Funktionsprototypen
void readSensors();
void publishSensorData();
void goToDeepSleep(unsigned long sleepDuration);
void reconnectMQTT();
void updateRGBLED();
void setRGBColor(int r, int g, int b);
void IRAM_ATTR setRelayFlag() {
  unsigned long currentTime = millis();
  if (currentTime - lastDebounceTime > debounceDelay) {
    relayFlag = true;
    Serial.println("Pumpflag gesetzt!");
    setRGBColor(0, 0, 255);
    lastDebounceTime = currentTime;
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String incomingMessage = "";
  for (int i = 0; i < length; i++) incomingMessage += (char)payload[i];
  if (String(topic) == "manuel_watering") {
    DynamicJsonDocument doc(256);
    if (deserializeJson(doc, incomingMessage) == DeserializationError::Ok) {
      if (doc["action"] == "water") setRelayFlag();
    }
  }
}

void setup() {
  Serial.begin(115200);

  // Verbindung zu WLAN herstellen
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("WLAN verbunden");

  // NTP-Client starten
  timeClient.begin();

  // MQTT-Client einrichten
  espClient.setCACert(root_ca);
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  reconnectMQTT();

  // Sensoren und Pins initialisieren
  dht.begin();
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(SOIL_MOISTURE_PIN, INPUT);
  pinMode(LDR_PIN, INPUT);
  pinMode(WATER_LEVEL_PIN, INPUT);
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLDOWN);
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), setRelayFlag, FALLING);

  readSensors();   // Sensordaten auslesen
  updateRGBLED();  // LED aktualisieren
}

void loop() {
  if (!client.connected()) reconnectMQTT();  // MQTT-Verbindung sicherstellen
  client.loop();

  // NTP-Zeitaktualisierung
  timeClient.update();
  if (timeClient.getEpochTime() == 0) {
    Serial.println("Fehler beim Abrufen der NTP-Zeit");
  } else {
    int hour = timeClient.getHours();
    int minute = timeClient.getMinutes();
    int second = timeClient.getSeconds();

    // Überprüfen, ob es Nacht ist (zwischen 20:00 und 07:00 Uhr)
    isNightMode = (hour >= 20 || hour < 7);

    if (isNightMode) {
      // Im Nachtmodus:
      // LED deaktivieren
      digitalWrite(RED_PIN, LOW);
      digitalWrite(GREEN_PIN, LOW);
      digitalWrite(BLUE_PIN, LOW);

      // Nicht-blockierender Puffer nach Deep Sleep
      static unsigned long wakeTime = 0;
      if (wakeTime == 0) wakeTime = millis();  // Aufwachzeitpunkt speichern
      if (millis() - wakeTime < 20000) {       // 20 Sekunden Puffer
        Serial.println("Warten auf Verbindungen...");
        return;  // Warten, bis 20 Sekunden vorbei sind
      }

      // Sensordaten auslesen und veröffentlichen
      readSensors();
      publishSensorData();

      // Deep Sleep bis zur nächsten vollen oder halben Stunde berechnen
      int sleepMinutes = (minute < 30) ? (30 - minute) : (60 - minute);
      unsigned long sleepDuration = (sleepMinutes * 60 - second) * 1000000; // Zeit bis zur nächsten Markierung in Mikrosekunden
      goToDeepSleep(sleepDuration);
    } else {
      // Im Tagmodus:
      static int lastMinute = -1;  

      if (second == 0 && minute != lastMinute) {  // Neue Minute erreicht
        lastMinute = minute;  

        // Überprüfung des Relais-Flags, um das Relais zu aktivieren 
        if (relayFlag) {
          digitalWrite(RELAY_PIN, HIGH);  // Relais einschalten <= Pumpe aktivieren
          if (relayActivationTime == 0) {
            relayActivationTime = millis();  // Zeit für die Relais-Aktivierung setzen
            relayFlag = false;
          }
        }

        readSensors();        // Sensordaten auslesen
        updateRGBLED();       // LED aktualisieren
        publishSensorData();  // Sensordaten veröffentlichen
      }

      // Pumpe nach 2 Sekunden Bewässerung wieder deaktivieren
      if (relayActivationTime != 0) {
        if (millis() - relayActivationTime >= 2000) {
          digitalWrite(RELAY_PIN, LOW);  // Relais ausschalten
          relayActivationTime = 0;      // Relais-Aktivierungszeit zurücksetzen
          relayFlag = false;
        }
      }
    }
  }
}

// Funktion zum Auslesen der Sensoren
void readSensors() {
  soilMoistureValue = analogRead(SOIL_MOISTURE_PIN);
  soilMoisturePercent = map(soilMoistureValue, 3000, 500, 0, 100);
  humidity = dht.readHumidity();
  tempDHT = dht.readTemperature();
  ldrValue = analogRead(LDR_PIN);
  ldrPercent = map(ldrValue, 0, 4095, 0, 100);
  waterLevelValue = analogRead(WATER_LEVEL_PIN);
  waterLevelPercent = map(waterLevelValue, 0, 1900, 0, 100);
}

// Funktion zur Aktualisierung der RGB-LED
void updateRGBLED() {
  if (waterLevelPercent < 25 && waterLevelPercent > 10) {
    setRGBColor(255, 255, 0);  // Gelb für niedrigen Wasserstand
  } else if (waterLevelPercent <= 10) {
    setRGBColor(255, 0, 0);  // Rot für kritischen Wasserstand
  } else {
    setRGBColor(0, 0, 0);  // LED ausschalten
  }
}

// Funktion zum Setzen der RGB-Farbe
void setRGBColor(int r, int g, int b) {
  analogWrite(RED_PIN, r);
  analogWrite(GREEN_PIN, g);
  analogWrite(BLUE_PIN, b);
}

// Funktion zum Veröffentlichen der Sensordaten über MQTT
void publishSensorData() {
  // Zeit aktualisieren
  timeClient.update();
  String currentTime = String(timeClient.getHours()) + ":" + String(timeClient.getMinutes()) + ":" + String(timeClient.getSeconds());

  // Sensordaten in Payload formatieren
  String payload = "{\"Temperature\":" + String(tempDHT) + 
                    ",\"Humidity\":" + String(humidity) + 
                    ",\"SoilMoisture\":" + String(soilMoisturePercent) +    
                    ",\"LightIntensity\":" + String(ldrPercent) + 
                    ",\"WaterLevel\":" + String(waterLevelPercent) + "}";

  // Sensordaten über MQTT veröffentlichen
  client.publish("plant_watering", payload.c_str(), false);

  // Ausgabe der Sensordaten und der aktuellen Zeit auf der seriellen Konsole
  Serial.print("Time: ");
  Serial.println(currentTime);
  Serial.println("Sensor Data: ");
  Serial.println(payload);
}

// Funktion, um in den Deep-Sleep-Modus zu wechseln
void goToDeepSleep(unsigned long sleepDuration) {
  esp_sleep_enable_timer_wakeup(sleepDuration);
  esp_deep_sleep_start();
}

// Funktion zum Wiederverbinden mit MQTT
void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Verbindung zu MQTT wird hergestellt...");
    String clientId = "ESP8266Client-" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("verbunden");
      client.subscribe("manuel_watering");
    } else {
      Serial.print("fehlgeschlagen, rc=");
      Serial.println(client.state());
      delay(5000);
    }
  }
}
