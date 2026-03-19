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
        
    if t <= 5:
        return "MEGA FROID"
    elif t <= 15:
        return "FROID"
    elif t <= 20:
        return "FRISQUET"
    elif t <= 25:
        return "NICKEL"
    elif t <= 28:
        return "CHAUD"
    elif t <= 32:
        return "CHAUD ++"
    elif t <= 35:
        return "TROP CHAUD LA"
    elif t <= 37:
        return "LE SERVEUR VA PEUT ETRE S ETEINDRE"
    elif t <= 40:
        return "FEU FEU FEU"
    elif t <= 43:
        return "EXTINCTEUR IMMEDIAT !!!"
    else:
        return "MORT."

def load():
    now = datetime.now().strftime(("%d/%m/%Y %H:%M"))
    temperature = None
    random_number = random.randint(1, 10000)
    # Requête Flux pour récupérer la dernière valeur de température sur la dernière heure
    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "temperature")
        |> last()
    '''
    
    try:
        # Connexion à InfluxDB et exécution de la requête
        client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        tables = client.query_api().query(query, org=INFLUX_ORG)
        
        # Extraction de la valeur si la requête retourne des résultats
        if tables and tables[0].records:
            temperature = tables[0].records[0].get_value()
            
    except Exception as e:
        print(f"Erreur lors de la connexion à InfluxDB : {e}")
        temperature = "N/A" # Valeur de secours en cas d'erreur

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
    app.run(debug=True)
