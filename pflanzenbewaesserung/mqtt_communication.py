import paho.mqtt.client as paho
from paho import mqtt
import json
from datetime import datetime
from db_model import Messdaten, db

# MQTT-Broker-Informationen
MQTT_BROKER = "abf5695669a8496cbb7cb383b743fdcc.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC = "plant_watering"
MQTT_USERNAME = "EnzoZacharias"
MQTT_PASSWORD = "ahNg13Q4XeHr"

# MQTT-Client konfigurieren
mqtt_client = paho.Client()
mqtt_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)  # TLS-Verschlüsselung aktivieren
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)  # Anmeldedaten setzen

# Funktion zur Einrichtung des MQTT-Clients
def setup_mqtt(app):
    if not mqtt_client.is_connected():
        # Event-Handler setzen
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = lambda client, userdata, message: on_message(client, userdata, message, app)
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT)  # Verbindung zum Broker herstellen
        mqtt_client.loop_start()  # Hintergrundprozess starten

# Event-Handler für erfolgreiche Verbindung
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Verbindung zum MQTT-Broker hergestellt.")
        client.subscribe(MQTT_TOPIC)  # Abonnieren des angegebenen Topics
    else:
        print(f"Verbindung fehlgeschlagen mit Fehlercode {rc}")

# Event-Handler für eingehende Nachrichten
def on_message(client, userdata, message, app):
    payload = message.payload.decode()  # Nachricht dekodieren
    print("Nachricht empfangen:", payload)
    
    try:
        # JSON-Nachricht parsen
        data = json.loads(payload)
        temperature = data["Temperature"]
        humidity = data["Humidity"]
        soil_moisture = data["SoilMoisture"]
        light_intensity = data["LightIntensity"]
        wasserstand = data["WaterLevel"]
        
        # Daten in die Datenbank speichern
        with app.app_context():  # Flask-App-Kontext aktivieren
            Messdaten.add_messdaten(
                "00-1D-60-4A-8C-CB",  # Beispiel-MAC-Adresse (anpassen, falls dynamisch)
                datetime.now(), 
                temperature, 
                humidity, 
                soil_moisture, 
                light_intensity, 
                wasserstand
            )
    except json.JSONDecodeError:
        print("Fehler beim Dekodieren der JSON-Daten")