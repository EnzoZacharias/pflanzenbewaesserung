from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Mail, Message
from db_model import db, Pflanze, Messdaten, get_name_by_plant_id
from app_plant import plant, getPlants
from datetime import datetime
from mqtt_communication import setup_mqtt, mqtt_client, MQTT_TOPIC
import os
import json
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO
from sqlalchemy import event

app = Flask(__name__)
app.register_blueprint(plant)

app.config['SECRET_KEY'] = 'mysecretkey'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pflanzenbewaesserung.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'enzozachariasllm@gmail.com'
app.config['MAIL_PASSWORD'] = 'arux dbfd iqec mpbd'
app.config['MAIL_DEFAULT_SENDER'] = ('Bewässerungssystem für Pflanzen', 'enzozachariasllm@gmail.com')

mail = Mail(app)
socketio = SocketIO(app)
db.init_app(app)

email_sent_status = {}
watering_triggered_status = {}

def send_email(water_level, plant_name="Unbekannt"):
    msg = Message(
        subject="🚨 Warnung: Niedriger Wasserstand im Tank! 🚨",
        recipients=["E.Zacharias@beckhoff.com"], # Anpassen, falls man die E-Mail an eine andere Adresse senden möchte
        html=(
            f"<html><body>"
            f"<h2 style='color: red;'>🚨 Warnung: Niedriger Wasserstand im Tank! 🚨</h2>"
            f"<p>🌱 <strong>Achtung!</strong> Der Wasserstand im Tank der Pflanze <strong>'{plant_name}'</strong> "
            f"ist auf <strong>{water_level}%</strong> gesunken.</p>"
            f"<p>Bitte füllen Sie den Tank so schnell wie möglich auf, um sicherzustellen, "
            f"dass Ihre Pflanze weiterhin optimal versorgt wird.</p>"
            f"<p>Vielen Dank für Ihre Aufmerksamkeit!</p>"
            f"<p><em>Ihr Bewässerungssystem für Pflanzen 🌿</em></p>"
            f"</body></html>"
        )
    )
    try:
        mail.send(msg)
        print("E-Mail erfolgreich gesendet.")
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")

setup_mqtt(app)

# Event-Listener für die Überwachung der Datenbank
@event.listens_for(Messdaten, 'after_insert')
def after_insert(mapper, connection, target):
    plant_id = target.Pflanzen_ID
    name = get_name_by_plant_id(target.Pflanzen_ID)
    if target.Wasserstand is not None and target.Wasserstand < 10:
        if plant_id not in email_sent_status or not email_sent_status[plant_id]:
            send_email(target.Wasserstand, name)
            email_sent_status[plant_id] = True
    else:
        email_sent_status[plant_id] = False
    # Check soil moisture and trigger watering if low
    if target.Bodenfeuchtigkeit is not None and target.Bodenfeuchtigkeit < 10:
        if plant_id not in watering_triggered_status or not watering_triggered_status[plant_id]:
            # Trigger watering
            message = json.dumps({"action": "water"})
            mqtt_client.publish("manuel_watering", message)
            Pflanze.update_zuletztGegossen(plant_id)
            watering_triggered_status[plant_id] = True
            print(f"Automatic watering started for plant {name} ({plant_id}) due to low soil moisture.")
    else:
        watering_triggered_status[plant_id] = False
    socketio.emit('reload_page')

@app.route('/')
def index():
    pflanzen = getPlants()
    
    low_water_plants = [pflanze['name'] for pflanze in pflanzen if pflanze['currMeasData']['waterlevel'] < 10]
    
    low_water_warning = len(low_water_plants) > 0
    
    return render_template('overview.html', plants=pflanzen, low_water_warning=low_water_warning, low_water_plants=low_water_plants)

@app.route('/pflanze/hinzufuegen', methods=['GET', 'POST'])
def pflanze_hinzufuegen():
    if request.method == 'POST':
        mac_adresse = request.form['mac_adresse']
        ip_adresse = request.form['ip_adresse']
        name = request.form['name']
        standort = request.form['standort']
        temperatur_min = request.form['temperatur_min']
        temperatur_max = request.form['temperatur_max']
        sonnenintensität_min = request.form['sonnenintensität_min']
        sonnenintensität_max = request.form['sonnenintensität_max']
        sonnendauer_max = request.form['sonnendauer_max']
        bodenfeuchtigkeit_min = request.form['bodenfeuchtigkeit_min']
        bodenfeuchtigkeit_max = request.form['bodenfeuchtigkeit_max']
        luftfeuchtigkeit_min = request.form['luftfeuchtigkeit_min']
        luftfeuchtigkeit_max = request.form['luftfeuchtigkeit_max']
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                # Formatierte MAC-Adresse für den Bildnamen
                formatted_mac = mac_adresse.replace(":", "").lower()
                filename = secure_filename(f"{formatted_mac}.png")
                image.save(os.path.join('pflanzenbewaesserung','static', 'images', filename))

        try:
            Pflanze.add_pflanze(
                mac_adresse=mac_adresse,
                ip_adresse=ip_adresse,
                name=name,
                temperatur_min=float(temperatur_min),
                temperatur_max=float(temperatur_max),
                sonnenintensität_min=float(sonnenintensität_min),
                sonnenintensität_max=float(sonnenintensität_max),
                sonnendauer_max=float(sonnendauer_max),
                bodenfeuchtigkeit_min=float(bodenfeuchtigkeit_min),
                bodenfeuchtigkeit_max=float(bodenfeuchtigkeit_max),
                luftfeuchtigkeit_min=float(luftfeuchtigkeit_min),
                luftfeuchtigkeit_max=float(luftfeuchtigkeit_max),
                standort=standort
            )
            
            flash("Pflanze erfolgreich hinzugefügt!")
        except Exception as e:
            flash(f"Fehler beim Hinzufügen der Pflanze: {e}")
        return redirect(url_for('index'))
    return render_template('pflanze_hinzufuegen.html')

@app.route('/messdaten/hinzufuegen', methods=['GET', 'POST'])
def messdaten_hinzufuegen():
    pflanzen = Pflanze.query.all()
    
    if request.method == 'POST':
        pflanzen_id = request.form['pflanzen_id']
        zeitstempel = datetime.now()
        umgebungstemperatur = request.form['umgebungstemperatur']
        luftfeuchtigkeit = request.form['luftfeuchtigkeit']
        bodenfeuchtigkeit = request.form['bodenfeuchtigkeit']
        lichtintensität = request.form['lichtintensität']
        wasserstand = request.form['wasserstand']

        try:
            Messdaten.add_messdaten(
                pflanzen_id=pflanzen_id,
                zeitstempel=zeitstempel.replace(microsecond=0),
                umgebungstemperatur=float(umgebungstemperatur),
                luftfeuchtigkeit=float(luftfeuchtigkeit),
                bodenfeuchtigkeit=float(bodenfeuchtigkeit),
                lichtintensität=float(lichtintensität),
                wasserstand=float(wasserstand)
            )
            flash("Messdaten erfolgreich hinzugefügt!")
            return redirect(url_for('overview.html'))
        except Exception as e:
            flash(f"Fehler beim Hinzufügen der Messdaten: {e}")

    return render_template('messdaten_hinzufuegen.html', pflanzen=pflanzen)

@socketio.on('manual_water')
def handle_manual_water(data):
    message = json.dumps({"action": "water"})
    mqtt_client.publish("manuel_watering", message)
    Pflanze.update_zuletztGegossen(data['mac'])
    print(f"Manuelle Bewässerung gestartet")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    #app.run(debug=True)
    socketio.run(app, debug=True)