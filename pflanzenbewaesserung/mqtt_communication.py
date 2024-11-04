import paho.mqtt.client as paho
from paho import mqtt
import json
from datetime import datetime
from db_model import Messdaten, db

MQTT_BROKER = "abf5695669a8496cbb7cb383b743fdcc.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC = "plant_watering"
MQTT_USERNAME = "EnzoZacharias"
MQTT_PASSWORD = "ahNg13Q4XeHr"

mqtt_client = paho.Client()
mqtt_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

def setup_mqtt(app):
    if not mqtt_client.is_connected():
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = lambda client, userdata, message: on_message(client, userdata, message, app)
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        mqtt_client.loop_start()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Verbindung zum MQTT-Broker hergestellt.")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Verbindung fehlgeschlagen mit Fehlercode {rc}")

def on_message(client, userdata, message, app):
    payload = message.payload.decode()
    print("Nachricht empfangen:", payload)
    
    try:
        data = json.loads(payload)
        temperature = data["Temperature"]
        humidity = data["Humidity"]
        soil_moisture = data["SoilMoisture"]
        light_intensity = data["LightIntensity"]
        wasserstand = data["WaterLevel"]
        
        with app.app_context():
            Messdaten.add_messdaten("00-1D-60-4A-8C-CB", datetime.now(), temperature, humidity, soil_moisture, light_intensity, wasserstand)
        
    except json.JSONDecodeError:
        print("Fehler beim Dekodieren der JSON-Daten")