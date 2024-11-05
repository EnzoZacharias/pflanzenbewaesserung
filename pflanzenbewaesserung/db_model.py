from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
 
db = SQLAlchemy()

engine = db.create_engine('sqlite:///pflanzenbewaesserung.db', echo=True)
 
class Pflanze(db.Model):
    __tablename__ = 'pflanze'

    MAC_Adresse = db.Column(db.String(48), primary_key=True)
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
    gepflanzt_am = db.Column(db.Date)
    zuletztGegossen = db.Column(db.DateTime)

    messdaten = relationship("Messdaten", back_populates="pflanze")

    @classmethod
    def add_pflanze(cls, mac_adresse, ip_adresse, name, temperatur_min, temperatur_max, sonnenintensität_min, sonnenintensität_max, sonnendauer_max, bodenfeuchtigkeit_min, bodenfeuchtigkeit_max, luftfeuchtigkeit_min, luftfeuchtigkeit_max, standort):
        try:
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
                gepflanzt_am=date.today(),
                zuletztGegossen=datetime.now().replace(microsecond=0)
            )
            db.session.add(new_pflanze)
            db.session.commit()

            # Initiale Messdaten
            Messdaten.add_messdaten(mac_adresse, datetime.now(), 0, 0, 0, 0)
            return new_pflanze
        except Exception as e:
            raise e


class Messdaten(db.Model):
    __tablename__ = 'messdaten'

    ID = db.Column(db.Integer, primary_key=True)
    Pflanzen_ID = db.Column(db.String(48), db.ForeignKey('pflanze.MAC_Adresse'))
    Zeitstempel = db.Column(db.DateTime)
    Umgebungstemperatur = db.Column(db.Float)
    Luftfeuchtigkeit = db.Column(db.Float)
    Bodenfeuchtigkeit = db.Column(db.Float)
    Lichtintensität = db.Column(db.Float)
    Wasserstand = db.Column(db.Float)

    pflanze = relationship("Pflanze", back_populates="messdaten")

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
    
def get_name_by_plant_id(plant_id):
    plant = Pflanze.query.filter_by(MAC_Adresse=plant_id).first()
    return plant.Name