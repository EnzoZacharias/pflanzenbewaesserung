from flask import Blueprint, render_template, redirect, url_for, session, flash
from db_model import db, Pflanze, Messdaten
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

# Blueprint für Pflanzenverwaltung erstellen
plant = Blueprint(__name__, import_name="app_plant")

# Funktion, um eine Liste aller Pflanzen mit deren aktuellen Messdaten zu erstellen
def getPlants():
    plants = []
    elements = db.session.query(Pflanze).all()  # Alle Pflanzen aus der Datenbank abrufen
    for plant in elements:
        newPlant = getGeneralData(plant.MAC_Adresse)  # Allgemeine Daten der Pflanze abrufen
        newPlant["currMeasData"] = getMeasurementDataNow(plant.MAC_Adresse)  # Aktuelle Messdaten der Pflanze abrufen
        plants.append(newPlant)
    return plants

# Route für die Detailansicht einer Pflanze
@plant.route("/details/<macAdd>")
def detailPage(macAdd):
    generalData = getGeneralData(macAdd)  # Allgemeine Daten der Pflanze abrufen
    measurementDataHist = getMeasurementDataHist(macAdd)  # Historische Messdaten der Pflanze abrufen
    measurementDataNow = getMeasurementDataNow(macAdd)  # Aktuelle Messdaten der Pflanze abrufen
    url = "http://127.0.0.1:5000/details/" + macAdd  # URL für die Detailseite
    return render_template('details.html', generalData=generalData, measurementDataHist=measurementDataHist, measurementDataNow=measurementDataNow, url=url)

# Route für die Übersicht aller Pflanzen
@plant.route("/overview")
def overview():
    plants = getPlants()  # Alle Pflanzen und deren Daten abrufen
    return render_template('overview.html', plants=plants)

# Funktion, um allgemeine Daten einer Pflanze anhand der MAC-Adresse abzurufen
def getGeneralData(macAdd):
    data = db.session.query(Pflanze).filter(Pflanze.MAC_Adresse == macAdd).first()  # Pflanzendaten aus der Datenbank
    generalPlantData = {
        'name': data.Name,
        'mac': data.MAC_Adresse,
        'ip': data.IP_Adresse,
        'tem_min': data.Temperatur_min,
        'tem_max': data.Temperatur_max,
        'sunInt_min': data.Sonnenintensität_min,
        'sunInt_max': data.Sonnenintensität_max,
        'sunDur_max': data.Sonnendauer_max,
        'moisture_min': data.Bodenfeuchtigkeit_min,
        'moisture_max': data.Bodenfeuchtigkeit_max,
        'air_min': data.Luftfeuchtigkeit_min,
        'air_max': data.Luftfeuchtigkeit_max,
        'planted': data.gepflanzt_am,
        'pour': data.zuletztGegossen,
        'place': data.Standort
    }
    return generalPlantData

# Funktion, um historische Messdaten der letzten 72 Stunden für eine Pflanze abzurufen
def getMeasurementDataHist(macAdd):
    now = datetime.now()
    timewindow = now - timedelta(hours=72)  # Zeitfenster der letzten 72 Stunden berechnen
    data = []
    measurementData = db.session.query(Messdaten).join(Pflanze).filter(
        Messdaten.Pflanzen_ID == macAdd,
        Messdaten.Zeitstempel <= now,
        Messdaten.Zeitstempel >= timewindow
    ).all()
    for element in measurementData:
        newData = {
            'zeitstempel': element.Zeitstempel,
            'Temp': element.Umgebungstemperatur,
            'air': element.Luftfeuchtigkeit,
            'ground': element.Bodenfeuchtigkeit,
            'sun': element.Lichtintensität
        }
        data.append(newData)
    return data

# Funktion, um die aktuellsten Messdaten einer Pflanze abzurufen
def getMeasurementDataNow(macAdd):
    now = datetime.now()
    element = db.session.query(Messdaten).join(Pflanze).filter(
        Messdaten.Pflanzen_ID == macAdd,
        Messdaten.Zeitstempel <= now
    ).order_by(Messdaten.Zeitstempel.desc()).first()  # Neueste Messdaten abrufen

    if element is None:
        # Falls keine Daten vorhanden sind, Standardwerte zurückgeben
        data = {
            'zeitstempel': now,
            'Temp': 0,
            'air': 0,
            'ground': 0,
            'sun': 0,
            'waterlevel': 0
        }
    else:
        # Vorhandene Daten in ein Dictionary umwandeln
        data = {
            'zeitstempel': element.Zeitstempel,
            'Temp': element.Umgebungstemperatur,
            'air': element.Luftfeuchtigkeit,
            'ground': element.Bodenfeuchtigkeit,
            'sun': element.Lichtintensität,
            'waterlevel': element.Wasserstand
        }
    return data