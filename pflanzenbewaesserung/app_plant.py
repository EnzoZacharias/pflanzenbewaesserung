from flask import Blueprint, render_template, redirect, url_for, session, flash
from db_model import db, Pflanze, Messdaten
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

plant = Blueprint(__name__, import_name="app_plant")

def getPlants():
    plants = []
    elements = db.session.query(Pflanze).all()
    for plant in elements:
        newPlant = getGeneralData(plant.MAC_Adresse)
        newPlant["currMeasData"] = getMeasurementDataNow(plant.MAC_Adresse)
        plants.append(newPlant)
    return plants

@plant.route("/details/<macAdd>")
def detailPage(macAdd):
    generalData = getGeneralData(macAdd)
    measurementDataHist = getMeasurementDataHist(macAdd)
    measurementDataNow = getMeasurementDataNow(macAdd)
    url = "http://127.0.0.1:5000/details/" + macAdd
    return render_template('details.html', generalData=generalData, measurementDataHist=measurementDataHist, measurementDataNow=measurementDataNow, url=url)

@plant.route("/overview")
def overview():
    plants = getPlants()
    return render_template('overview.html', plants=plants)

def getGeneralData(macAdd):
    data = db.session.query(Pflanze).filter(Pflanze.MAC_Adresse == macAdd).first()
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

def getMeasurementDataHist(macAdd):
    now = datetime.now()
    two_weeks_ago = now - timedelta(hours=72)
    data = []
    measurementData = db.session.query(Messdaten).join(Pflanze).filter(
        Messdaten.Pflanzen_ID == macAdd,
        Messdaten.Zeitstempel <= now,
        Messdaten.Zeitstempel >= two_weeks_ago
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

def getMeasurementDataNow(macAdd):
    now = datetime.now()
    element = db.session.query(Messdaten).join(Pflanze).filter(
        Messdaten.Pflanzen_ID == macAdd,
        Messdaten.Zeitstempel <= now
    ).order_by(Messdaten.Zeitstempel.desc()).first()

    if element is None:
        data = {
        'zeitstempel': now,
        'Temp': 0,
        'air': 0,
        'ground': 0,
        'sun': 0,
        'waterlevel': 0
    }
    else:
        data = {
        'zeitstempel': element.Zeitstempel,
        'Temp': element.Umgebungstemperatur,
        'air': element.Luftfeuchtigkeit,
        'ground': element.Bodenfeuchtigkeit,
        'sun': element.Lichtintensität,
        'waterlevel': element.Wasserstand
    }
    return data