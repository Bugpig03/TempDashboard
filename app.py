from flask import Flask, render_template
from datetime import datetime
from random import randint
import random
import os
from influxdb_client import InfluxDBClient

app = Flask(__name__)

# Configuration InfluxDB (à adapter avec vos propres valeurs)
INFLUX_URL = os.environ.get("INFLUX_URL")
INFLUX_TOKEN = os.environ.get("INFLUX_TOKEN")
INFLUX_ORG = os.environ.get("INFLUX_ORG")
INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET")

def get_temperature_state(temp):
    # Sécurité au cas où la base de données est injoignable
    if temp is None or temp == "N/A":
        return "INCONNU"
        
    try:
        t = float(temp)
    except (ValueError, TypeError):
        return "INCONNU"
        
    if t <= 30:
        return "MEGA FROID"
    elif t <= 35:
        return "FROID"
    elif t <= 40:
        return "FRISQUET"
    elif t <= 50:
        return "NICKEL"
    elif t <= 60:
        return "CHAUD"
    elif t <= 65:
        return "CHAUD ++"
    elif t <= 70:
        return "TROP CHAUD LA"
    elif t <= 73:
        return "LE SERVEUR VA PEUT ETRE S ETEINDRE"
    elif t <= 75:
        return "FEU FEU FEU"
    elif t <= 84:
        return "EXTINCTEUR IMMEDIAT !!!"
    else:
        return "MORT."

def load():
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    temperature = "N/A" # Par défaut
    random_number = random.randint(1, 10000)

    # CORRECTION : On définit une vraie plage de temps (-1h)
    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
        |> range(start: -1h)
        |> filter(fn: (r) => r["_measurement"] == "temp")
        |> filter(fn: (r) => r["_field"] == "temp")
        |> filter(fn: (r) => r["sensor"] == "cpu_thermal")
        |> last()
    '''
    
    try:
        # On utilise une seule instance de client si possible, ou on la ferme bien
        with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
            tables = client.query_api().query(query, org=INFLUX_ORG)
            
            if tables and len(tables) > 0 and len(tables[0].records) > 0:
                val = tables[0].records[0].get_value()
                # On arrondit pour que ce soit joli sur le dashboard
                temperature = round(float(val), 1)
            else:
                temperature = "N/A" # Pas de données sur la dernière heure

    except Exception as e:
        print(f"Erreur InfluxDB : {e}")
        temperature = "Erreur"

    # On calcule l'état (OK, CHAUD, etc.)
    state = get_temperature_state(temperature)

    return now, random_number, temperature, state


@app.route('/')
def home():

    # Lister les fichiers dans static/sound
    sound_folder = os.path.join('static', 'sound')
    liste_sons = [f for f in os.listdir(sound_folder) if os.path.isfile(os.path.join(sound_folder, f))]

    now, random_number, temperature, state = load()
    # On fait appel à notre nouvelle fonction
    return render_template('index.html', now=now, random_number=random_number, temperature=temperature, state=state, sounds=liste_sons)

if __name__ == '__main__':
    # debug=True permet de voir les erreurs et de redémarrer auto lors d'un changement
    app.run(debug=False, host='0.0.0.0', port=5000)
