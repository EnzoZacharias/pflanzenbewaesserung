from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

# SQLAlchemy-Datenbankinitialisierung
db = SQLAlchemy()

# Datenbank-Engine (optional, falls separat benötigt)
engine = db.create_engine('sqlite:///pflanzenbewaesserung.db', echo=True)

# Datenbankmodell für die Pflanzen
class Pflanze(db.Model):
    __tablename__ = 'pflanze'

    # Definition der Spalten für die Tabelle 'pflanze'
    MAC_Adresse = db.Column(db.String(48), primary_key=True)  # Eindeutige MAC-Adresse
    IP_Adresse = db.Column(db.String(32))
    Name = db.Column(db.String(128))
    Temperatur_min = db.Column(db.Float)
    Temperatur_max = db.Column(db.Float)
    Sonnenintensität_min = db.Column(db.Float)
    Sonnenintensität_max = db.Column(db.Float)
    Sonnendauer_max = db.Column(db.Float)
    Bodenfeuchtigkeit_min = db.Column(db.Float)
    Bodenfeuchtigkeit_max = db.Column(db.Float)
    Luftfeuchtigkeit_min = db.Column(db.Float)
    Luftfeuchtigkeit_max = db.Column(db.Float)
    Standort = db.Column(db.String(128))
    gepflanzt_am = db.Column(db.Date)  # Pflanzdatum
    zuletztGegossen = db.Column(db.DateTime)  # Zeitpunkt der letzten Bewässerung

    # Beziehung zu Messdaten
    messdaten = relationship("Messdaten", back_populates="pflanze")

    # Methode zum Hinzufügen einer neuen Pflanze
    @classmethod
    def add_pflanze(cls, mac_adresse, ip_adresse, name, temperatur_min, temperatur_max, sonnenintensität_min, sonnenintensität_max, sonnendauer_max, bodenfeuchtigkeit_min, bodenfeuchtigkeit_max, luftfeuchtigkeit_min, luftfeuchtigkeit_max, standort):
        try:
            # Pflanze erstellen
            new_pflanze = cls(
                MAC_Adresse=mac_adresse,
                IP_Adresse=ip_adresse,
                Name=name,
                Temperatur_min=temperatur_min,
                Temperatur_max=temperatur_max,
                Sonnenintensität_min=sonnenintensität_min,
                Sonnenintensität_max=sonnenintensität_max,
                Sonnendauer_max=sonnendauer_max,
                Bodenfeuchtigkeit_min=bodenfeuchtigkeit_min,
                Bodenfeuchtigkeit_max=bodenfeuchtigkeit_max,
                Luftfeuchtigkeit_min=luftfeuchtigkeit_min,
                Luftfeuchtigkeit_max=luftfeuchtigkeit_max,
                Standort=standort,
                gepflanzt_am=date.today(),  # Heutiges Datum
                zuletztGegossen=datetime.now().replace(microsecond=0)  # Aktuelle Zeit
            )
            db.session.add(new_pflanze)
            db.session.commit()

            # Initiale Messdaten hinzufügen
            Messdaten.add_messdaten(mac_adresse, datetime.now(), 0, 0, 0, 0, 0)
            return new_pflanze
        except Exception as e:
            raise e

    # Methode zum Aktualisieren des Zeitpunkts der letzten Bewässerung
    @classmethod
    def update_zuletztGegossen(cls, mac_adresse):
        pflanze = cls.query.filter_by(MAC_Adresse=mac_adresse).first()
        pflanze.zuletztGegossen = datetime.now().replace(microsecond=0)
        db.session.commit()
        return pflanze

# Datenbankmodell für Messdaten
class Messdaten(db.Model):
    __tablename__ = 'messdaten'

    # Definition der Spalten für die Tabelle 'messdaten'
    ID = db.Column(db.Integer, primary_key=True)  # Automatische ID
    Pflanzen_ID = db.Column(db.String(48), db.ForeignKey('pflanze.MAC_Adresse'))  # Fremdschlüssel
    Zeitstempel = db.Column(db.DateTime)  # Zeitpunkt der Messung
    Umgebungstemperatur = db.Column(db.Float)
    Luftfeuchtigkeit = db.Column(db.Float)
    Bodenfeuchtigkeit = db.Column(db.Float)
    Lichtintensität = db.Column(db.Float)
    Wasserstand = db.Column(db.Float)  # Wasserstand im Tank

    # Beziehung zur Pflanze
    pflanze = relationship("Pflanze", back_populates="messdaten")

    # Methode zum Hinzufügen neuer Messdaten
    @classmethod
    def add_messdaten(cls, pflanzen_id, zeitstempel, umgebungstemperatur, luftfeuchtigkeit, bodenfeuchtigkeit, lichtintensität, wasserstand):
        new_messdaten = cls(
            Pflanzen_ID=pflanzen_id,
            Zeitstempel=zeitstempel,
            Umgebungstemperatur=umgebungstemperatur,
            Luftfeuchtigkeit=luftfeuchtigkeit,
            Bodenfeuchtigkeit=bodenfeuchtigkeit,
            Lichtintensität=lichtintensität,
            Wasserstand=wasserstand
        )
        print("Neue Messdaten: ", new_messdaten)
        db.session.add(new_messdaten)
        db.session.commit()
        return new_messdaten

# Hilfsfunktion, um den Namen einer Pflanze anhand ihrer MAC-Adresse zu erhalten
def get_name_by_plant_id(plant_id):
    plant = Pflanze.query.filter_by(MAC_Adresse=plant_id).first()
    return plant.Name